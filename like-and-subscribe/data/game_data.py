# data/game_data.py

PLATFORMS = {
    "Mux": {
        "preferred": ["Hot Take", "Meme"],
        "risk_event": "Community Note",
    },
    "SnoozeTube": {
        "preferred": ["Tutorial", "Short"],
        "risk_event": "Copyright Strike",
    },
    "Shrubshack": {
        "preferred": ["Essay"],
        "risk_event": "Algorithm Nerf",
    },
    "CrikCrok": {
        "preferred": ["Reel", "Livestream"],
        "risk_event": "Platform Shut Down",
    },
    "BootHead": {
        "preferred": ["Meme", "Livestream"],
        "risk_event": "Shadowban",
    },
    "Randogram": {
        "preferred": ["Reel", "Meme"],
        "risk_event": "Format Change",
    },
    "Oldbird": {
        "preferred": ["Essay", "Joke"],
        "risk_event": "Platform Outage",
    }
}

CONTENT_TYPES = {
    "Meme": {"energy": 1, "base_followers": 100},
    "Hot Take": {"energy": 1, "base_followers": 200, "risk": True},
    "Tutorial": {"energy": 2, "base_followers": 150},
    "Essay": {"energy": 2, "base_followers": 100},
    "Livestream": {"energy": 2, "base_followers": 180},
    "Reel": {"energy": 1, "base_followers": 160},
    "Short": {"energy": 1, "base_followers": 140},
    "Joke": {"energy": 1, "base_followers": 90}
}

DEFAULT_GAME_LENGTHS = {
    "Quick Grind": 14,
    "Standard Career": 30,
    "Influencer Marathon": 60
}

# Sample news events with dynamic tracking
NEWS_EVENTS = [
    {
        "headline": "Short-form videos get global spotlight",
        "platform": "SnoozeTube",
        "content_type": "Shorts",
        "duration": 2,
        "multiplier": 1.6
    },
    {
        "headline": "Mux trending tab favors Hot Takes",
        "platform": "Mux",
        "content_type": "Hot Takes",
        "duration": 2,
        "multiplier": 1.5
    },
    {
        "headline": "BootHead promoting Livestreams",
        "platform": "BootHead",
        "content_type": "Livestreams",
        "duration": 2,
        "multiplier": 1.4
    },
    {
        "headline": "Randogram starts Meme contest",
        "platform": "Randogram",
        "content_type": "Memes",
        "duration": 2,
        "multiplier": 1.5
    },
    {
        "headline": "Essays featured on Oldbird home feed",
        "platform": "Oldbird",
        "content_type": "Essays",
        "duration": 2,
        "multiplier": 1.7
    },
    {
        "headline": "Shrubshack launches discovery page",
        "platform": "Shrubshack",
        "content_type": "Essays",
        "duration": 2,
        "multiplier": 1.6
    },
    {
        "headline": "CrikCrok disables Reels tab in U.S.",
        "platform": "CrikCrok",
        "content_type": "Reels",
        "duration": 2,
        "multiplier": 0.5,
        "type": "detriment"
    },
    {
        "headline": "BootHead rollout causes Memes to vanish",
        "platform": "BootHead",
        "content_type": "Memes",
        "duration": 2,
        "multiplier": 0.6,
        "type": "detriment"
    },
    {
        "headline": "Old controversial post resurfaces",
        "platform": None,
        "content_type": None,
        "duration": 1,
        "follower_loss_percent": 0.25,
        "type": "detriment"
    },
    {
        "headline": "Shrubshack flags Tutorials as spam",
        "platform": "Shrubshack",
        "content_type": "Tutorials",
        "duration": 2,
        "multiplier": 0.4,
        "type": "detriment"
    }
]

