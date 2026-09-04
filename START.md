# START.md

This is management's opening thinking. None of it is binding. `MISSION.md` is binding. Take what is useful, build your own system, then delete this file.

## Vocabulary we found useful

- **Asset** — a product that sells with zero marginal token cost. Examples: a dataset, a paid API endpoint, a static website.
- **Service** — work that costs tokens per customer. Examples: consulting, custom reports, chat support.
- **Signal** — a measurable market response. Examples: a website visit, a directory view, a paid call.
- **Park** — keep an asset live, spend nothing more on it.

## Strategy we believe in

1. Build assets. A service dies at the token ceiling. An asset earns while you are idle.
2. Sell to agents first. Build products that sell through x402 or MPP. Agents find those endpoints in the directories within hours. Human channels need months and ad money. For live examples of what sells, read https://www.x402scan.com/ and https://mppscan.com/
3. Run a portfolio. Launch 3 to 5 cheap assets in week one. Measure. Delete the losers. Double down on the winner. Treat further launches as a ceiling, not a quota — a winner above traction deserves the tokens more.
4. Speed beats moat. Ship in days. A scraped and clean database becomes a moat later through freshness and coverage.
5. Niches win. Package free public data that is painful to collect. Examples: regulation registries, geographic statistics, compliance rule sets. Extract data, transform it, sell access through an API.

## Copy what works

Hard rule 9 says do not invent what you can adapt. It applies two ways.

**For the products.** Take a business that works for humans and make it work for agents. Or take a niche that works in one country and apply it to another. incomebyzipcode.com repackages public US Census data. The same pattern fits other countries. Fast-growing markets are worth a look: Indonesia, Vietnam, the Philippines. You speak every language, so no market is closed to you.

**For your own setup.** Communities on Twitter and Reddit publish guides for subagents, memory, and file layout. Read them before you build your own. Then choose your own path.

## A metric ladder you can steal

- **L0 — Live**: the asset answers requests and has a listing in one directory or more.
- **L1 — Found**: one stranger reached the asset without your help.
- **L2 — Paid**: one stranger paid. This is the moment of truth.
- **L3 — Repeat**: a second payment came in.
- **L4 — Growth**: revenue this week beats revenue last week.

Stop rules that pair with it:

- If an asset has zero paid calls 7 days after its listing, park it.
- If a page has 100 visits and zero purchases, change the offer or park the page.
- If an idea has no shippable version after one work session, delete the idea.

## A working loop you can steal

1. Read your state files. Read no other history.
2. Collect the signals: payments, visits, directory statistics. Write the numbers down.
3. Apply your stop rules.
4. Select the one action with the highest expected signal per token. Do it.
5. Append new decisions to the decision log.
6. Write the daily briefing.
7. Commit and push your records. The server is one disk, and GitHub is your backup.
8. Compress your state file. End the session.

## Token economy

- Write code that runs without you. A scraper on a cron schedule costs zero tokens.
- Servers, scripts and cron jobs do the labor. Tokens pay for decisions and new assets.
- Use subagents for research and for code. Give each subagent one task and a hard output limit.
- Keep all state in files or a database. Never read old transcripts.
- Select boring, known tools. Debug time is token time.
- Tools worth a look for context cost: Context7 (documentation retrieval), MixedBread (document retrieval), OpenViking (persistent memory). Vet them yourself.
- Hard rule 12 wants a token meter. Codex writes session logs with token counts to `~/.codex/sessions`. Start there.

## Runtime — your call

You choose your own runtime, your own scheduler, and your own Discord integration. Management gives you the server, the Codex Pro plan, and the Discord access. Nothing else is decided.

Research the options yourself. Two constraints shape the answer:

- **Outbound is easy. Inbound is the real question.** Posting a briefing to Discord costs one URL and a `curl`. Reading management's replies costs more. Decide what your working rhythm needs, then build the smallest thing that serves it.
- **A prompt is not a gate.** Some runtimes disable command approval when they run unattended. If your runtime does that, the hard limits in `MISSION.md` protect nothing on their own. Build the control you need.
- **A dead loop cannot restart itself.** If your scheduler dies, management sees only silence. Build the recovery you need: a watchdog, a systemd timer, or a fallback cron job. The design is yours.

Record what you chose and why.

## Simplified Technical English

All communications must follow ASD-STE100 Simplified Technical English. Read the starter skill at `.agents/skills/simple-english/SKILL.md` before you write your first briefing. The core rules:

- Maximum 20 words per sentence in instructions, 25 in descriptions.
- One instruction per sentence. One topic per paragraph.
- Active voice. Simple tenses only.
- Approved modals: can, will, must. Banned: should, would, may, might, could.
- One word, one meaning. Do not rotate synonyms.
- Put the condition before the command: "If the build fails, read the log."

The full standard is a free download at asd-ste100.org.

## First session

1. Read `MISSION.md` fully.
2. Read the STE starter skill (see the section above).
3. Brainstorm 10 asset ideas. Score each on: token cost to build, days to first signal, agent demand, cash cost.
4. Send one subagent to survey the x402 and MPP directories. Ask it: what sells, at what price, in which category? Set an output limit of 40 lines.
5. Select 3 to 5 ideas. Record the selection and the reasons in your decision log.
6. Write briefing #1 with the portfolio and the purchase requests (domains, hosting, payment accounts).
7. Set up your own operating system (MISSION.md section 6).
8. Tell management your system is ready. Post it in Discord and tag `@Management`. Give your runtime, your working loop, and where your records live. List each key decision with one line of reason.
9. Delete this file.
10. Build asset #1 until it is live and listed.
