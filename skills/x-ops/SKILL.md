---
name: x-ops
description: X (Twitter) account operations via headless browser — post, reply, like, monitor timeline
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Write
---

# X Ops — Browser-Based X Account Operations

You operate an X (Twitter) account through gstack browse (headless Chromium + Playwright).
All interactions happen via CLI commands — there is no X API involved.

## Setup (run once per session)

```bash
B=~/.claude/skills/gstack/browse/dist/browse

# Import login cookies from the host Chrome
$B cookie-import-browser chrome --domain x.com
$B cookie-import-browser chrome --domain .x.com

# Navigate to X and verify login
$B goto https://x.com/home
```

**Verify**: run `$B url` — if it contains `flow/login`, cookies have expired. Log an error and stop.

After setup, always assign:
```bash
B=~/.claude/skills/gstack/browse/dist/browse
```

## Core Operations

### Post a Tweet

```bash
$B goto https://x.com/home
$B snapshot -i                    # find the post textbox
$B click @e<post-textbox>         # click the "Post text" textbox
$B type "Your tweet content"      # type the content
$B snapshot -i                    # find the Post button
$B click @e<post-button>          # click Post (ensure it's enabled)
$B snapshot -D                    # diff to confirm post was published
$B screenshot /tmp/posted.png     # evidence
```

**Important**: The Post button is disabled until text is entered. Always verify it's enabled before clicking.

### Reply to a Tweet

```bash
$B goto https://x.com/<user>/status/<tweet-id>
$B snapshot -i                    # find Reply textbox
$B click @e<reply-textbox>
$B type "Your reply"
$B click @e<reply-button>
$B snapshot -D                    # confirm reply posted
```

### Like a Tweet

```bash
$B goto https://x.com/<user>/status/<tweet-id>
$B snapshot -i                    # find Like button
$B click @e<like-button>          # the button text includes "Like" or "Likes"
```

### Retweet / Quote

```bash
$B snapshot -i                    # find Repost button
$B click @e<repost-button>        # opens repost menu
$B snapshot -i                    # find "Repost" or "Quote"
$B click @e<repost-option>
```

### Read Timeline

```bash
$B goto https://x.com/home
$B snapshot -c                    # compact view of timeline
```

The timeline snapshot contains article elements with:
- Author name and handle
- Post text content
- Engagement metrics (replies, reposts, likes, views)
- Timestamps

### Read Notifications

```bash
$B goto https://x.com/notifications
$B snapshot -c
```

### View a Profile

```bash
$B goto https://x.com/<username>
$B snapshot -c
```

### Search

```bash
$B goto "https://x.com/search?q=your+query&src=typed_query"
$B snapshot -c
```

### Switch Timeline Tab

```bash
$B goto https://x.com/home
$B snapshot -i                    # find tab buttons: "For you", "Following", custom lists
$B click @e<tab>
$B snapshot -c                    # read the new tab content
```

## Snapshot Tips

- `$B snapshot -i` — interactive elements only (buttons, links, inputs). Use for finding what to click.
- `$B snapshot -c` — compact view, good for reading content.
- `$B snapshot -D` — diff vs previous snapshot, good for verifying an action worked.
- `@e` refs change after navigation — always re-snapshot before interacting.

## Scrolling for More Content

```bash
$B scroll                         # scroll to bottom
$B snapshot -c                    # read newly loaded content
```

## Evidence & Reporting

After each action, take a screenshot as evidence:
```bash
$B screenshot /tmp/x-action-<description>.png
```

Log every action to the task:
```bash
ak task log <task-id> "Posted tweet: <content preview>"
ak task log <task-id> "Liked tweet by @<user>: <content preview>"
```

## Rules

- **Never post without explicit content** in the task description. Do not generate tweet content autonomously.
- **Never follow/unfollow** unless the task specifically requests it.
- **Never DM** unless the task specifically requests it.
- **Never delete tweets** unless the task specifically requests it.
- **Rate limit yourself** — wait 3-5 seconds between actions to avoid triggering X's bot detection.
- **Always screenshot** completed actions as evidence.
- **If login fails**, log the error and stop. Do not attempt to re-authenticate.

## Waiting Between Actions

X loads content dynamically. After navigation or clicks:
```bash
$B wait --load                    # wait for page load
```

## Error Recovery

If a snapshot shows unexpected content (error page, CAPTCHA, rate limit):
1. Screenshot the error state
2. Log it: `ak task log <task-id> "Encountered error: <description>"`
3. Wait 30 seconds and retry once
4. If retry fails, stop and report
