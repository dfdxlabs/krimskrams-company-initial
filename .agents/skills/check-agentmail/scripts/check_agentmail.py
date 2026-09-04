#!/usr/bin/env python3
"""Read AgentMail messages without modifying mailbox state."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.agentmail.to/v0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or retrieve AgentMail messages using read-only GET requests."
    )
    parser.add_argument("--limit", type=int, default=25, help="Messages to request (1-100).")
    parser.add_argument(
        "--unread-only", action="store_true", help="Return only messages labeled unread."
    )
    parser.add_argument("--include-spam", action="store_true")
    parser.add_argument("--include-blocked", action="store_true")
    parser.add_argument("--include-unauthenticated", action="store_true")
    parser.add_argument("--include-trash", action="store_true")
    parser.add_argument(
        "--page-token",
        help="Continue a listing with the next_page_token value from a previous result.",
    )
    parser.add_argument(
        "--message-id", help="Retrieve one message instead of listing the inbox."
    )
    parser.add_argument(
        "--include-html",
        action="store_true",
        help="Include a retrieved message's HTML body in the output.",
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    if args.include_html and not args.message_id:
        parser.error("--include-html requires --message-id")
    if args.page_token and args.message_id:
        parser.error("--page-token is not valid with --message-id")
    return args


def require_environment() -> tuple[str, str]:
    api_key = os.environ.get("AGENTMAIL_API_KEY")
    inbox_id = os.environ.get("AGENTMAIL_INBOX_ID")
    missing = [
        name
        for name, value in (
            ("AGENTMAIL_API_KEY", api_key),
            ("AGENTMAIL_INBOX_ID", inbox_id),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")
    return api_key, inbox_id


def get_json(url: str, api_key: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "check-agentmail-skill/1.0",
        },
        method="GET",
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def attachment_summary(message: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "filename": attachment.get("filename"),
            "content_type": attachment.get("content_type"),
            "size": attachment.get("size"),
        }
        for attachment in message.get("attachments", [])
    ]


def message_summary(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": message.get("message_id"),
        "thread_id": message.get("thread_id"),
        "labels": message.get("labels", []),
        "timestamp": message.get("timestamp"),
        "from": message.get("from"),
        "to": message.get("to", []),
        "subject": message.get("subject"),
        "preview": message.get("preview"),
        "attachments": attachment_summary(message),
    }


def list_messages(args: argparse.Namespace, api_key: str, inbox_id: str) -> dict[str, Any]:
    params: dict[str, Any] = {
        "limit": args.limit,
        "include_spam": str(args.include_spam).lower(),
        "include_blocked": str(args.include_blocked).lower(),
        "include_unauthenticated": str(args.include_unauthenticated).lower(),
        "include_trash": str(args.include_trash).lower(),
    }
    if args.page_token:
        params["page_token"] = args.page_token
    query = urlencode(params)
    url = f"{API_BASE}/inboxes/{quote(inbox_id, safe='')}/messages?{query}"
    result = get_json(url, api_key)
    messages = result.get("messages", [])
    if args.unread_only:
        messages = [message for message in messages if "unread" in message.get("labels", [])]
    summaries = [message_summary(message) for message in messages]
    return {
        "count": len(summaries),
        "api_count": result.get("count", 0),
        "limit": result.get("limit", args.limit),
        "next_page_token": result.get("next_page_token"),
        "messages": summaries,
    }


def get_message(
    args: argparse.Namespace, api_key: str, inbox_id: str
) -> dict[str, Any]:
    url = (
        f"{API_BASE}/inboxes/{quote(inbox_id, safe='')}/messages/"
        f"{quote(args.message_id, safe='')}"
    )
    message = get_json(url, api_key)
    result = message_summary(message)
    result.update(
        {
            "reply_to": message.get("reply_to", []),
            "cc": message.get("cc", []),
            "text": message.get("text"),
            "extracted_text": message.get("extracted_text"),
        }
    )
    if args.include_html:
        result["html"] = message.get("html")
        result["extracted_html"] = message.get("extracted_html")
    return result


def main() -> int:
    args = parse_args()
    try:
        api_key, inbox_id = require_environment()
        result = (
            get_message(args, api_key, inbox_id)
            if args.message_id
            else list_messages(args, api_key, inbox_id)
        )
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print(f"AgentMail API error {error.code}: {detail}", file=sys.stderr)
        return 1
    except URLError as error:
        print(f"AgentMail connection error: {error.reason}", file=sys.stderr)
        return 1
    except TimeoutError:
        print("AgentMail connection error: request timed out", file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
