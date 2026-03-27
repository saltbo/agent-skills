#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tweepy"]
# ///
"""Supplementary CLI for X operations not covered by the MCP server."""

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
)

MY_ID = "726438383401074688"


def cmd_follow(args):
    """Follow a user. Usage: follow <user_id>"""
    if not args:
        print("Usage: x-cli.py follow <user_id>")
        sys.exit(1)
    CLIENT.follow_user(args[0])
    print(json.dumps({"ok": True, "followed": args[0]}))


def cmd_unfollow(args):
    """Unfollow a user. Usage: unfollow <user_id>"""
    if not args:
        print("Usage: x-cli.py unfollow <user_id>")
        sys.exit(1)
    CLIENT.unfollow_user(args[0])
    print(json.dumps({"ok": True, "unfollowed": args[0]}))


COMMANDS = {
    "follow": cmd_follow,
    "unfollow": cmd_unfollow,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: x-cli.py <command> [args...]")
        print(f"Commands: {', '.join(COMMANDS.keys())}")
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
