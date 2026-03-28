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

## API Constraint

X API blocks replies/quotes to accounts that haven't mentioned @rdsaltbo. Do NOT attempt replies to strangers — always 403. Only reply to mentions.

## Cycle Workflow

**Minimize Bash calls.** Every `$X` call is a tool round-trip. Target: 8-12 calls per cycle.

1. `$X profile rdsaltbo` — get follower count, determine tier (1 call)
2. `$X search "<query>" 20` — run 1-2 searches from task description (1-2 calls)
3. `$X mentions 726438383401074688` — check mentions (1 call)
4. Reply to actionable mentions only — do NOT reply to strangers (0-2 calls)
5. Like 5-8 posts from search results — pick substantive posts from target developers (5-8 calls, can batch quickly)
6. Follow 3-5 developers from search results — use author_id from search data directly (3-5 calls)
7. Post 1 original tweet based on what you observed in search (1 call)
8. Log actions + create next task (2 calls)

## Search Query Rotation

Use 1-2 per cycle. These find both content inspiration and like/follow targets:
- `claude code`
- `AI coding agent`
- `cursor AI` OR `codex`
- `multi-agent` AND `code`
- `vibe coding`
- `AI developer tools`
- `coding agent workflow`
- `"build in public" AI tools`
- `"looking to connect" developer AI`
- `"indie hacker" AI agent`

## De-duplication

Do NOT like/follow the same person more than once per cycle. Check the task description's "Follow-up from last cycle" — if you already followed someone in previous cycles, skip them.

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

**2 — Likes**
```
LIKES (<count>)
♥ @<user> (<followers>) — "<first 50 chars of their post>" [tweet:<id>]
```

**3 — Follows**
```
FOLLOWS (<count>)
+ @<user> (<followers>) — <reason>
```

**4 — Mentions**
```
MENTIONS (<count> new)
↩ @<user> — "<reply preview>" [tweet:<id>]
— no actionable mentions
```

**5 — Tweet**
```
TWEET [<id>]
"<full tweet text>"
Type: <type>
```

**6 — Summary**
```
CYCLE COMPLETE | Followers: <n>
Likes: <n> | Follows: <n> | Mentions replied: <n> | Tweet: <0 or 1>
Next: <task-id> scheduled <time>
```

## Error Handling

- 403 on reply → skip target, find another. Do NOT count as success.
- Rate limit error → wait until reset, then retry.
- Auth error → stop and report. Do not retry.
- If `ak create task` fails → retry once after 10 seconds.
