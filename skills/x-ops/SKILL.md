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

**Minimize Bash calls.** Every `$X` call is a tool round-trip. Combine and reuse data.

1. Run `$X profile rdsaltbo` — get follower count, determine tier
2. Run `$X search "<query>" 20` for each query in task description. Search results already include `replies`, `author_followers` — use these directly for pre-check. No need to call `$X tweet` separately.
3. From search results, filter candidates: `replies > 0` AND `author_followers` in tier range. Attempt replies on filtered candidates only.
4. Run `$X mentions 726438383401074688` — reply to actionable ones
5. Follow: pick users from search results whose profiles look good (already have author_followers), then `$X follow <user_id>`
6. Post original tweet only if task description includes a tweet plan
7. Log all actions per Comment Standards
8. Create next task per Task Standards

**Target: complete a cycle in 10-15 Bash calls, not 40+.**

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

Use the `replies` and `author_followers` fields from search results directly — do NOT call `$X tweet` separately for each candidate. Only reply to posts where:
- `replies > 0` — someone else has replied, so replies are open
- `author_followers` is within target range for current tier

NOTE: X API may block replies from accounts without prior mutual engagement. If all replies return 403, pivot to follow + original tweets and reply only to mentions.

## De-duplication

Do NOT reply to or engage with the same person more than once per cycle. Check the task description's "Follow-up from last cycle" section — if you already replied to someone in the last 2 cycles, skip them unless they directly asked you a question in a mention.

This prevents spamming the same people when cycles run close together.

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

⚠️ CRITICAL: You MUST include --scheduled-at. Without it, the task runs immediately and creates an infinite loop that spams the account. This has happened before — do NOT skip this parameter.

Calculate the scheduled time with a random offset (avoid exact intervals — looks robotic):
```bash
OFFSET=$((110 + RANDOM % 40))m  # 110-150 minutes (roughly 2h with jitter)
NEXT=$(date -u -v+${OFFSET} +"%Y-%m-%dT%H:%M:%SZ")

# Check if NEXT falls in quiet hours (UTC 06:00-14:00 = EST 01:00-09:00 = PST 22:00-06:00)
# If so, push to 14:00 UTC (09:00 EST / 06:00 PST)
NEXT_HOUR=$(date -u -v+${OFFSET} +"%H")
if [ "$NEXT_HOUR" -ge 6 ] && [ "$NEXT_HOUR" -lt 14 ]; then
  NEXT=$(date -u -v+1d +"%Y-%m-%dT14:%M:%SZ")  # next day 14:00 UTC
fi
ak create task \
  --board jb21kfv6 \
  --assign-to e6f896b845f81e93 \
  --scheduled-at "$NEXT" \
  --title "x-ops #<next-seq>: <focus>" \
  --description "<filled template>" \
  --priority medium \
  --labels "ops,engagement,connect"
```

Verify the created task has a scheduled_at value in the response. If not, cancel it immediately.

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
