#!/usr/bin/env python3
"""Read and send Discord messages through a dedicated bot account."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://discord.com/api/v10"
USER_AGENT = "krimskrams-use-discord-skill/1.0"


def snowflake(value: str | None, label: str) -> str:
    if not value or not value.isascii() or not value.isdigit():
        raise ValueError(f"{label} must be a Discord ID containing only digits")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use the Discord REST API through a dedicated bot account."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("identity", help="Show the authenticated bot identity.")
    subparsers.add_parser("channels", help="List channels visible in the configured server.")

    read_parser = subparsers.add_parser("read", help="Read recent channel messages.")
    read_parser.add_argument("--channel-id", help="Override DISCORD_CHANNEL_ID.")
    read_parser.add_argument("--limit", type=int, default=25, help="Message count (1-100).")
    position = read_parser.add_mutually_exclusive_group()
    position.add_argument("--before", help="Read messages before this message ID.")
    position.add_argument("--after", help="Read messages after this message ID.")
    position.add_argument("--around", help="Read messages around this message ID.")
    read_parser.add_argument(
        "--management-only",
        action="store_true",
        help="Return only configured management users or role members.",
    )

    message_parser = subparsers.add_parser("message", help="Retrieve one message.")
    message_parser.add_argument("message_id")
    message_parser.add_argument("--channel-id", help="Override DISCORD_CHANNEL_ID.")

    send_parser = subparsers.add_parser("send", help="Send a new message or reply.")
    send_parser.add_argument("--channel-id", help="Override DISCORD_CHANNEL_ID.")
    content = send_parser.add_mutually_exclusive_group(required=True)
    content.add_argument("--content", help="Message text.")
    content.add_argument(
        "--content-file",
        help="UTF-8 text file, or '-' to read message text from standard input.",
    )
    send_parser.add_argument(
        "--mention-management",
        action="store_true",
        help="Prefix and permit a mention of DISCORD_MANAGEMENT_ROLE_ID.",
    )
    send_parser.add_argument("--reply-to", help="Message ID to reply to.")
    return parser.parse_args()


def require_token() -> str:
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("Missing required environment variable: DISCORD_BOT_TOKEN")
    return token


def configured_id(name: str, override: str | None = None) -> str:
    return snowflake(override or os.environ.get(name), name)


def management_user_ids() -> set[str]:
    raw = os.environ.get("DISCORD_MANAGEMENT_USER_IDS", "")
    values = {value.strip() for value in raw.split(",") if value.strip()}
    for value in values:
        snowflake(value, "DISCORD_MANAGEMENT_USER_IDS entry")
    return values


def api_json(
    path: str,
    token: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> Any:
    data = None
    headers = {
        "Authorization": f"Bot {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:
        body = response.read()
        return json.loads(body) if body else None


def attachment_summary(attachment: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": attachment.get("id"),
        "filename": attachment.get("filename"),
        "content_type": attachment.get("content_type"),
        "size": attachment.get("size"),
        "url": attachment.get("url"),
    }


def message_summary(message: dict[str, Any]) -> dict[str, Any]:
    author = message.get("author") or {}
    member = message.get("member") or {}
    reference = message.get("message_reference") or {}
    return {
        "message_id": message.get("id"),
        "channel_id": message.get("channel_id"),
        "guild_id": message.get("guild_id"),
        "timestamp": message.get("timestamp"),
        "edited_timestamp": message.get("edited_timestamp"),
        "author": {
            "id": author.get("id"),
            "username": author.get("username"),
            "global_name": author.get("global_name"),
            "bot": author.get("bot", False),
        },
        "member_role_ids": member.get("roles", []),
        "content": message.get("content", ""),
        "attachments": [
            attachment_summary(attachment)
            for attachment in message.get("attachments", [])
        ],
        "referenced_message_id": reference.get("message_id"),
    }


def fetch_member_roles(
    token: str, guild_id: str, user_id: str, cache: dict[str, set[str]]
) -> set[str]:
    # REST message objects do not include member roles. Fetch the member record instead.
    if user_id not in cache:
        try:
            member = api_json(f"/guilds/{guild_id}/members/{user_id}", token)
        except HTTPError as error:
            if error.code != 404:
                raise
            member = None
        cache[user_id] = {str(value) for value in (member or {}).get("roles", [])}
    return cache[user_id]


def identity(token: str) -> dict[str, Any]:
    user = api_json("/users/@me", token)
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "global_name": user.get("global_name"),
        "bot": user.get("bot", False),
        "verified": user.get("verified"),
    }


def list_channels(token: str) -> dict[str, Any]:
    guild_id = configured_id("DISCORD_GUILD_ID")
    channels = api_json(f"/guilds/{guild_id}/channels", token)
    summaries = [
        {
            "id": channel.get("id"),
            "name": channel.get("name"),
            "type": channel.get("type"),
            "parent_id": channel.get("parent_id"),
            "position": channel.get("position"),
        }
        for channel in channels
    ]
    return {"guild_id": guild_id, "count": len(summaries), "channels": summaries}


def read_messages(args: argparse.Namespace, token: str) -> dict[str, Any]:
    if not 1 <= args.limit <= 100:
        raise ValueError("--limit must be between 1 and 100")
    channel_id = configured_id("DISCORD_CHANNEL_ID", args.channel_id)
    role_id = None
    user_ids: set[str] = set()
    guild_id = None
    if args.management_only:
        configured_role = os.environ.get("DISCORD_MANAGEMENT_ROLE_ID")
        role_id = (
            snowflake(configured_role, "DISCORD_MANAGEMENT_ROLE_ID")
            if configured_role
            else None
        )
        user_ids = management_user_ids()
        if not role_id and not user_ids:
            raise ValueError(
                "--management-only requires DISCORD_MANAGEMENT_ROLE_ID or "
                "DISCORD_MANAGEMENT_USER_IDS"
            )
        if role_id:
            if not os.environ.get("DISCORD_GUILD_ID"):
                raise ValueError(
                    "DISCORD_MANAGEMENT_ROLE_ID filtering also requires DISCORD_GUILD_ID"
                )
            guild_id = configured_id("DISCORD_GUILD_ID")
    query: dict[str, str | int] = {"limit": args.limit}
    for name in ("before", "after", "around"):
        value = getattr(args, name)
        if value:
            query[name] = snowflake(value, f"--{name}")
    messages = api_json(
        f"/channels/{channel_id}/messages?{urlencode(query)}", token
    )
    if args.management_only:
        member_cache: dict[str, set[str]] = {}
        kept = []
        for message in messages:
            author = message.get("author") or {}
            author_id = str(author.get("id", ""))
            if author_id in user_ids:
                kept.append(message)
            elif role_id and author_id and not author.get("bot", False):
                roles = fetch_member_roles(token, guild_id, author_id, member_cache)
                if role_id in roles:
                    kept.append(message)
        messages = kept
    messages.sort(key=lambda item: str(item.get("timestamp", "")))
    summaries = [message_summary(message) for message in messages]
    return {"channel_id": channel_id, "count": len(summaries), "messages": summaries}


def get_message(args: argparse.Namespace, token: str) -> dict[str, Any]:
    channel_id = configured_id("DISCORD_CHANNEL_ID", args.channel_id)
    message_id = snowflake(args.message_id, "message_id")
    message = api_json(f"/channels/{channel_id}/messages/{message_id}", token)
    return message_summary(message)


def read_content(args: argparse.Namespace) -> str:
    if args.content is not None:
        content = args.content
    elif args.content_file == "-":
        content = sys.stdin.read()
    else:
        content = Path(args.content_file).read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("Message content must not be empty")
    return content


def send_message(args: argparse.Namespace, token: str) -> dict[str, Any]:
    channel_id = configured_id("DISCORD_CHANNEL_ID", args.channel_id)
    content = read_content(args)
    allowed_mentions: dict[str, Any] = {
        "parse": [],
        "roles": [],
        "users": [],
        "replied_user": False,
    }
    if args.mention_management:
        role_id = configured_id("DISCORD_MANAGEMENT_ROLE_ID")
        content = f"<@&{role_id}>\n{content}"
        allowed_mentions["roles"] = [role_id]
    if len(content) > 2000:
        raise ValueError("Discord message content must not exceed 2000 characters")
    payload: dict[str, Any] = {
        "content": content,
        "allowed_mentions": allowed_mentions,
    }
    if args.reply_to:
        payload["message_reference"] = {
            "message_id": snowflake(args.reply_to, "--reply-to"),
            "channel_id": channel_id,
            "fail_if_not_exists": True,
        }
    message = api_json(
        f"/channels/{channel_id}/messages", token, method="POST", payload=payload
    )
    return message_summary(message)


def error_detail(error: HTTPError) -> str:
    body = error.read().decode("utf-8", errors="replace")
    try:
        value = json.loads(body)
    except json.JSONDecodeError:
        return body[:500]
    if error.code == 429:
        retry_after = value.get("retry_after")
        return f"rate limited; retry_after={retry_after} seconds"
    message = value.get("message")
    code = value.get("code")
    return f"{message or 'request failed'} (Discord code {code})"


def main() -> int:
    args = parse_args()
    try:
        token = require_token()
        if args.command == "identity":
            result = identity(token)
        elif args.command == "channels":
            result = list_channels(token)
        elif args.command == "read":
            result = read_messages(args, token)
        elif args.command == "message":
            result = get_message(args, token)
        else:
            result = send_message(args, token)
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        print(
            f"Discord API error {error.code}: {error_detail(error)}", file=sys.stderr
        )
        return 1
    except URLError as error:
        print(f"Discord connection error: {error.reason}", file=sys.stderr)
        return 1
    except TimeoutError:
        print("Discord connection error: request timed out", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"File error: {error}", file=sys.stderr)
        return 2

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
