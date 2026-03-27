---
name: x-ops
description: X (Twitter) account operations via x-cli.py — post, reply, like, search, follow
user-invocable: false
allowed-tools:
  - Bash
---

# X Ops — Operational Procedures

All operations use `x-cli.py` (tweepy + official X API v2). Set the alias at the start of every session:

```bash
X="uv run .agents/skills/x-ops/x-cli.py"
```

## Commands

### Read
```bash
$X profile <username>          # full profile with followers/following/tweet count
$X tweet <tweet_id>            # tweet with reply_count, likes, views, author_followers
$X search "<query>" [count]    # search recent tweets (min 10, max 100)
$X mentions <user_id> [count]  # mentions of a user
```

All read commands return JSON with full metrics (reply_count, followers, etc).

### Write
```bash
$X post "<text>"               # post a tweet
$X reply <tweet_id> "<text>"   # reply to a tweet
$X like <tweet_id>             # like a tweet
$X follow <user_id>            # follow a user
$X unfollow <user_id>          # unfollow a user
```

Write commands return JSON confirmation with the created tweet ID.

## Rate Limits (X API v2)

| Operation | Limit |
|-----------|-------|
| search    | 60 / 15min |
| mentions  | 10 / 15min |
| profile   | 95 / 15min |
| tweet     | 300 / 15min |
| post      | 100 / day |
| like      | 1000 / day |
| follow    | 15 / 15min |

Wait 2-3 seconds between write operations.

## Cycle Workflow

1. Check follower count: `$X profile rdsaltbo`
2. Search using the queries specified in the task description
3. For each candidate post, check `$X tweet <id>` — only reply if `replies > 0` (proves replies are open). Also check `author_followers` is within target range for current tier.
4. Reply one by one: `$X reply <tweet_id> "<text>"`. Skip 403s. Keep going until target reply count is met.
5. Check mentions: `$X mentions 726438383401074688`
6. Reply to actionable mentions
7. Follow relevant developers: check `$X profile <username>` first, then `$X follow <user_id>`
8. Post original tweet only if task description includes a tweet plan
9. Log all actions per Comment Standards
10. Create next task per Task Standards

## Search Query Rotation

### Engagement queries (for replies)
Rotate 2-3 per cycle:
- `claude code`
- `AI coding agent`
- `cursor AI` OR `codex`
- `multi-agent` AND `code`
- `vibe coding`
- `AI developer tools`
- `coding agent workflow`
- `claude code tip` OR `claude code trick`

### Connect queries (for finding people to follow)
Use 1 per cycle to find builders/creators actively seeking connections:
- `"looking to connect" developer AI`
- `"build in public" AI tools`
- `"indie hacker" AI agent`
- `"open source" "coding agent"`
- `"shipping daily" AI code`

## Reply Pre-check

Before replying, run `$X tweet <id>` and check:
- `replies > 0` — someone else has replied, so replies are open
- `author_followers` is within target range for current tier
Skip if either check fails.

## Task Standards

### Title format
`x-ops #<seq>: <focus keyword>`

### Description template
```
## Search queries
- <query 1>
- <query 2>

## Tweet plan
- Type: <hot take | build-in-public | tip | comparison | observation>
- Topic: <what to write about>
(or "None — replies + connect only cycle")

## Follow-up from last cycle
- <conversation to continue, or "none">

## Notes from last cycle
- <observations about what worked or didn't>
```

### Self-continuation
After completing a cycle, create next task. MUST include --scheduled-at:
```bash
ak create task \
  --board jb21kfv6 \
  --assign-to e6f896b845f81e93 \
  --scheduled-at <1 hour from now, ISO 8601> \
  --title "x-ops #<next-seq>: <focus>" \
  --description "<filled template>" \
  --priority medium \
  --labels "ops,engagement,connect"
```

## Comment Standards

Post comments using `ak task log <task-id> "<message>"`:

**1 — Start**
```
CYCLE START | Followers: <n> | Tier: <phase> | Queries: <q1>, <q2>
```

**2 — Replies**
```
REPLIES (<success>/<attempted>)
✓ @<user> (<followers>) — "<first 60 chars of reply>" [tweet:<id>]
✗ @<user> — 403 reply restricted
⊘ @<user> — skipped (replies:0 or out of tier range)
```

**3 — Mentions**
```
MENTIONS (<count> new)
↩ @<user> — "<reply preview>" [tweet:<id>]
— no actionable mentions
```

**4 — Follows**
```
FOLLOWS (<count>)
+ @<user> (<followers>) — <reason>
```

**5 — Tweet** (only if posted)
```
TWEET [<id>]
"<full tweet text>"
Type: <type>
```

**6 — Summary**
```
CYCLE COMPLETE | Followers: <n>
Replies: <n>/<n> | Mentions: <n> | Follows: <n> | Tweet: <0 or 1>
Next: <task-id> scheduled <time>
```

## Error Handling

- 403 on reply → skip target, find another. Do NOT count as success.
- Rate limit error → wait until reset, then retry.
- Auth error → stop and report. Do not retry.
- If `ak create task` fails → retry once after 10 seconds.
