import html
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


def build_prompt() -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""
You are writing a daily Energy Aspects-style UK / France / Nordics power briefing for {today}.

Task:
Write an update-only briefing using public information from the last two days.

Strict rules:
- Do not repeat older items unless there is a new update.
- Include prices, power plant outages, interconnectors/grid availability, and policy/regulation.
- Focus on UK, France and Nordics.
- Be explicit when data is stale or not available.
- Keep a trader/analyst tone.
- Use concise tables where helpful.
- End with a bottom line.

Structure:
1) Day-ahead prices
2) Live balance / flows
3) Power plant / generation outages
4) Interconnectors / grid availability
5) Policy / regulation
6) Bottom line

Important:
Use web search to verify current information before writing.
"""


def generate_briefing() -> str:
    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input=build_prompt(),
    )

    return response.output_text


def render_html(briefing_text: str) -> str:
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    escaped_text = html.escape(briefing_text)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>UK / France / Nordics Power Briefing</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      max-width: 1050px;
      margin: 36px auto;
      padding: 0 20px;
      line-height: 1.45;
      color: #111;
      background: #fafafa;
    }}
    .card {{
      background: white;
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 26px 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}
    h1 {{
      margin-top: 0;
      margin-bottom: 6px;
      font-size: 28px;
    }}
    .meta {{
      color: #666;
      margin-bottom: 24px;
      font-size: 14px;
    }}
    pre {{
      white-space: pre-wrap;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
      margin: 0;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>UK / France / Nordics Power Briefing</h1>
    <div class="meta">Last updated: {updated}</div>
    <pre>{escaped_text}</pre>
  </div>
</body>
</html>
"""


def main() -> None:
    briefing = generate_briefing()

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    output_path = docs_dir / "index.html"
    output_path.write_text(render_html(briefing), encoding="utf-8")

    print(f"Updated {output_path}")


if __name__ == "__main__":
    main()
