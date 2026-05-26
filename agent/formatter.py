from datetime import datetime
from zoneinfo import ZoneInfo
import config


def format_digest(articles: list[dict]) -> tuple[str, str]:
    tz = ZoneInfo(config.LOCAL_TIMEZONE)
    now = datetime.now(tz)
    date_str = now.strftime("%B %-d, %Y")
    subject = f"Morning Brief — {date_str}"

    sources = sorted({a["source_name"] for a in articles})
    sources_str = " · ".join(sources)

    article_cards = ""
    for i, article in enumerate(articles, start=1):
        title = article["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        url = article.get("url", "#")
        source = article.get("source_name", "")
        summary = article.get("summary", "").strip()
        summary = summary.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        summary_html = f'<p style="margin:8px 0 0;font-size:14px;line-height:1.5;color:#555;">{summary}</p>' if summary else ""

        article_cards += f"""
        <tr>
          <td style="padding:0 0 16px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:8px;border:1px solid #e8e8e8;">
              <tr>
                <td style="padding:16px 20px;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td style="padding:0 0 6px;">
                        <span style="display:inline-block;background:#f0f4ff;color:#3b5bdb;font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;letter-spacing:0.3px;">{source}</span>
                        <span style="font-size:11px;color:#aaa;margin-left:8px;">#{i}</span>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <a href="{url}" style="font-size:16px;font-weight:600;color:#1a1a1a;text-decoration:none;line-height:1.4;">{title}</a>
                      </td>
                    </tr>
                    <tr><td>{summary_html}</td></tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f5f5f5;">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);border-radius:12px 12px 0 0;padding:32px 32px 28px;">
              <p style="margin:0 0 4px;font-size:12px;font-weight:600;letter-spacing:2px;color:#8899bb;text-transform:uppercase;">Daily Digest</p>
              <h1 style="margin:0 0 4px;font-size:28px;font-weight:700;color:#ffffff;">Morning Brief</h1>
              <p style="margin:0;font-size:15px;color:#99aacc;">{date_str}</p>
            </td>
          </tr>

          <!-- Subheader -->
          <tr>
            <td style="background:#2d3561;padding:12px 32px;">
              <p style="margin:0;font-size:13px;color:#aabbdd;">
                Top {len(articles)} stories ranked by Gemini AI &nbsp;·&nbsp; {sources_str}
              </p>
            </td>
          </tr>

          <!-- Articles -->
          <tr>
            <td style="padding:24px 24px 8px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {article_cards}
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#1a1a2e;border-radius:0 0 12px 12px;padding:20px 32px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#667799;">
                Automated by Newspaper Agent &nbsp;·&nbsp; {date_str}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, html
