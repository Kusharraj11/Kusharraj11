"""Generate the public profile README and local SVG assets.

Only the Python standard library is used so this can run in GitHub Actions
without installing dependencies.
"""

from __future__ import annotations

import base64
import json
import os
import textwrap
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "profile" / "source" / "profile.md"
GENERATED = ROOT / "profile" / "assets" / "generated"
PORTRAIT = ROOT / "profile" / "assets" / "portrait" / "source"
FONT = ROOT / "profile" / "assets" / "fonts" / "profile-font.woff2"
USERNAME = os.environ.get("GITHUB_USERNAME", "Kusharraj11")


def github_json(url: str, token: str | None) -> object | None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-generator"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def contribution_count(token: str | None) -> int | None:
    if not token:
        return None
    query = {
        "query": """query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar { totalContributions }
            }
          }
        }""",
        "variables": {"login": USERNAME},
    }
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(query).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-generator",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.load(response)
        return int(result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"])
    except (KeyError, TypeError, ValueError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def collect_stats() -> tuple[int, int, list[tuple[str, int]]]:
    token = os.environ.get("GITHUB_TOKEN")
    repos = github_json(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner",
        token,
    )
    if not isinstance(repos, list):
        return 0, 0, []
    languages: Counter[str] = Counter()
    for repo in repos:
        if not isinstance(repo, dict) or repo.get("fork"):
            continue
        language_data = github_json(str(repo.get("languages_url", "")), token)
        if isinstance(language_data, dict):
            for language, bytes_count in language_data.items():
                if isinstance(bytes_count, int):
                    languages[str(language)] += bytes_count
    return len(repos), contribution_count(token) or 0, sorted(
        languages.items(), key=lambda pair: (-pair[1], pair[0])
    )


def font_css() -> str:
    if not FONT.exists():
        return ""
    encoded = base64.b64encode(FONT.read_bytes()).decode("ascii")
    return f"@font-face{{font-family:'ProfileEmbedded';src:url(data:font/woff2;base64,{encoded}) format('woff2');}}"


def stats_svg(repo_count: int, activity: int, languages: list[tuple[str, int]]) -> str:
    total = sum(value for _, value in languages) or 1
    palette = ["#58a6ff", "#bc8cff", "#3fb950", "#f0883e", "#f778ba", "#d29922"]
    rows = []
    for index, (language, value) in enumerate(languages[:6]):
        width = round(420 * value / total)
        rows.append(
            f'<text x="24" y="{105 + index * 30}" fill="#c9d1d9">{language}</text>'
            f'<rect x="125" y="{91 + index * 30}" width="{width}" height="16" rx="8" fill="{palette[index % len(palette)]}"/>'
            f'<text x="{570}" y="{105 + index * 30}" fill="#8b949e" text-anchor="end">{value / total:.0%}</text>'
        )
    if not rows:
        rows.append('<text x="24" y="105" fill="#8b949e">No public language data yet</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="620" height="260" role="img" aria-label="GitHub public activity and language statistics">
<style>{font_css()}text{{font-family:'ProfileEmbedded','JetBrains Mono',monospace;font-size:14px}}.label{{font-size:13px;fill:#8b949e}}</style>
<rect width="620" height="260" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="24" y="32" fill="#f0f6fc" font-size="18" font-weight="700">Public GitHub snapshot</text>
<text x="24" y="60" class="label">{repo_count} repositories · {activity} contributions (calendar when authenticated)</text>
<text x="24" y="82" class="label">Languages by reported bytes</text>
{''.join(rows)}
</svg>
"""


def read_pgm() -> list[str]:
    for suffix in ("pgm", "ppm"):
        path = PORTRAIT / f"portrait.{suffix}"
        if path.exists():
            return path.read_text(encoding="ascii", errors="ignore").split()
    return []


def portrait_svg() -> str:
    tokens = read_pgm()
    art = ["  /\\_/\\\\", " ( o.o )", "  > ^ < "]
    if tokens:
        art = ["  [ portrait input detected ]", "  ASCII conversion ready", "  replace source to refresh"]
    frames = []
    for offset in (0, 1):
        lines = "\n".join(
            f'<text x="34" y="{68 + index * 24}" fill="#58a6ff">{textwrap.shorten(line[offset:], 32, placeholder="")}</text>'
            for index, line in enumerate(art)
        )
        frames.append(f"<g opacity=\"{1 if offset == 0 else 0}\"><animate attributeName=\"opacity\" values=\"{1 if offset == 0 else 0};{0 if offset == 0 else 1};{1 if offset == 0 else 0}\" dur=\"1.6s\" repeatCount=\"indefinite\"/>{lines}</g>")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="260" height="150" role="img" aria-label="Animated ASCII portrait placeholder">
<style>{font_css()}text{{font-family:'ProfileEmbedded','JetBrains Mono',monospace;font-size:18px}}</style>
<rect width="260" height="150" rx="14" fill="#0d1117" stroke="#30363d"/>
{''.join(frames)}
</svg>
"""


def build_readme(repo_count: int, activity: int) -> str:
    source = SOURCE.read_text(encoding="utf-8").rstrip()
    generated = """<!-- Generated by scripts/generate_profile.py. Edit profile/source/profile.md instead. -->

<p align="center">
  <img src="profile/assets/generated/portrait.svg" width="260" alt="Animated ASCII portrait placeholder">
</p>

<p align="center">
  <img src="profile/assets/generated/stats.svg" alt="Public GitHub statistics">
</p>

_Generated snapshot: {repo_count} public repositories and {activity} public contributions (calendar when authenticated)._

""".format(repo_count=repo_count, activity=activity)
    return generated + source + "\n"


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    repo_count, activity, languages = collect_stats()
    (GENERATED / "stats.svg").write_text(stats_svg(repo_count, activity, languages), encoding="utf-8")
    (GENERATED / "portrait.svg").write_text(portrait_svg(), encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(repo_count, activity), encoding="utf-8")


if __name__ == "__main__":
    main()
