#!/usr/bin/env python3
"""Draw the profile's daily contribution candles and refresh the README's generated sections.

The chart follows a momentum level that climbs quickly with each day's contributions and eases off slowly
on quiet days. Each candle runs from the previous day's level to the new one, its wick reaches towards
the day's count, and the bars below are the raw daily counts. Both use a square-root scale, so one heavy
day does not flatten the rest. Private work appears only as the anonymous daily counts the public
profile already shows, because the workflow runs with the repository's own token.
"""

from __future__ import annotations

import json
import math
import os
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
LOGIN = os.environ.get("PROFILE_LOGIN", "TrevorAntony")
DAYS = 120
RISE = 0.6
FALL = 0.3
API = "https://api.github.com/graphql"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
QUERY = """
query($login: String!, $merged: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } }
  }
  search(query: $merged, type: ISSUE, first: 100) {
    issueCount
    nodes { ... on PullRequest { repository { nameWithOwner url isPrivate } } }
  }
}
"""
REST = "https://api.github.com"
MARKERS = {"open-source": ("<!-- open-source:start -->", "<!-- open-source:end -->")}


@dataclass(frozen=True)
class Theme:
    ink: str
    fg: str
    muted: str
    grid: str
    up: str
    down: str
    average: str


DARK = Theme(ink="#0d1117", fg="#e6edf3", muted="#8b949e", grid="rgba(240,246,252,0.08)", up="#3fb950", down="#f85149", average="#d29922")
LIGHT = Theme(ink="#ffffff", fg="#1f2328", muted="#59636e", grid="rgba(31,35,40,0.08)", up="#1a7f37", down="#cf222e", average="#9a6700")


@dataclass(frozen=True)
class Candle:
    on: date
    count: int
    open: float
    close: float
    high: float
    low: float

    @property
    def up(self) -> bool:
        return self.close >= self.open


def fetch(token: str) -> dict:
    variables = {"login": LOGIN, "merged": f"author:{LOGIN} is:pr is:merged is:public"}
    request = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-chart"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


def days_of(calendar: dict) -> list[tuple[date, int]]:
    return sorted((date.fromisoformat(d["date"]), d["contributionCount"]) for w in calendar["weeks"] for d in w["contributionDays"])


def candles_of(days: list[tuple[date, int]]) -> list[Candle]:
    level, candles = 0.0, []
    for on, count in days:
        rate = RISE if count > level else FALL
        new = level + (count - level) * rate
        reach = (count - max(level, new)) * 0.35 if count > max(level, new) else 0.0
        candles.append(Candle(on=on, count=count, open=level, close=new, high=max(level, new) + reach, low=min(level, new) * (0.94 if count == 0 else 1)))
        level = new
    return candles


def streaks(calendar: dict) -> tuple[int, int]:
    counts = [d["contributionCount"] for w in calendar["weeks"] for d in w["contributionDays"]]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):
        if not c:
            break
        current += 1
    return longest, current


def svg(candles: list[Candle], total_year: int, longest: int, current: int, theme: Theme, width: int = 880, days: int = DAYS) -> str:
    shown, before = candles[-days:], candles[-2 * days : -days]
    narrow = width < 600
    height = 360 if narrow else 330
    left, right = 44, 16
    top = 112 if narrow else 82
    price_bottom, volume_top, volume_bottom = top + 140, top + 154, top + 208
    step = (width - left - right) / len(shown)
    body = max(2.0, step * 0.62)
    ceiling = _nice(max(c.high for c in shown))
    y = lambda v: price_bottom - (price_bottom - top) * math.sqrt(max(v, 0) / ceiling)
    vol_ceiling = max(1, max(c.count for c in shown))
    vy = lambda v: volume_bottom - (volume_bottom - volume_top) * math.sqrt(v / vol_ceiling)
    x = lambda i: left + step * (i + 0.5)
    now, then = sum(c.count for c in shown), sum(c.count for c in before)
    change = f"{(now - then) / then:+.0%}" if then else "new"
    headline = f"{now:,}"
    right_x, right_y = (left, 84) if narrow else (width - right, 30)
    anchor = "start" if narrow else "end"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
        f'aria-label="Daily contribution candles for {LOGIN} over the last {days} days">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{theme.ink}"/>',
        f'<g font-family="{FONT}">',
        f'<text x="{left}" y="30" font-size="12" fill="{theme.muted}" letter-spacing="1.5">CONTRIBUTIONS · LAST {days} DAYS</text>',
        f'<text x="{left}" y="60" font-size="28" font-weight="600" fill="{theme.fg}">{headline}</text>',
        f'<text x="{left + 18 + 16.8 * len(headline):.0f}" y="60" font-size="13" fill="{theme.up if now >= then else theme.down}">{change} vs the {days} days before</text>',
        f'<text x="{right_x}" y="{right_y}" font-size="12" fill="{theme.muted}" text-anchor="{anchor}">{total_year:,} in the last year · longest streak {longest} d · current {current} d</text>',
    ]
    for frac in (0, 0.25, 1):
        v = ceiling * frac
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{theme.grid}"/>')
        parts.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" font-size="10" fill="{theme.muted}" text-anchor="end">{v:g}</text>')
    parts.append(f'<text x="{left - 8}" y="{volume_top + 8}" font-size="10" fill="{theme.muted}" text-anchor="end">day</text>')
    for i, c in enumerate(shown):
        color = theme.up if c.up else theme.down
        top_y, bottom_y = y(max(c.open, c.close)), y(min(c.open, c.close))
        parts.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{y(c.high):.1f}" y2="{y(c.low):.1f}" stroke="{color}" stroke-width="1"/>')
        parts.append(
            f'<rect x="{x(i) - body / 2:.1f}" y="{top_y:.1f}" width="{body:.1f}" height="{max(1.2, bottom_y - top_y):.1f}" fill="{color}">'
            f"<title>{c.on:%a %d %b}: {c.count} contributions</title></rect>"
        )
        if c.count:
            parts.append(f'<rect x="{x(i) - body / 2:.1f}" y="{vy(c.count):.1f}" width="{body:.1f}" height="{volume_bottom - vy(c.count):.1f}" fill="{color}" opacity="0.4"/>')
        if c.on.day == 1:
            parts.append(f'<text x="{x(i):.1f}" y="{height - 16}" font-size="10" fill="{theme.muted}" text-anchor="middle">{c.on:%b}</text>')
    weekly = [mean(k.count for k in candles[len(candles) - days + i - 6 : len(candles) - days + i + 1]) for i in range(len(shown))]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(a):.1f}" for i, a in enumerate(weekly))
    parts.append(f'<path d="{path}" fill="none" stroke="{theme.average}" stroke-width="1.4" stroke-linejoin="round" opacity="0.9"/>')
    parts.append(f'<text x="{width - right}" y="{top - 10}" font-size="10" fill="{theme.average}" text-anchor="end">7-day average</text>')
    parts.append("</g></svg>")
    return "\n".join(parts)


def _nice(value: float) -> float:
    for power in range(0, 6):
        for base in (1, 2, 2.5, 5):
            candidate = base * 10**power
            if candidate >= value:
                return candidate
    return value


def open_source_section(search: dict) -> str:
    counts: dict[str, tuple[str, int]] = {}
    for node in search["nodes"]:
        repo = node.get("repository") or {}
        if not repo or repo.get("isPrivate"):
            continue
        name = repo["nameWithOwner"]
        url, n = counts.get(name, (repo["url"], 0))
        counts[name] = (url, n + 1)
    rows = sorted(counts.items(), key=lambda item: -item[1][1])
    items = " · ".join(f'<a href="{url}">{name.split("/")[1]}</a> <sub>{n}</sub>' for name, (url, n) in rows)
    return f"<sub>MERGED PULL REQUESTS IN PUBLIC REPOSITORIES</sub><br>{items}" if items else ""


def hero_svg(theme: Theme, width: int = 880) -> str:
    """The profile's opening card: the name, and a small interface that switches theme and asks to approve a change."""
    narrow = width < 600
    height = 300 if narrow else 220
    ui_x, ui_y = (20, 120) if narrow else (width - 380, 28)
    ui_w, ui_h = (width - 40, 160) if narrow else (360, 164)
    sans = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img"
 aria-label="Trevor Antony, full-stack software engineer working on AI and UI/UX. A small interface switches theme and asks to approve a change.">
<style>
@media (prefers-reduced-motion: no-preference) {{
  .cursor {{ animation: move 8s ease-in-out infinite; }}
  .night {{ animation: night 8s ease-in-out infinite; }}
  .knob {{ animation: knob 8s ease-in-out infinite; }}
  .ask {{ animation: ask 8s ease-out infinite; }}
  .tick {{ animation: tick 8s ease-out infinite; }}
  .caret {{ animation: blink 1.1s steps(1) infinite; }}
  .ink {{ animation: ink 8s ease-in-out infinite; }}
}}
@keyframes move {{ 0%,8% {{ transform: translate(0,0); }} 22%,30% {{ transform: translate({ui_w - 84}px,-104px); }} 52%,60% {{ transform: translate({ui_w - 120}px,-4px); }} 78%,100% {{ transform: translate(0,0); }} }}
@keyframes night {{ 0%,24% {{ opacity: 0; }} 30%,92% {{ opacity: 1; }} 98%,100% {{ opacity: 0; }} }}
@keyframes knob {{ 0%,24% {{ transform: translateX(0); }} 30%,92% {{ transform: translateX(14px); }} 98%,100% {{ transform: translateX(0); }} }}
@keyframes ask {{ 0%,34% {{ opacity: 0; transform: translateY(6px); }} 40%,92% {{ opacity: 1; transform: translateY(0); }} 98%,100% {{ opacity: 0; }} }}
@keyframes tick {{ 0%,56% {{ opacity: 0; }} 60%,92% {{ opacity: 1; }} 98%,100% {{ opacity: 0; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@keyframes ink {{ 0%,24% {{ fill: {theme.fg}; }} 30%,92% {{ fill: #e6edf3; }} 98%,100% {{ fill: {theme.fg}; }} }}
</style>
<rect width="{width}" height="{height}" rx="10" fill="{theme.ink}"/>
<g font-family="{sans}">
  <text x="{20 if narrow else 40}" y="{48 if narrow else 84}" font-size="{30 if narrow else 38}" font-weight="700" fill="{theme.fg}">Trevor Antony<tspan class="caret" fill="{theme.average}">_</tspan></text>
  <text x="{20 if narrow else 40}" y="{76 if narrow else 118}" font-size="{14 if narrow else 16}" fill="{theme.muted}">Full-stack software engineer · AI · UI/UX</text>
  <text x="{20 if narrow else 40}" y="{98 if narrow else 144}" font-size="{12 if narrow else 13}" fill="{theme.muted}" font-family="{FONT}">Nairobi · React · TypeScript · Python</text>
</g>
<g transform="translate({ui_x},{ui_y})" font-family="{sans}">
  <rect width="{ui_w}" height="{ui_h}" rx="10" fill="{theme.fg}" opacity="0.05" stroke="{theme.muted}" stroke-opacity="0.35"/>
  <rect class="night" width="{ui_w}" height="{ui_h}" rx="10" fill="#010409" opacity="0"/>
  <circle cx="16" cy="16" r="4" fill="{theme.down}"/><circle cx="30" cy="16" r="4" fill="{theme.average}"/><circle cx="44" cy="16" r="4" fill="{theme.up}"/>
  <rect x="{ui_w - 52}" y="9" width="34" height="14" rx="7" fill="{theme.muted}" opacity="0.5"/>
  <g class="knob"><circle class="ink" cx="{ui_w - 44}" cy="16" r="5" fill="{theme.fg}"/></g>
  <rect x="16" y="38" width="{ui_w * 0.55:.0f}" height="8" rx="4" fill="{theme.muted}" opacity="0.45"/>
  <rect x="16" y="54" width="{ui_w * 0.4:.0f}" height="8" rx="4" fill="{theme.muted}" opacity="0.3"/>
  <g class="ask" opacity="0">
    <rect x="16" y="76" width="{ui_w - 32}" height="56" rx="8" fill="{theme.average}" opacity="0.12"/>
    <text class="ink" x="28" y="98" font-size="12" fill="{theme.fg}">Assistant · Let the support bot use a new model?</text>
    <rect x="{ui_w - 120}" y="108" width="80" height="18" rx="9" fill="{theme.up}"/>
    <text x="{ui_w - 80}" y="121" font-size="11" fill="#ffffff" text-anchor="middle" font-weight="600">Approve</text>
    <text class="tick" x="28" y="122" font-size="11" fill="#3fb950" opacity="0">✓ Allowed, version 4</text>
  </g>
  <g class="cursor"><path d="M40 120 l0 16 l4 -4 l3 7 l3 -1 l-3 -7 l6 0 z" fill="{theme.fg}" stroke="{theme.ink}" stroke-width="1"/></g>
</g>
</svg>"""


def _get(path: str, token: str):
    request = urllib.request.Request(
        f"{REST}/{path}", headers={"Authorization": f"bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "profile-chart"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def work_history(token: str, today: date) -> dict:
    """Every merged pull request, by month, split into private and public, as totals only: no repository is named."""
    query = urllib.parse.quote(f"author:{LOGIN} is:pr is:merged")
    merged = []
    for page in range(1, 11):
        items = _get(f"search/issues?q={query}&per_page=100&page={page}", token)["items"]
        merged.extend(items)
        if len(items) < 100:
            break
    repo_of = lambda item: item["repository_url"].removeprefix(f"{REST}/repos/")
    by_repo = Counter(repo_of(item) for item in merged)
    private = {repo for repo in by_repo if _get(f"repos/{repo}", token)["private"]}
    languages: Counter = Counter()
    for repo in private:
        sizes = _get(f"repos/{repo}/languages", token)
        total = sum(sizes.values()) or 1
        for name, size in sizes.items():
            languages[name] += by_repo[repo] * size / total
    first = min(date.fromisoformat(item["closed_at"][:10]) for item in merged) if merged else today
    months = {m: [0, 0] for m in _months(first, today)}
    for item in merged:
        months.setdefault(item["closed_at"][:7], [0, 0])[0 if repo_of(item) in private else 1] += 1
    weight = sum(languages.values()) or 1
    return {
        "since": f"{first:%Y-%m}",
        "merged": len(merged),
        "private": sum(by_repo[repo] for repo in private),
        "private_repositories": len(private),
        "months": [[m, *months[m]] for m in sorted(months)],
        "languages": [[name, round(100 * size / weight)] for name, size in languages.most_common(4)],
    }


def _months(since: date, today: date) -> list[str]:
    months, year, month = [], since.year, since.month
    while (year, month) <= (today.year, today.month):
        months.append(f"{year}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def history_svg(work: dict, theme: Theme, width: int = 880) -> str:
    narrow = width < 600
    height = 262 if narrow else 220
    left, right = 44, 16
    top, bottom = (110, 206) if narrow else (80, 178)
    # Bars start at the first month with steady work, so years with a stray pull request do not leave an empty chart.
    busy = next((i for i, (_, private, public) in enumerate(work["months"]) if private + public >= 2), 0)
    months = work["months"][-12:] if narrow else work["months"][busy:]
    step = (width - left - right) / len(months)
    peak = max(1, max(p + q for _, p, q in months))
    headline = f"{work['merged']:,}"
    since = date.fromisoformat(work["since"] + "-01")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
        f'aria-label="Merged pull requests per month since {since:%B %Y}, private and public, shown as totals only">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{theme.ink}"/>',
        f'<g font-family="{FONT}">',
        f'<text x="{left}" y="30" font-size="12" fill="{theme.muted}" letter-spacing="1.5">MERGED PULL REQUESTS · SINCE {f"{since:%b %Y}".upper()}</text>',
        f'<text x="{left}" y="60" font-size="26" font-weight="600" fill="{theme.fg}">{headline}</text>',
        f'<text x="{left + 16 + 15.6 * len(headline):.0f}" y="60" font-size="13" fill="{theme.muted}">{work["private"]:,} in {work["private_repositories"]} private repositories</text>',
    ]
    shares = " · ".join(f"{name} {share}%" for name, share in work["languages"] if share)
    sx, sy, anchor = (left, 84, "start") if narrow else (width - right, 30, "end")
    parts.append(f'<text x="{sx}" y="{sy}" font-size="12" fill="{theme.muted}" text-anchor="{anchor}">{shares}</text>')
    lx = width - right
    ly = (top - 14) if not narrow else (height - 12)
    parts.append(f'<text x="{lx}" y="{ly}" font-size="11" text-anchor="end"><tspan fill="{theme.up}">■ private</tspan><tspan fill="{theme.muted}">  ■ public</tspan></text>')
    bar = max(2.0, step * 0.7)
    for i, (month, private, public) in enumerate(months):
        x = left + step * i + (step - bar) / 2
        hp = (bottom - top) * private / peak
        hq = (bottom - top) * public / peak
        if private:
            parts.append(f'<rect x="{x:.1f}" y="{bottom - hp:.1f}" width="{bar:.1f}" height="{hp:.1f}" rx="1.5" fill="{theme.up}"><title>{month}: {private} private</title></rect>')
        if public:
            parts.append(f'<rect x="{x:.1f}" y="{bottom - hp - hq:.1f}" width="{bar:.1f}" height="{hq:.1f}" rx="1.5" fill="{theme.muted}" opacity="0.7"><title>{month}: {public} public</title></rect>')
        on = date.fromisoformat(month + "-01")
        label = f"{on:%b %y}" if narrow and i % 2 == 0 else f"{on:%Y}" if not narrow and on.month == 1 else ""
        if label:
            parts.append(f'<text x="{x + bar / 2:.1f}" y="{bottom + 18}" font-size="10" fill="{theme.muted}" text-anchor="middle">{label}</text>')
    parts.append(f'<line x1="{left}" x2="{width - right}" y1="{bottom}" y2="{bottom}" stroke="{theme.grid}"/>')
    parts.append("</g></svg>")
    return "\n".join(parts)


def replace_section(text: str, key: str, content: str) -> str:
    start, end = MARKERS[key]
    head, _, rest = text.partition(start)
    _, _, tail = rest.partition(end)
    return f"{head}{start}\n{content}\n{end}{tail}"


def main() -> None:
    data = fetch(os.environ["GITHUB_TOKEN"])
    calendar = data["user"]["contributionsCollection"]["contributionCalendar"]
    candles = candles_of(days_of(calendar))
    longest, current = streaks(calendar)
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        (assets / f"hero-{name}.svg").write_text(hero_svg(theme), encoding="utf-8")
        (assets / f"hero-{name}-narrow.svg").write_text(hero_svg(theme, width=420), encoding="utf-8")
        (assets / f"activity-{name}.svg").write_text(svg(candles, calendar["totalContributions"], longest, current, theme), encoding="utf-8")
        (assets / f"activity-{name}-narrow.svg").write_text(svg(candles, calendar["totalContributions"], longest, current, theme, width=420, days=45), encoding="utf-8")
    # Private work needs a token of the profile's owner; without one, the last drawn card is kept as it is.
    stats_token = os.environ.get("PROFILE_STATS_TOKEN")
    if stats_token:
        work = work_history(stats_token, date.today())
        (assets / "private-work.json").write_text(json.dumps(work, indent=1), encoding="utf-8")
        for name, theme in (("dark", DARK), ("light", LIGHT)):
            (assets / f"private-{name}.svg").write_text(history_svg(work, theme), encoding="utf-8")
            (assets / f"private-{name}-narrow.svg").write_text(history_svg(work, theme, width=420), encoding="utf-8")
    readme = ROOT / "README.md"
    readme.write_text(replace_section(readme.read_text(encoding="utf-8"), "open-source", open_source_section(data["search"])), encoding="utf-8")


if __name__ == "__main__":
    main()
