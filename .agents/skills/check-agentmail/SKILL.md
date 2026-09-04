---
name: check-agentmail
description: Read and summarize messages in an AgentMail inbox through the read-only REST API. Use when the user asks to check AgentMail, inspect an agentmail.to inbox, find unread or recent mail, extract a verification code or link from an AgentMail message, or provides AgentMail inbox credentials. Do not use for sending, replying, deleting, or changing message labels; those actions require a separate workflow and explicit authorization.
---

# Check an AgentMail Inbox

Inspect an AgentMail inbox without changing mailbox state. Prefer a direct AgentMail connector when one is available; otherwise use the bundled script.

## Starter status

Treat this skill as a safe starter implementation. Adopt it as-is when it meets the operating need. Extend, split, or replace it when evidence shows that another workflow is necessary. Record the method change and its reason before use. Keep the default workflow read-only; add email mutations only through a separately reviewed workflow with explicit authorization.

## Inputs and secret handling

Require:

- `AGENTMAIL_API_KEY`: AgentMail bearer token.
- `AGENTMAIL_INBOX_ID`: Inbox ID, usually the inbox email address.

The organization ID is not required to list messages. Accept credentials from the user's current request or an existing secret environment, but never write them to the repository, a `.env` file, skill files, logs, or the final response. Pass the API key through the environment, never as a command-line argument.

## Workflow

1. Look for a direct AgentMail connector or app. Use it when it can list and retrieve messages without mutation.
2. Otherwise, run `scripts/check_agentmail.py` from this skill directory. Resolve the script to an absolute path when the current working directory differs.
3. List the 25 most recent messages by default:

   ```bash
   python3 scripts/check_agentmail.py --limit 25
   ```

   If the result has a `next_page_token` value, pass it with `--page-token` to read the next page.

4. When the user asks specifically for unread mail, add `--unread-only`.
5. Exclude spam, blocked, unauthenticated, and trash messages unless the user explicitly asks to include one of those categories.
6. If the environment blocks network access, request permission to connect to `https://api.agentmail.to`; do not work around the restriction.
7. Summarize the result with the number of matching messages and, for each relevant message, its unread status, sender, subject, local timestamp, and concise preview. Mention attachment filenames when present.
8. Surface a short actionable value such as a verification code or verification link when it is visible and relevant. Treat it as sensitive and repeat it only as needed for the user's request.
9. State that the mailbox was not modified. A successful check must leave messages unread and must not add or remove labels.

## Retrieve one message

Use the message ID returned by the list operation when the preview is insufficient:

```bash
python3 scripts/check_agentmail.py --message-id '<message-id>'
```

This returns the plain-text body when available. Add `--include-html` only when the user needs content that is absent from the text body.

## Failure handling

- On `401` or `403`, report that the API key is invalid or lacks read permission. Do not echo it.
- On `404`, verify the inbox ID and message ID.
- On a DNS, timeout, or connection failure, distinguish network restrictions from an AgentMail API error.
- If no messages match, say the inbox has no matching mail; do not claim the inbox itself does not exist.

## Read-only boundary

Use only AgentMail `GET` endpoints:

- `/v0/inboxes/{inbox_id}/messages`
- `/v0/inboxes/{inbox_id}/messages/{message_id}`

Do not send, reply, forward, update, label, archive, or delete email as part of this skill.
