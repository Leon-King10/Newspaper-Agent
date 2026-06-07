# 🗞️ Newspaper Agent

**Your daily news, read and summarized for you — delivered to your inbox twice a day.**

Newspaper Agent is an autonomous AI assistant that reads the news so you don't have to. It runs twice daily, gathers the latest headlines, picks the stories that matter, writes a clear summary of each one, and emails you a clean, beautifully designed digest — automatically, with nothing for you to check or open.

---

## Why we built it

Staying informed takes time most people don't have. Between dozens of news sites, endless scrolling, and clickbait headlines, simply *finding out what happened* has become a chore.

Newspaper Agent solves that. Instead of you visiting multiple news sites every day, one assistant does the reading and hands you the essentials — a morning briefing and a night briefing that cover **Bangladesh**, **sports**, and the **wider world**, with balanced representation across each. No apps, no dashboards, no noise.

---

## What you get

Twice a day, a single email lands in your inbox containing:

- **The most important stories**, chosen by AI from international, Bangladeshi, and sports news — never stale or recycled articles.
- **A short, clear summary of each story**, written in plain language so you understand what happened at a glance — no need to click through.
- **The original article image and a one-click link**, in case you want the full story.
- **A balanced view** — equal slots given to each source, so you never see only one angle.
- **A polished, easy-to-read design** that feels like a premium newspaper, not a wall of text.

The result: you stay genuinely informed in about two minutes, twice a day, without lifting a finger.

---

## How the automation works

The whole thing runs by itself. Each run, behind the scenes, the assistant:

1. **Gathers** the latest headlines from four trusted sources.
2. **Filters by time window** — the morning brief covers the previous 24 hours; the night brief covers articles published since 9 AM that same day. You only ever see fresh news.
3. **Selects the best stories** using AI, giving equal space to each source.
4. **Summarizes each one** into a crisp, readable brief.
5. **Designs and sends** the finished digest straight to your inbox.

You do nothing. The news simply arrives, ready to read.

---

## The sources

| Source | Coverage |
|---|---|
| **Al Jazeera** | International news |
| **The Daily Star** | Bangladesh news |
| **Prothom Alo** | Bangladesh news (Bengali) |
| **Prothom Alo Sports** | Sports news (Bengali) |

Each digest gives **equal representation** to every source — 5 stories per source, 20 stories total.

---

## Schedule

| Edition | Local Time (Asia/Dhaka) | What it covers |
|---|---|---|
| **Morning Brief** | ~8:42 AM | Previous day's news (yesterday 9 AM → today 9 AM) |
| **Night Brief** | ~7:12 PM | Today's news published since 9 AM |

---

## Configuration

All settings are in `config.py`. Key variables:

| Variable | Default | Purpose |
|---|---|---|
| `TOP_N` | `20` | Total articles per digest (4 sources × 5 each) |
| `ARTICLES_PER_SOURCE` | `15` | Max articles fetched per source before ranking |
| `NEWS_WINDOW_START_HOUR` | `9` | Hour (local) that separates morning and night windows |
| `LOCAL_TIMEZONE` | `Asia/Dhaka` | Timezone for all time calculations |
| `GEMINI_MODEL` | `gemini-2.5-flash` | AI model used for ranking and summarization |

Environment variables required (set as GitHub Secrets):

| Variable | Purpose |
|---|---|
| `SENDER_EMAIL` | Gmail address used to send digests |
| `SENDER_APP_PASSWORD` | Gmail App Password |
| `RECIPIENT_EMAILS` | Comma-separated list of recipient addresses |
| `GEMINI_API_KEY` | Google Gemini API key |

---

*Built by Samiul Azim. Private and proprietary — all rights reserved.*
