"""The profile's animated cards: the opening card and four small demos of the kind of interface work behind it.

Each card is a plain SVG with CSS animation, so it plays inside GitHub's image renderer, which runs no
script. Motion stops for visitors who ask their system to reduce it, and every card comes in light and
dark versions drawn from the same palette as the charts.
"""

from __future__ import annotations

from dataclasses import dataclass

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LOOP = "8s"


@dataclass(frozen=True)
class Palette:
    ink: str
    panel: str
    fg: str
    muted: str
    line: str
    accent: str
    good: str
    warm: str
    bad: str


DARK = Palette(ink="#0d1117", panel="#161b22", fg="#e6edf3", muted="#8b949e", line="#30363d", accent="#4493f8", good="#3fb950", warm="#d29922", bad="#f85149")
LIGHT = Palette(ink="#ffffff", panel="#f6f8fa", fg="#1f2328", muted="#59636e", line="#d1d9e0", accent="#0969da", good="#1a7f37", warm="#9a6700", bad="#cf222e")


def _frame(width: int, height: int, p: Palette, label: str, css: str, body: str, title: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{title}">
<style>
@media (prefers-reduced-motion: no-preference) {{
{css}
}}
</style>
<rect width="{width}" height="{height}" rx="10" fill="{p.ink}"/>
<text x="20" y="28" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{p.muted}">{label}</text>
{body}
</svg>"""


def hero(p: Palette, width: int = 880) -> str:
    """The name, and a small window that loads its content and switches theme."""
    narrow = width < 600
    height = 300 if narrow else 220
    ux, uy = (20, 120) if narrow else (width - 380, 28)
    uw, uh = (width - 40, 160) if narrow else (360, 164)
    night = "#0d1117"
    css = f"""  .skeleton {{ animation: skeleton {LOOP} ease-in-out infinite; }}
  .content {{ animation: content {LOOP} ease-in-out infinite; }}
  .bar {{ transform-box: fill-box; transform-origin: bottom; animation: grow {LOOP} ease-out infinite; }}
  .night {{ animation: night {LOOP} ease-in-out infinite; }}
  .knob {{ animation: knob {LOOP} ease-in-out infinite; }}
  .ink {{ animation: ink {LOOP} ease-in-out infinite; }}
  .cursor {{ animation: cursor {LOOP} ease-in-out infinite; }}
  .caret {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes skeleton {{ 0%,18% {{ opacity: 1; }} 26%,100% {{ opacity: 0; }} }}
  @keyframes content {{ 0%,20% {{ opacity: 0; }} 28%,100% {{ opacity: 1; }} }}
  @keyframes grow {{ 0%,24% {{ transform: scaleY(0.05); }} 40%,100% {{ transform: scaleY(1); }} }}
  @keyframes cursor {{ 0%,40% {{ transform: translate(0,0); }} 54%,64% {{ transform: translate({uw - 100}px,-112px); }} 86%,100% {{ transform: translate(0,0); }} }}
  @keyframes night {{ 0%,56% {{ opacity: 0; }} 62%,92% {{ opacity: 1; }} 98%,100% {{ opacity: 0; }} }}
  @keyframes knob {{ 0%,56% {{ transform: translateX(0); }} 62%,92% {{ transform: translateX(14px); }} 98%,100% {{ transform: translateX(0); }} }}
  @keyframes ink {{ 0%,56% {{ fill: {p.fg}; }} 62%,92% {{ fill: #e6edf3; }} 98%,100% {{ fill: {p.fg}; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}"""
    bars = "".join(
        f'<rect class="bar" style="animation-delay:{i * 0.08:.2f}s" x="{22 + i * 30}" y="{uh - 22 - h}" width="18" height="{h}" rx="3" fill="{p.accent}" opacity="{0.55 + i * 0.07:.2f}"/>'
        for i, h in enumerate((34, 52, 40, 68, 58, 80))
    )
    tx = 20 if narrow else 40
    body = f"""<g font-family="{SANS}">
  <text x="{tx}" y="{56 if narrow else 84}" font-size="{30 if narrow else 38}" font-weight="700" fill="{p.fg}">Trevor Antony<tspan class="caret" fill="{p.warm}">_</tspan></text>
  <text x="{tx}" y="{82 if narrow else 118}" font-size="{14 if narrow else 16}" fill="{p.muted}">Full-stack software engineer · AI · UI/UX</text>
  <text x="{tx}" y="{104 if narrow else 144}" font-size="{12 if narrow else 13}" fill="{p.muted}" font-family="{MONO}">Nairobi · React · TypeScript · Python</text>
</g>
<g transform="translate({ux},{uy})" font-family="{SANS}">
  <rect width="{uw}" height="{uh}" rx="10" fill="{p.panel}" stroke="{p.line}"/>
  <rect class="night" width="{uw}" height="{uh}" rx="10" fill="{night}" opacity="0"/>
  <circle cx="16" cy="16" r="4" fill="{p.bad}"/><circle cx="30" cy="16" r="4" fill="{p.warm}"/><circle cx="44" cy="16" r="4" fill="{p.good}"/>
  <rect x="{uw - 52}" y="9" width="34" height="14" rx="7" fill="{p.muted}" opacity="0.5"/>
  <g class="knob"><circle class="ink" cx="{uw - 44}" cy="16" r="5" fill="{p.fg}"/></g>
  <g class="skeleton">
    <rect x="16" y="40" width="{uw * 0.5:.0f}" height="10" rx="5" fill="{p.muted}" opacity="0.3"/>
    <rect x="16" y="60" width="{uw * 0.32:.0f}" height="10" rx="5" fill="{p.muted}" opacity="0.2"/>
    <rect x="16" y="84" width="{uw - 32}" height="{uh - 100}" rx="8" fill="{p.muted}" opacity="0.12"/>
  </g>
  <g class="content" opacity="0">
    <text class="ink" x="16" y="48" font-size="12" fill="{p.fg}">Requests this week</text>
    <text class="ink" x="16" y="72" font-size="22" font-weight="700" fill="{p.fg}">1,284</text>
    <text x="84" y="72" font-size="12" fill="{p.good}">+18%</text>
    {bars}
  </g>
  <g class="cursor"><path d="M70 130 l0 16 l4 -4 l3 7 l3 -1 l-3 -7 l6 0 z" fill="{p.fg}" stroke="{p.ink}" stroke-width="1"/></g>
</g>"""
    return _frame(width, height, p, "", css, body, "Trevor Antony, full-stack software engineer working on AI and UI/UX. A small window loads a dashboard card and switches theme.")


def design_system(p: Palette) -> str:
    """A button through its states, a toggle, a moving chip selection and typed search text."""
    width, height = 434, 230
    css = f"""  .btn {{ transform-box: fill-box; transform-origin: center; animation: btn {LOOP} ease-in-out infinite; }}
  .ring {{ animation: ring {LOOP} ease-in-out infinite; }}
  .state {{ animation: state {LOOP} steps(1) infinite; }}
  .tknob {{ animation: tknob {LOOP} ease-in-out infinite; }}
  .ttrack {{ animation: ttrack {LOOP} ease-in-out infinite; }}
  .chip {{ animation: chip {LOOP} ease-in-out infinite; }}
  .typed {{ animation: typed {LOOP} steps(14) infinite; }}
  @keyframes btn {{ 0%,10% {{ transform: scale(1); filter: none; }} 18%,26% {{ transform: scale(1); filter: brightness(1.18); }} 30%,34% {{ transform: scale(0.94); }} 40%,100% {{ transform: scale(1); filter: none; }} }}
  @keyframes ring {{ 0%,44% {{ opacity: 0; }} 50%,70% {{ opacity: 1; }} 76%,100% {{ opacity: 0; }} }}
  @keyframes tknob {{ 0%,30% {{ transform: translateX(0); }} 38%,80% {{ transform: translateX(18px); }} 88%,100% {{ transform: translateX(0); }} }}
  @keyframes ttrack {{ 0%,30% {{ fill: {p.muted}; }} 38%,80% {{ fill: {p.good}; }} 88%,100% {{ fill: {p.muted}; }} }}
  @keyframes chip {{ 0%,20% {{ transform: translateX(0); }} 28%,48% {{ transform: translateX(84px); }} 56%,76% {{ transform: translateX(168px); }} 84%,100% {{ transform: translateX(0); }} }}
  @keyframes typed {{ 0%,10% {{ width: 0; }} 50%,90% {{ width: 140px; }} 100% {{ width: 0; }} }}"""
    chips = "".join(
        f'<text x="{62 + i * 84}" y="134" font-size="12" text-anchor="middle" fill="{p.fg}">{name}</text>' for i, name in enumerate(("Overview", "Usage", "Budgets"))
    )
    body = f"""<g font-family="{SANS}">
  <rect class="ring" x="16" y="44" width="132" height="44" rx="12" fill="none" stroke="{p.accent}" stroke-width="2" opacity="0"/>
  <g class="btn"><rect x="20" y="48" width="124" height="36" rx="9" fill="{p.accent}"/><text x="82" y="71" font-size="13" font-weight="600" text-anchor="middle" fill="#ffffff">New profile</text></g>
  <rect class="ttrack" x="172" y="56" width="40" height="22" rx="11" fill="{p.muted}"/>
  <circle class="tknob" cx="184" cy="67" r="8" fill="#ffffff"/>
  <text x="222" y="72" font-size="12" fill="{p.muted}">Dark mode</text>
  <rect x="20" y="114" width="252" height="32" rx="16" fill="{p.panel}" stroke="{p.line}"/>
  <rect class="chip" x="22" y="116" width="80" height="28" rx="14" fill="{p.accent}" opacity="0.18"/>
  {chips}
  <rect x="20" y="166" width="394" height="40" rx="9" fill="{p.panel}" stroke="{p.line}"/>
  <text x="34" y="191" font-size="13" fill="{p.muted}">⌕</text>
  <clipPath id="typing"><rect class="typed" x="54" y="172" width="0" height="28"/></clipPath>
  <text x="54" y="191" font-size="13" fill="{p.fg}" clip-path="url(#typing)">Search profiles…</text>
</g>"""
    return _frame(width, height, p, "DESIGN SYSTEM", css, body, "A design system: a button moving through hover, pressed and focus states, a toggle, a chip selection and a search field being typed into.")


def responsive(p: Palette) -> str:
    """A desktop layout with a sidebar and three cards that folds into a phone layout and back."""
    width, height = 434, 230
    css = f"""  .wide {{ animation: wide {LOOP} ease-in-out infinite; }}
  .phone {{ animation: phone {LOOP} ease-in-out infinite; }}
  @keyframes wide {{ 0%,30% {{ opacity: 1; }} 40%,80% {{ opacity: 0; }} 90%,100% {{ opacity: 1; }} }}
  @keyframes phone {{ 0%,30% {{ opacity: 0; }} 40%,80% {{ opacity: 1; }} 90%,100% {{ opacity: 0; }} }}"""
    device = (
        f'<rect x="20" y="44" width="394" height="166" rx="10" fill="{p.panel}" stroke="{p.line}">'
        f'<animate attributeName="x" values="20;20;152;152;20" keyTimes="0;0.3;0.4;0.82;0.92" dur="{LOOP}" repeatCount="indefinite"/>'
        f'<animate attributeName="width" values="394;394;130;130;394" keyTimes="0;0.3;0.4;0.82;0.92" dur="{LOOP}" repeatCount="indefinite"/></rect>'
    )
    wide_cards = "".join(f'<rect x="{124 + i * 96}" y="96" width="84" height="56" rx="6" fill="{p.accent}" opacity="{0.25 + i * 0.12:.2f}"/>' for i in range(3))
    phone_cards = "".join(f'<rect x="162" y="{78 + i * 34}" width="110" height="26" rx="5" fill="{p.accent}" opacity="{0.25 + i * 0.12:.2f}"/>' for i in range(3))
    tabs = "".join(f'<circle cx="{180 + i * 37}" cy="196" r="4" fill="{p.muted}"/>' for i in range(3))
    body = f"""{device}
<g class="wide">
  <rect x="30" y="54" width="80" height="146" rx="6" fill="{p.muted}" opacity="0.14"/>
  {''.join(f'<rect x="40" y="{68 + i * 20}" width="{56 - i * 6}" height="8" rx="4" fill="{p.muted}" opacity="0.45"/>' for i in range(4))}
  <rect x="124" y="60" width="140" height="12" rx="6" fill="{p.fg}" opacity="0.7"/>
  {wide_cards}
  <rect x="124" y="164" width="276" height="30" rx="6" fill="{p.muted}" opacity="0.14"/>
</g>
<g class="phone" opacity="0">
  <rect x="162" y="56" width="70" height="10" rx="5" fill="{p.fg}" opacity="0.7"/>
  {phone_cards}
  <line x1="152" x2="282" y1="184" y2="184" stroke="{p.line}"/>
  {tabs}
</g>"""
    return _frame(width, height, p, "RESPONSIVE", css, body, "A desktop layout with a sidebar and three cards folding into a phone layout with stacked cards and a bottom tab bar.")


def ai_chat(p: Palette) -> str:
    """A question, an answer streaming in, and the live chart it ends with."""
    width, height = 434, 230
    css = f"""  .ask {{ animation: ask {LOOP} ease-out infinite; }}
  .reply {{ animation: reply {LOOP} ease-out infinite; }}
  .stream {{ animation: stream {LOOP} steps(24) infinite; }}
  .spark {{ stroke-dasharray: 220; animation: spark {LOOP} ease-out infinite; }}
  .dots {{ animation: dots {LOOP} steps(1) infinite; }}
  @keyframes ask {{ 0%,4% {{ opacity: 0; transform: translateY(6px); }} 10%,94% {{ opacity: 1; transform: none; }} 100% {{ opacity: 0; }} }}
  @keyframes dots {{ 0%,12% {{ opacity: 0; }} 14%,24% {{ opacity: 1; }} 26%,100% {{ opacity: 0; }} }}
  @keyframes reply {{ 0%,24% {{ opacity: 0; }} 28%,94% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
  @keyframes stream {{ 0%,28% {{ width: 0; }} 56%,94% {{ width: 300px; }} 100% {{ width: 0; }} }}
  @keyframes spark {{ 0%,56% {{ stroke-dashoffset: 220; }} 72%,94% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: 220; }} }}"""
    body = f"""<g font-family="{SANS}">
  <g class="ask"><rect x="194" y="42" width="220" height="32" rx="14" fill="{p.accent}"/><text x="304" y="63" font-size="12" text-anchor="middle" fill="#ffffff">How did signups do this month?</text></g>
  <g class="dots" opacity="0">{''.join(f'<circle cx="{36 + i * 12}" cy="100" r="3.5" fill="{p.muted}"/>' for i in range(3))}</g>
  <g class="reply" opacity="0">
    <rect x="20" y="86" width="330" height="124" rx="14" fill="{p.panel}" stroke="{p.line}"/>
    <clipPath id="streaming"><rect class="stream" x="34" y="94" width="0" height="40"/></clipPath>
    <g clip-path="url(#streaming)">
      <text x="34" y="110" font-size="12" fill="{p.fg}">Up 18% on last month, mostly from the</text>
      <text x="34" y="128" font-size="12" fill="{p.fg}">new onboarding flow. Here is the trend:</text>
    </g>
    <rect x="34" y="140" width="300" height="56" rx="8" fill="{p.ink}" stroke="{p.line}"/>
    <path class="spark" d="M44 186 L84 178 L124 182 L164 168 L204 170 L244 156 L284 150 L324 146" fill="none" stroke="{p.good}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</g>"""
    return _frame(width, height, p, "AI CHAT", css, body, "An AI chat: a question, an answer streaming in, and a small live chart drawn at the end of the answer.")


def workflow(p: Palette) -> str:
    """A run moving through its steps, each lighting up in turn, ending with a tick."""
    width, height = 434, 230
    steps = ("Check", "Resolve", "Read", "Summarise", "Done")
    xs = [44 + i * 86 for i in range(len(steps))]
    css_steps = "\n".join(
        f"  .s{i} {{ animation: s{i} {LOOP} ease-in-out infinite; }}\n"
        f"  @keyframes s{i} {{ 0%,{8 + i * 14}% {{ fill: {p.panel}; stroke: {p.line}; }} {12 + i * 14}%,92% {{ fill: {p.good if i == len(steps) - 1 else p.accent}; stroke: transparent; }} 100% {{ fill: {p.panel}; stroke: {p.line}; }} }}"
        for i in range(len(steps))
    )
    css = f"""{css_steps}
  .flow {{ stroke-dasharray: 6 6; animation: flow 1s linear infinite; }}
  .tick {{ animation: tick {LOOP} ease-out infinite; }}
  .pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse {LOOP} ease-out infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -12; }} }}
  @keyframes tick {{ 0%,68% {{ opacity: 0; }} 74%,92% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
  @keyframes pulse {{ 0%,68% {{ opacity: 0; transform: scale(1); }} 72% {{ opacity: 0.5; }} 90%,100% {{ opacity: 0; transform: scale(1.9); }} }}"""
    edges = "".join(f'<line class="flow" x1="{xs[i] + 18}" x2="{xs[i + 1] - 18}" y1="118" y2="118" stroke="{p.muted}" stroke-width="2"/>' for i in range(len(steps) - 1))
    nodes = "".join(
        f'<circle class="s{i}" cx="{x}" cy="118" r="16" fill="{p.panel}" stroke="{p.line}" stroke-width="2"/>'
        f'<text x="{x}" y="156" font-size="11" text-anchor="middle" fill="{p.muted}">{name}</text>'
        for i, (x, name) in enumerate(zip(xs, steps))
    )
    last = xs[-1]
    body = f"""<g font-family="{SANS}">
  {edges}
  <circle class="pulse" cx="{last}" cy="118" r="16" fill="{p.good}" opacity="0"/>
  {nodes}
  <path class="tick" d="M{last - 7} 118 l5 5 l9 -10" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>
  <text x="20" y="196" font-size="12" fill="{p.muted}">Each run shows its state as it moves, and retries what fails.</text>
</g>"""
    return _frame(width, height, p, "WORKFLOWS", css, body, "A workflow run moving through Check, Resolve, Read and Summarise to Done, each step lighting up in turn and ending with a tick.")


CARDS = {"design-system": design_system, "responsive": responsive, "ai-chat": ai_chat, "workflow": workflow}
