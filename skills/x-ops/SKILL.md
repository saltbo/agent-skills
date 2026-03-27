---
name: x-ops
description: X (Twitter) account operations via MCP tools — post, reply, like, search, monitor mentions
user-invocable: false
allowed-tools:
  - Bash
  - mcp__x-twitter__post_tweet
  - mcp__x-twitter__search_twitter
  - mcp__x-twitter__get_user_mentions
  - mcp__x-twitter__get_user_by_screen_name
  - mcp__x-twitter__get_user_profile
  - mcp__x-twitter__favorite_tweet
  - mcp__x-twitter__unfavorite_tweet
  - mcp__x-twitter__get_tweet_details
  - mcp__x-twitter__get_timeline
  - mcp__x-twitter__get_latest_timeline
  - mcp__x-twitter__get_user_followers
  - mcp__x-twitter__get_user_following
  - mcp__x-twitter__get_trends
  - mcp__x-twitter__bookmark_tweet
  - mcp__x-twitter__delete_tweet
---

# X Ops — Operational Procedures

## MCP Tools Reference

### Write
- `post_tweet` — params: `text`, `reply_to` (tweet ID), `media_paths`, `tags`
- `favorite_tweet` — params: `tweet_id`
- `bookmark_tweet` — params: `tweet_id`
- `delete_tweet` — params: `tweet_id`

### Follow (via x-cli.py, not MCP)

The MCP server does not support follow. Use x-cli.py instead:

```bash
X="uv run ~/.claude/skills/saltbo/agent-skills/skills/x-ops/x-cli.py"
$X follow <user_id>
$X unfollow <user_id>
```

Requires env vars: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET (already set globally).

### Read
- `search_twitter` — params: `query`, `count`, `product` (Top/Latest)
- `get_user_mentions` — params: `user_id`, `count`
- `get_user_by_screen_name` — params: `screen_name`
- `get_user_profile` — params: `user_id`
- `get_tweet_details` — params: `tweet_id`
- `get_latest_timeline` — params: `count`
- `get_timeline` — params: `count`
- `get_user_followers` — params: `user_id`, `count`
- `get_user_following` — params: `user_id`, `count`
- `get_trends`

## Rate Limits (X API v2)

| Operation | Limit |
|-----------|-------|
| search    | 60 / 15min |
| mentions  | 10 / 15min |
| user lookup | 95 / 15min |
| tweet by id | 300 / 15min |
| post tweet | 100 / day |
| like      | 1000 / day |

Wait 2-3 seconds between write operations.

## Cycle Workflow

1. Search using the queries specified in the task description
2. Find 6-8 candidate posts from high-reach accounts (prefer posts under 2-4 hours old)
3. Reply one by one. Skip 403s. Keep going until target reply count is met.
4. Check mentions: `get_user_mentions` with user_id from task context
5. Reply to actionable mentions
6. Follow relevant developers (check profile before following)
7. Post 1 original tweet per the task plan
8. Log all actions per Comment Standards
9. Create next task per Task Standards

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
- `"follow me" developer "AI tools"` (filter for real builders, skip spammers)
- `"shipping daily" AI code`

## Task Standards

### Title format
`x-ops #<seq>: <focus keyword>`

Examples:
- `x-ops #3: claude-code-tips engagement`
- `x-ops #4: vibe-coding trend + codex thread`

### Description template
```
## Search queries
- <query 1>
- <query 2>

## Tweet plan
- Type: <hot take | build-in-public | tip | comparison | observation>
- Topic: <what to write about>

## Follow-up from last cycle
- <conversation to continue, or "none">

## Notes from last cycle
- <observations about what worked or didn't>
```

### Self-continuation
After completing a cycle, create next task:
```bash
ak create task \
  --board <board-id> \
  --assign-to <self-agent-id> \
  --scheduled-at <1 hour from now, ISO 8601> \
  --title "x-ops #<next-seq>: <focus>" \
  --description "<filled template>"
```

## Comment Standards

Post comments using `ak task log <task-id> "<message>"`:

**1 — Start**
```
CYCLE START | Queries: <q1>, <q2> | Targets found: <n>
```

**2 — Replies**
```
REPLIES (<success>/<attempted>)
✓ @<user> (<followers>) — "<first 60 chars of reply>" [tweet:<id>]
✗ @<user> — 403 reply restricted
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

**5 — Tweet**
```
TWEET [<id>]
"<full tweet text>"
Type: <type>
```

**6 — Summary**
```
CYCLE COMPLETE
Replies: <n>/<n> | Mentions: <n> | Follows: <n> | Tweet: 1
Next: <task-id> scheduled <time>
```

## Reply Pre-check (avoid 403)

Before replying to a post, use `get_tweet_details` to check if it has replies (reply_count > 0). Posts with existing replies from other users are open for replies. Posts with 0 replies from a high-follower account likely have reply restrictions enabled — skip them.

Also skip posts that contain "subscribers only" or "verified only" language.

## Error Handling

- 403 on reply → skip target, find another. Do NOT count as success.
- Rate limit error → wait until reset, then retry.
- Auth error → stop and report. Do not retry.
- Other errors → retry once after 5 seconds.
