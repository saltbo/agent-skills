#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tweepy", "requests"]
# ///
"""Complete X (Twitter) CLI using official API v2 via tweepy."""

import json
import os
import sys
from pathlib import Path

import tweepy

ENV_FILE = Path.home() / ".config" / "x-ops" / ".env"


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()

CLIENT = tweepy.Client(
    consumer_key=os.environ["TWITTER_API_KEY"],
    consumer_secret=os.environ["TWITTER_API_SECRET"],
    access_token=os.environ["TWITTER_ACCESS_TOKEN"],
    access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    bearer_token=os.environ.get("TWITTER_BEARER_TOKEN", ""),
)

TWEET_FIELDS = ["public_metrics", "author_id", "created_at", "conversation_id"]
USER_FIELDS = ["public_metrics", "description", "location", "created_at"]
EXPANSIONS = ["author_id"]


def _fmt_tweet(t, users=None):
    m = t.public_metrics or {}
    author = None
    if users and t.author_id:
        author = next((u for u in users if u.id == t.author_id), None)
    return {
        "id": str(t.id),
        "text": t.text,
        "author_id": str(t.author_id) if t.author_id else None,
        "author": author.username if author else None,
        "author_name": author.name if author else None,
        "author_followers": (author.public_metrics or {}).get("followers_count") if author else None,
        "replies": m.get("reply_count", 0),
        "retweets": m.get("retweet_count", 0),
        "likes": m.get("like_count", 0),
        "views": m.get("impression_count", 0),
        "created_at": str(t.created_at) if t.created_at else None,
    }


def _fmt_user(u):
    m = u.public_metrics or {}
    return {
        "id": str(u.id),
        "name": u.name,
        "username": u.username,
        "description": u.description,
        "followers": m.get("followers_count", 0),
        "following": m.get("following_count", 0),
        "tweets": m.get("tweet_count", 0),
        "location": getattr(u, "location", None),
    }


def cmd_profile(args):
    """Usage: profile <username>"""
    r = CLIENT.get_user(username=args[0], user_fields=USER_FIELDS, user_auth=False)
    print(json.dumps(_fmt_user(r.data), indent=2))


def cmd_tweet(args):
    """Usage: tweet <tweet_id>"""
    r = CLIENT.get_tweet(args[0], tweet_fields=TWEET_FIELDS,
                         expansions=EXPANSIONS, user_fields=USER_FIELDS,
                         user_auth=False)
    users = r.includes.get("users", []) if r.includes else []
    print(json.dumps(_fmt_tweet(r.data, users), indent=2))


def cmd_search(args):
    """Usage: search <query> [count]"""
    count = int(args[1]) if len(args) > 1 else 10
    r = CLIENT.search_recent_tweets(query=args[0], max_results=max(10, min(count, 100)),
                                     tweet_fields=TWEET_FIELDS,
                                     expansions=EXPANSIONS,
                                     user_fields=USER_FIELDS,
                                     user_auth=False)
    users = r.includes.get("users", []) if r.includes else []
    for t in (r.data or []):
        print(json.dumps(_fmt_tweet(t, users)))


def cmd_mentions(args):
    """Usage: mentions <user_id> [count]"""
    count = int(args[1]) if len(args) > 1 else 10
    r = CLIENT.get_users_mentions(args[0], max_results=min(count, 100),
                                   tweet_fields=TWEET_FIELDS,
                                   expansions=EXPANSIONS,
                                   user_fields=USER_FIELDS)
    users = r.includes.get("users", []) if r.includes else []
    for t in (r.data or []):
        print(json.dumps(_fmt_tweet(t, users)))


def cmd_post(args):
    """Usage: post <text>"""
    r = CLIENT.create_tweet(text=args[0])
    print(json.dumps({"id": str(r.data["id"]), "text": args[0]}))


def cmd_reply(args):
    """Usage: reply <tweet_id> <text>"""
    r = CLIENT.create_tweet(text=args[1], in_reply_to_tweet_id=args[0])
    print(json.dumps({"id": str(r.data["id"]), "reply_to": args[0], "text": args[1]}))


def cmd_like(args):
    """Usage: like <tweet_id>"""
    CLIENT.like(args[0])
    print(json.dumps({"ok": True, "liked": args[0]}))


def cmd_follow(args):
    """Usage: follow <user_id>"""
    CLIENT.follow_user(args[0])
    print(json.dumps({"ok": True, "followed": args[0]}))


def cmd_unfollow(args):
    """Usage: unfollow <user_id>"""
    CLIENT.unfollow_user(args[0])
    print(json.dumps({"ok": True, "unfollowed": args[0]}))


def cmd_usage(args):
    """Show API usage for current billing period."""
    import requests
    bt = os.environ.get("TWITTER_BEARER_TOKEN", "")
    r = requests.get("https://api.x.com/2/usage/tweets",
                      headers={"Authorization": f"Bearer {bt}"})
    d = r.json().get("data", {})
    print(json.dumps({
        "used": int(d.get("project_usage", 0)),
        "cap": int(d.get("project_cap", 0)),
        "reset_day": d.get("cap_reset_day"),
    }, indent=2))


COMMANDS = {
    "usage": cmd_usage,
    "profile": cmd_profile,
    "tweet": cmd_tweet,
    "search": cmd_search,
    "mentions": cmd_mentions,
    "post": cmd_post,
    "reply": cmd_reply,
    "like": cmd_like,
    "follow": cmd_follow,
    "unfollow": cmd_unfollow,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmds = ", ".join(COMMANDS.keys())
        print(f"Usage: x-cli.py <command> [args...]\nCommands: {cmds}")
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
