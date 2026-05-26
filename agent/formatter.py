from datetime import datetime
from zoneinfo import ZoneInfo
import config


# Map source names to accent colors and flag/icons
_SOURCE_STYLES = {
    "Al Jazeera":   {"color": "#e8b84b", "bg": "#2a2200", "label": "🌍 International"},
    "Daily Star":   {"color": "#4fc3f7", "bg": "#001a2e", "label": "🇧🇩 Bangladesh"},
}
_DEFAULT_STYLE = {"color": "#a78bfa", "bg": "#1a0a2e", "label": "📰 News"}


def _source_style(source_name: str) -> dict:
    for key, style in _SOURCE_STYLES.items():
        if key.lower() in source_name.lower():
            return style
    return _DEFAULT_STYLE


def format_digest(articles: list[dict]) -> tuple[str, str]:
    tz = ZoneInfo(config.LOCAL_TIMEZONE)
    now = datetime.now(tz)
    date_str = now.strftime("%B %-d, %Y")
    day_str = now.strftime("%A")
    subject = f"Morning Brief — {date_str}"

    # Group articles by source for section headers
    seen_sources: set[str] = set()
    article_cards = ""

    for i, article in enumerate(articles, start=1):
        title   = article["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        url     = article.get("url", "#")
        source  = article.get("source_name", "")
        summary = article.get("summary", "").strip()
        summary = summary.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        style   = _source_style(source)

        # Section divider when source changes
        section_header = ""
        if source not in seen_sources:
            seen_sources.add(source)
            section_header = f"""
        <tr>
          <td style="padding: 8px 0 12px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="border-top: 1px solid #2a2a3a; padding-top: 20px;">
                  <span style="
                    display: inline-block;
                    background: {style['bg']};
                    color: {style['color']};
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    padding: 4px 12px;
                    border-radius: 2px;
                    border-left: 3px solid {style['color']};
                  ">{style['label']}</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

        summary_html = (
            f'<p style="margin: 8px 0 0; font-size: 13px; line-height: 1.65; '
            f'color: #8899aa; font-style: italic;">{summary}</p>'
            if summary else ""
        )

        image_url = article.get("image_url", "").strip()
        image_html = (
            f'<a href="{url}"><img src="{image_url}" alt="" width="100%" '
            f'style="display:block; width:100%; max-height:220px; object-fit:cover; '
            f'border-radius:5px 5px 0 0; border:0;" /></a>'
            if image_url else ""
        )

        article_cards += f"""{section_header}
        <tr>
          <td style="padding: 0 0 2px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="
              background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
              border-radius: 6px;
              border: 1px solid #1e293b;
              margin-bottom: 10px;
            ">
              <tr>
                <td style="padding: 0;">
                  {image_html}
                  <!-- Left accent bar -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="3" style="background: {style['color']}; border-radius: {'0' if image_html else '6px'} 0 0 6px; width: 3px;">&nbsp;</td>
                      <td style="padding: 16px 20px 16px 16px;">
                        <!-- Source + Number row -->
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 8px;">
                          <tr>
                            <td>
                              <span style="
                                font-size: 10px;
                                font-weight: 700;
                                letter-spacing: 1.5px;
                                text-transform: uppercase;
                                color: {style['color']};
                              ">{source}</span>
                            </td>
                            <td align="right">
                              <span style="
                                font-size: 11px;
                                color: #334155;
                                font-weight: 600;
                              ">#{i:02d}</span>
                            </td>
                          </tr>
                        </table>
                        <!-- Headline -->
                        <a href="{url}" style="
                          display: block;
                          font-size: 15px;
                          font-weight: 700;
                          color: #e2e8f0;
                          text-decoration: none;
                          line-height: 1.5;
                          letter-spacing: -0.1px;
                        ">{title}</a>
                        {summary_html}
                        <!-- Read more -->
                        <p style="margin: 12px 0 0;">
                          <a href="{url}" style="
                            font-size: 11px;
                            font-weight: 600;
                            color: {style['color']};
                            text-decoration: none;
                            letter-spacing: 0.5px;
                          ">READ STORY →</a>
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    # Stats bar
    n_sources = len(seen_sources)
    source_list = " &nbsp;|&nbsp; ".join(
        f'<span style="color:{_source_style(s)["color"]}">{s}</span>'
        for s in seen_sources
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{subject}</title>
</head>
<body style="margin:0; padding:0; background:#060b14; font-family: Georgia, 'Times New Roman', serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#060b14;">
    <tr>
      <td align="center" style="padding: 28px 12px 40px;">
        <table width="620" cellpadding="0" cellspacing="0" border="0" style="max-width:620px; width:100%;">

          <!-- ═══ MASTHEAD ═══ -->
          <tr>
            <td style="
              background: linear-gradient(160deg, #0a0f1e 0%, #050a14 60%, #0d0820 100%);
              border-radius: 10px 10px 0 0;
              padding: 36px 36px 28px;
              border-bottom: 1px solid #1e293b;
              position: relative;
            ">
              <!-- Decorative top rule -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
                <tr>
                  <td style="height: 1px; background: linear-gradient(90deg, transparent, #e8b84b 30%, #4fc3f7 70%, transparent); font-size:0; line-height:0;">&nbsp;</td>
                </tr>
              </table>

              <!-- Brand -->
              <p style="margin: 0 0 6px; font-size: 10px; font-weight: 700; letter-spacing: 5px; color: #4a5568; text-transform: uppercase; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                ✦ &nbsp; The Daily Intelligence &nbsp; ✦
              </p>
              <h1 style="
                margin: 0 0 4px;
                font-size: 42px;
                font-weight: 900;
                letter-spacing: -1.5px;
                line-height: 1;
                font-family: Georgia, serif;
              ">
                <span style="color: #e8b84b;">Morning</span>
                <span style="color: #f1f5f9;"> Brief</span>
              </h1>
              <p style="margin: 8px 0 0; font-size: 14px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: 0.3px;">
                {day_str}, {date_str} &nbsp;·&nbsp; Asia/Dhaka
              </p>

              <!-- Bottom rule -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 20px;">
                <tr>
                  <td style="height: 1px; background: linear-gradient(90deg, transparent, #e8b84b 30%, #4fc3f7 70%, transparent); font-size:0; line-height:0;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ═══ META BAR ═══ -->
          <tr>
            <td style="
              background: #080d1a;
              padding: 10px 36px;
              border-bottom: 1px solid #1e293b;
            ">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font-size: 11px; color: #475569; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: 0.3px;">
                    🤖 &nbsp;Ranked by Gemini AI &nbsp;·&nbsp; {len(articles)} stories &nbsp;·&nbsp; {source_list}
                  </td>
                  <td align="right" style="font-size: 11px; color: #334155; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; white-space: nowrap;">
                    {n_sources} sources
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ═══ ARTICLES ═══ -->
          <tr>
            <td style="background: #080d1a; padding: 24px 28px 16px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {article_cards}
              </table>
            </td>
          </tr>

          <!-- ═══ FOOTER ═══ -->
          <tr>
            <td style="
              background: #050912;
              border-radius: 0 0 10px 10px;
              padding: 20px 36px;
              border-top: 1px solid #1e293b;
            ">
              <!-- Thin rule -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 16px;">
                <tr>
                  <td style="height: 1px; background: linear-gradient(90deg, transparent, #1e293b, transparent); font-size:0; line-height:0;">&nbsp;</td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font-size: 11px; color: #334155; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                    Newspaper Agent &nbsp;·&nbsp; Auto-generated digest
                  </td>
                  <td align="right" style="font-size: 11px; color: #1e293b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                    {date_str}
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""

    return subject, html
