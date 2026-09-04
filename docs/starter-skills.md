# Starter skills

The repository contains starter skills in `.agents/skills`. They give the agent a small, working interface for an integration or a required workflow. They are not immutable rules or a required final architecture.

The agent can adopt a starter skill as-is. The agent can also extend, split, or replace it when evidence shows that the current workflow is not sufficient. Before the agent uses a changed method, it must record the change and one line of reason. Every change must keep the limits in `MISSION.md`.

## Adoption rules

1. Read the applicable `SKILL.md` file before use.
2. Verify the required environment variables and the remote identity.
3. Start with the smallest capability that completes the task.
4. Keep credentials in the company `.env` file. Do not put credentials in Git, logs, prompts, or documentation.
5. Test a changed script before live use.
6. Update the skill and this document when the operating interface changes.
7. Record a method change and its reason before the changed method is used.

## AgentMail starter

Location: `.agents/skills/check-agentmail`

Purpose: Read and summarize company email without changing mailbox state.

Environment:

```dotenv
AGENTMAIL_API_KEY=...
AGENTMAIL_INBOX_ID=...
```

The starter is read-only. If the business needs email send or reply operations, create or extend a reviewed workflow with explicit authorization. Do not silently add mutation to the read-only path.

## Discord starter

Location: `.agents/skills/use-discord`

Purpose: Read the private management channel and send briefings, decision requests, and replies through the agent's own bot account.

The bot account must be a dedicated Discord bot identity. Do not use a management member's human account or user token. Management creates the bot, adds it to the company server, and supplies the configuration through the company `.env` file.

Environment:

```dotenv
DISCORD_BOT_TOKEN=...
DISCORD_CHANNEL_ID=...
DISCORD_BRIEFING_CHANNEL_ID=...
DISCORD_GUILD_ID=...
DISCORD_MANAGEMENT_ROLE_ID=...
DISCORD_MANAGEMENT_USER_IDS=123456789012345678,234567890123456789
```

`DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` are required. The other values support channel discovery, management role mentions, and management reply checks. Role-based reply checks also require `DISCORD_GUILD_ID`.

`DISCORD_CHANNEL_ID` points to `#management`, which is the default channel for decisions and approvals. `DISCORD_BRIEFING_CHANNEL_ID` points to `#briefing`. Send each daily briefing there with `--channel-id "$DISCORD_BRIEFING_CHANNEL_ID"`. The bot can read and write every channel in the server, so you can use `--channel-id` to reach any other channel.

Give the bot access only to the private management channel. The starter needs permission to view that channel, read message history, and send messages. Enable message content access so it can read management replies. Permit management role mentions only if the mission workflow needs them.

Run the identity check after initial setup or a token change:

```bash
python3 .agents/skills/use-discord/scripts/discord_bot.py identity
```

Confirm that the result has `bot: true` and the expected bot name. Then perform a read test before the first live post.

The starter uses the Discord REST API. It does not require a persistent process. If polling becomes too slow or expensive, the agent can extend the integration with a Gateway listener and a durable queue. Record that method change before use, and keep the same credential and authorization controls.

## STE writing starter

Location: `.agents/skills/simple-english`

Purpose: Write all communications in ASD-STE100 Simplified Technical English, as `MISSION.md` section 5 requires.

Environment: none. The skill needs no credentials and no network access.

Read the `SKILL.md` file before you write the first briefing. Apply it to briefings, decision logs, documentation, and replies to management.
