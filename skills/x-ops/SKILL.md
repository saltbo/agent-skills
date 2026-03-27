---
name: x-ops
description: X (Twitter) account operations via MCP tools — post, reply, like, search, monitor mentions
user-invocable: false
allowed-tools:
  - Bash
  - Read
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

# X Ops — MCP-Based X Account Operations

You operate an X (Twitter) account through the `x-twitter` MCP server tools.
All interactions use the official X API v2 — no browser automation.

## Available MCP Tools

### Write Operations

- `mcp__x-twitter__post_tweet` — Post a tweet. Params: `text` (required), `reply_to` (tweet ID for replies), `media_paths`, `tags`
- `mcp__x-twitter__favorite_tweet` — Like a tweet. Params: `tweet_id`
- `mcp__x-twitter__bookmark_tweet` — Bookmark a tweet. Params: `tweet_id`
- `mcp__x-twitter__delete_tweet` — Delete a tweet. Params: `tweet_id`

### Read Operations

- `mcp__x-twitter__search_twitter` — Search tweets. Params: `query`, `count`, `product` (Top/Latest)
- `mcp__x-twitter__get_user_mentions` — Get mentions. Params: `user_id`, `count`
- `mcp__x-twitter__get_user_by_screen_name` — Lookup user. Params: `screen_name`
- `mcp__x-twitter__get_user_profile` — Get profile details. Params: `user_id`
- `mcp__x-twitter__get_tweet_details` — Get a single tweet. Params: `tweet_id`
- `mcp__x-twitter__get_latest_timeline` — Following timeline. Params: `count`
- `mcp__x-twitter__get_timeline` — For You timeline. Params: `count`
- `mcp__x-twitter__get_user_followers` — Get followers. Params: `user_id`, `count`
- `mcp__x-twitter__get_user_following` — Get following. Params: `user_id`, `count`
- `mcp__x-twitter__get_trends` — Get trending topics.

## Logging

Log every action to the task:
```bash
ak task log <task-id> "Posted tweet: <content preview>"
ak task log <task-id> "Liked tweet by @<user>: <content preview>"
ak task log <task-id> "Replied to @<user>: <content preview>"
```

## Rate Limits (X API v2)

| Operation | Limit / 15min |
|-----------|--------------|
| search    | 60           |
| mentions  | 10           |
| user lookup | 95         |
| tweet by id | 300        |
| post tweet | 100/day      |
| like      | 1000/day     |

Wait 2-3 seconds between write operations to avoid rate limits.

## Rules

- **Never follow/unfollow** unless the task specifically requests it.
- **Never DM** unless the task specifically requests it.
- **Never delete tweets** unless the task specifically requests it.
- **If auth fails**, log the error and stop. Do not retry.
