# 🗞️ Newspaper Agent

> **An autonomous AI-powered daily news digest system** that scrapes top headlines from international and Bangladeshi news sources, ranks them with Google Gemini AI, generates professional summaries, and delivers a beautifully designed HTML email — fully automated, every morning.

---

## ✨ What It Does

Every day at **9:00 AM (Bangladesh Time)**, this system:

1. 📡 **Fetches** the latest headlines from Al Jazeera and The Daily Star via RSS
2. 🖼️ **Scrapes** the actual thumbnail image from each article page
3. 🤖 **Ranks** the top 5 stories from each source using **Google Gemini 3.5 Flash AI**
4. ✍️ **Writes** a crisp 2-sentence AI summary for every selected article
5. 🎨 **Formats** a premium dark-themed HTML email with images, source badges, and color-coded sections
6. 📬 **Delivers** the digest to all configured recipient inboxes

No dashboards to check. No apps to open. The news comes to you.

---

## 📸 Email Preview

The digest email features:
- A **premium dark newspaper aesthetic** inspired by high-end editorial design
- **Gold accents** for international news (Al Jazeera) and **cyan accents** for Bangladeshi news (Daily Star)
- **Article thumbnail images** pulled directly from each news source
- **AI-written 2-sentence summaries** for every story — not just raw RSS descriptions
- A `READ STORY →` link on every card for one-click access

---

## 🗂️ Project Structure

```
Newspaper Agent/
│
├── main.py                  # Entry point — orchestrates the 5-step pipeline
├── config.py                # Environment variable loading & news source definitions
├── requirements.txt         # Python dependencies
│
├── agent/
│   ├── scraper.py           # RSS fetching + parallel og:image extraction
│   ├── ranker.py            # Gemini AI article ranking (equal split per source)
│   ├── summarizer.py        # Gemini AI batch summary generation
│   ├── formatter.py         # Premium HTML email template builder
│   └── sender.py            # Gmail SMTP delivery
│
└── .github/
    └── workflows/
        └── daily_news.yml   # GitHub Actions — runs every day at 9 AM BST
```

---

## ⚙️ How It Works (Technical Pipeline)

```
RSS Feeds
    │
    ▼
[scraper.py]  ──── feedparser + parallel requests ────▶  25 raw articles
                   (og:image scraped for each)

    │
    ▼
[ranker.py]   ──── Gemini 3.5 Flash (×2 calls) ────────▶  Top 10 articles
                   5 from Al Jazeera
                   5 from Daily Star

    │
    ▼
[summarizer.py] ── Gemini 3.5 Flash (×1 batch call) ──▶  AI summaries for all 10

    │
    ▼
[formatter.py]  ── HTML template engine ───────────────▶  Styled email HTML

    │
    ▼
[sender.py]     ── Gmail SMTP (smtplib) ────────────────▶  📬 Delivered
```

---

## 🚀 Setup Guide

### Prerequisites
- Python 3.11+
- A Gmail account (used as the sender — not your primary email)
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/Leon-King10/Newspaper-Agent.git
cd Newspaper-Agent
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in the values:

```env
SENDER_EMAIL=your.sender@gmail.com
SENDER_APP_PASSWORD=xxxx xxxx xxxx xxxx
RECIPIENT_EMAILS=first@gmail.com,second@gmail.com
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.5-flash
LOCAL_TIMEZONE=Asia/Dhaka
```

> **⚠️ Never commit your `.env` file.** It is already listed in `.gitignore`.

#### Getting Your Gmail App Password
1. Go to [myaccount.google.com](https://myaccount.google.com) → **Security**
2. Enable **2-Step Verification** if not already on
3. Search for **"App passwords"**
4. Create one — select *Mail* and *Other (custom name)* → type `Newspaper Agent`
5. Copy the 16-character password into `SENDER_APP_PASSWORD`

### 5. Run Manually

```bash
python main.py
```

You should see the full 5-step pipeline log and receive the email within ~60 seconds.

---

## 🤖 Automation — GitHub Actions

The system runs automatically every day at **9:00 AM Bangladesh Time (3:00 AM UTC)** via GitHub Actions. It can also be triggered manually from the **Actions tab** in GitHub.

### Setting Up Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name | Value |
|---|---|
| `SENDER_EMAIL` | Your sender Gmail address |
| `SENDER_APP_PASSWORD` | The 16-character Gmail App Password |
| `RECIPIENT_EMAILS` | Comma-separated recipient emails |
| `GEMINI_API_KEY` | Your Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-3.5-flash` |

Once secrets are set, every morning the GitHub-hosted runner will execute the full pipeline at no cost (within GitHub's free tier limits).

---

## 📰 News Sources

Currently configured in `config.py`:

| Source | Coverage | Articles Fetched | AI-Selected |
|---|---|---|---|
| **Al Jazeera** | International news | 15 | Top 5 |
| **The Daily Star** | Bangladesh news | 10 | Top 5 |

The system is designed for **equal representation** — exactly 50% international, 50% Bangladeshi news in every digest.

### Adding a New Source

Open `config.py` and add a new entry to `NEWS_SOURCES`:

```python
{
    "name": "Prothom Alo",
    "rss_url": "https://www.prothomalo.com/feed",
    "site_url": "https://www.prothomalo.com/",
    "enabled": True,
},
```

The ranker automatically recalculates the equal-slot split when a new source is added. With 3 sources and `TOP_N = 10`, it would be ~3-4 articles per source.

---

## 🔧 Configuration Reference

All settings live in `config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `SENDER_EMAIL` | *(required)* | Gmail address used to send |
| `SENDER_APP_PASSWORD` | *(required)* | Gmail App Password |
| `RECIPIENT_EMAILS` | *(required)* | Comma-separated recipients |
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model to use |
| `LOCAL_TIMEZONE` | `Asia/Dhaka` | Timezone shown in email header |
| `TOP_N` | `10` | Total articles in each digest |
| `ARTICLES_PER_SOURCE` | `15` | Max articles fetched per source |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `feedparser` | Parses RSS feeds from news sources |
| `requests` + `beautifulsoup4` | Fetches article pages to extract `og:image` |
| `google-genai` | Google Gemini AI SDK for ranking & summarization |
| `python-dotenv` | Loads `.env` file into environment |
| `newspaper3k` | HTML fallback scraper (if RSS fails) |
| `lxml` / `lxml_html_clean` | HTML parsing dependencies |

---

## 🛡️ Security Notes

- Credentials are stored as **GitHub Secrets** — never in the codebase
- The `.env` file is excluded from git via `.gitignore`
- Gmail App Passwords are scoped to this app only and can be revoked at any time
- The sender email is a dedicated non-primary account — your main Gmail is never exposed

---

## 🗺️ Roadmap / Possible Enhancements

- [ ] Add more Bangladeshi sources (Prothom Alo, bdnews24, The Business Standard)
- [ ] WhatsApp delivery via CallMeBot in addition to email
- [ ] Topic filtering (e.g., only business, only sports)
- [ ] Weekly digest mode
- [ ] Web dashboard to view past digests
- [ ] Sentiment analysis per article

---

## 👤 Author

**Samiul Azim**  
Built with Python, Google Gemini AI, and GitHub Actions.

---

*This project is private and proprietary. All rights reserved.*
