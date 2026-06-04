from datetime import datetime
from zoneinfo import ZoneInfo
import config


_SOURCE_STYLES = {
    "Al Jazeera":  {"color": "#b45309", "label": "International"},
    "Daily Star":  {"color": "#1d4ed8", "label": "Bangladesh"},
    "Prothom Alo": {"color": "#15803d", "label": "Bangladesh"},
}
_DEFAULT_STYLE = {"color": "#6b21a8", "label": "News"}


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

    seen_sources: set[str] = set()
    article_cards = ""

    for i, article in enumerate(articles, start=1):
        title   = article["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        url     = article.get("url", "#")
        source  = article.get("source_name", "")
        summary = article.get("summary", "").strip()
        summary = summary.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        style   = _source_style(source)

        section_header = ""
        if source not in seen_sources:
            seen_sources.add(source)
            section_header = f"""
        <tr>
          <td style="padding: 32px 0 16px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="border-bottom: 2px solid {style['color']}; padding-bottom: 8px;">
                  <span style="
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 2.5px;
                    text-transform: uppercase;
                    color: {style['color']};
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                  ">{style['label']} &nbsp;·&nbsp; {source}</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

        summary_html = (
            f'<p style="margin: 8px 0 0; font-size: 13px; line-height: 1.7; '
            f'color: #6b7280; font-style: italic; font-family: Georgia, serif;">{summary}</p>'
            if summary else ""
        )

        image_url = article.get("image_url", "").strip()
        image_html = (
            f'<a href="{url}"><img src="{image_url}" alt="" width="100%" '
            f'style="display:block; width:100%; max-height:200px; object-fit:cover; '
            f'border-radius:4px 4px 0 0; border:0; margin-bottom:0;" /></a>'
            if image_url else ""
        )

        article_cards += f"""{section_header}
        <tr>
          <td style="padding: 0 0 12px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="
              background: #ffffff;
              border-radius: 6px;
              border: 1px solid #e5e7eb;
              box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            ">
              <tr>
                <td style="padding: 0;">
                  {image_html}
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="3" style="background: {style['color']}; width: 3px; border-radius: {'0' if image_html else '6px'} 0 0 6px;">&nbsp;</td>
                      <td style="padding: 16px 20px 16px 16px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 6px;">
                          <tr>
                            <td>
                              <span style="
                                font-size: 10px;
                                font-weight: 700;
                                letter-spacing: 1.5px;
                                text-transform: uppercase;
                                color: {style['color']};
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                              ">{source}</span>
                            </td>
                            <td align="right">
                              <span style="
                                font-size: 11px;
                                color: #d1d5db;
                                font-weight: 600;
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                              ">#{i:02d}</span>
                            </td>
                          </tr>
                        </table>
                        <a href="{url}" style="
                          display: block;
                          font-size: 15px;
                          font-weight: 700;
                          color: #111827;
                          text-decoration: none;
                          line-height: 1.5;
                          font-family: Georgia, 'Times New Roman', serif;
                        ">{title}</a>
                        {summary_html}
                        <p style="margin: 12px 0 0;">
                          <a href="{url}" style="
                            font-size: 11px;
                            font-weight: 700;
                            color: {style['color']};
                            text-decoration: none;
                            letter-spacing: 0.8px;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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

    n_sources = len(seen_sources)
    source_list = " &nbsp;·&nbsp; ".join(
        f'<span style="color:{_source_style(s)["color"]};font-weight:600;">{s}</span>'
        for s in seen_sources
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{subject}</title>
</head>
<body style="margin:0; padding:0; background:#f3f4f6; font-family: Georgia, 'Times New Roman', serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f3f4f6;">
    <tr>
      <td align="center" style="padding: 32px 12px 48px;">
        <table width="620" cellpadding="0" cellspacing="0" border="0" style="max-width:620px; width:100%;">

          <!-- MASTHEAD -->
          <tr>
            <td style="
              background: #ffffff;
              border-radius: 8px 8px 0 0;
              padding: 40px 40px 28px;
              border-bottom: 1px solid #e5e7eb;
              text-align: center;
            ">
              <p style="margin: 0 0 12px; font-size: 10px; font-weight: 700; letter-spacing: 4px; color: #9ca3af; text-transform: uppercase; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                The Daily Intelligence
              </p>
              <!-- Thin rule -->
              <table width="60" cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto 16px;">
                <tr><td style="height:1px; background:#e5e7eb; font-size:0; line-height:0;">&nbsp;</td></tr>
              </table>
              <h1 style="
                margin: 0 0 8px;
                font-size: 40px;
                font-weight: 900;
                letter-spacing: -1px;
                line-height: 1;
                color: #111827;
                font-family: Georgia, serif;
              ">Morning Brief</h1>
              <p style="margin: 0; font-size: 13px; color: #9ca3af; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: 0.3px;">
                {day_str}, {date_str}
              </p>
            </td>
          </tr>

          <!-- META BAR -->
          <tr>
            <td style="
              background: #f9fafb;
              padding: 10px 40px;
              border-bottom: 1px solid #e5e7eb;
              border-top: 0;
            ">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font-size: 11px; color: #6b7280; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                    Ranked by Gemini AI &nbsp;·&nbsp; {len(articles)} stories &nbsp;·&nbsp; {source_list}
                  </td>
                  <td align="right" style="font-size: 11px; color: #d1d5db; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; white-space: nowrap;">
                    {n_sources} sources
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ARTICLES -->
          <tr>
            <td style="background: #f9fafb; padding: 8px 28px 16px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {article_cards}
              </table>
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="
              background: #ffffff;
              border-radius: 0 0 8px 8px;
              padding: 20px 40px;
              border-top: 1px solid #e5e7eb;
              text-align: center;
            ">
              <p style="margin: 0; font-size: 11px; color: #d1d5db; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                Newspaper Agent &nbsp;·&nbsp; Auto-generated digest &nbsp;·&nbsp; {date_str}
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
