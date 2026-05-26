# Switch Delivery to Gmail HTML Emails

This plan outlines replacing the unreliable CallMeBot WhatsApp integration with a robust, custom-styled HTML email sent every day via a Gmail account. 

## User Review Required

> [!WARNING]
> **Gmail Configuration:** Sending emails via a script requires you to enable **2-Step Verification** on your Google Account and generate an **App Password**. You cannot use your regular Gmail password. Are you comfortable with setting this up? (I will provide exact step-by-step instructions once we begin).

## Open Questions

> [!IMPORTANT]
> Since emails don't have strict character limits like WhatsApp bots, would you like me to include a **1-2 sentence AI summary** of each article in the email? (The scraper already has the article content, we just need to pass it to the AI ranker to summarize). If not, we can just stick to Titles and Links.

## Proposed Changes

---

### Configuration & Environment 

We will remove the CallMeBot variables and add Gmail variables.

#### [MODIFY] [config.py](file:///Users/samiulazim/Documents/Antigravity%20Folders/Newspaper%20Agent/config.py)
- Remove `RECIPIENT_PHONE` and `CALLMEBOT_API_KEY`.
- Add `SENDER_EMAIL`, `SENDER_APP_PASSWORD`, and `RECIPIENT_EMAIL`.

#### [MODIFY] [.env.example](file:///Users/samiulazim/Documents/Antigravity%20Folders/Newspaper%20Agent/.env.example)
- Remove WhatsApp instructions.
- Add clear instructions on how to generate a Gmail App Password and set the new environment variables.

---

### Delivery System

We will rewrite the sender module to use Python's built-in `smtplib` and `email` libraries.

#### [MODIFY] [agent/sender.py](file:///Users/samiulazim/Documents/Antigravity%20Folders/Newspaper%20Agent/agent/sender.py)
- Remove `requests` code targeting CallMeBot.
- Create `send_email(subject: str, html_content: str)` function.
- Connect to `smtp.gmail.com` over SSL and authenticate with the App Password.
- Construct and send an `EmailMessage` with HTML formatting.

#### [MODIFY] [agent/formatter.py](file:///Users/samiulazim/Documents/Antigravity%20Folders/Newspaper%20Agent/agent/formatter.py)
- Update `format_digest` to return a `(subject, html_body)` tuple.
- Generate a beautifully styled HTML string with inline CSS.
- Include clickable hyperlinks directly to the articles.
- Remove the 1500 character truncation limit since emails can be longer.

#### [MODIFY] [main.py](file:///Users/samiulazim/Documents/Antigravity%20Folders/Newspaper%20Agent/main.py)
- Change import from `send_whatsapp` to `send_email`.
- Pass the generated subject and HTML to the email sender.

## Verification Plan

### Manual Verification
- Provide instructions to the user on how to generate their Gmail App Password.
- The user will update their `.env` file.
- The user will run `python main.py` locally.
- Confirm that the user receives the beautifully formatted HTML email in their inbox.
