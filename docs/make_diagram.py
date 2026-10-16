"""Generates docs/architecture-light.svg and docs/architecture-dark.svg.

Run from the repository root: python docs/make_diagram.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent

THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", muted="#59636e", card="#ffffff", line="#d0d7de",
                  wire="#8c959f", fast="#0d9488", heavy="#5b5bd6", amber="#d97706", vault="#7c3aed",
                  fast_tint="#0d948812", heavy_tint="#5b5bd610", vault_tint="#7c3aed0d"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9198a1", card="#161b22", line="#30363d",
                 wire="#6e7681", fast="#2dd4bf", heavy="#8b8cf6", amber="#f59e0b", vault="#a78bfa",
                 fast_tint="#2dd4bf14", heavy_tint="#8b8cf612", vault_tint="#a78bfa10"),
}

W, H = 1280, 680
CW, CH, CY = 140, 100, 332            # specialist card width, height, top
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# (name, role, tier, vault folder); order puts Validator between the two agents it checks
AGENTS = [
    ("Task Manager", "goals → small steps", "fast", "Goals"),
    ("Secretary", "plans today", "fast", "Schedule"),
    ("Researcher", "cited research", "heavy", "Research"),
    ("Validator", "re-checks evidence", "heavy", "Validation"),
    ("Coder", "writes &amp; runs code", "heavy", "Code"),
    ("YouTube Partner", "video pipeline", "heavy", "Content"),
    ("Film Partner", "DaVinci Resolve", "heavy", "Editing"),
]
GAPS = [18, 40, 44, 44, 40, 18]       # wider gaps separate the groups and fit the MAVF arrows
XS = [48]
for g in GAPS:
    XS.append(XS[-1] + CW + g)
CX = [x + CW / 2 for x in XS]
MODEL = {"fast": "qwen3.5 · 9B", "heavy": "qwen3.6 · 27B"}


def text(x, y, s, size, fill, weight=400, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def badge(cx, y, label, color):
    w = 7.2 * len(label) + 18
    return (f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="20" rx="10" fill="{color}" fill-opacity="0.14"/>'
            + text(cx, y + 14, label, 11, color, 600))


def card(x, y, w, h, name, role, tier, t):
    c = t[tier]
    cx = x + w / 2
    return "".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["card"]}" stroke="{t["line"]}"/>',
        f'<path d="M{x + 12},{y} H{x + w - 12}" stroke="{c}" stroke-width="3" stroke-linecap="round"/>',
        text(cx, y + 32, name, 15, t["ink"], 650),
        text(cx, y + 53, role, 12, t["muted"]),
        badge(cx, y + h - 32, MODEL[tier], c),
    ])


def build(t):
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'font-family="{FONT}">')
    s.append("<defs>")
    for name, col in [("wire", t["wire"]), ("amber", t["amber"]), ("vault", t["vault"]), ("fast", t["fast"])]:
        s.append(f'<marker id="a-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
                 f'orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9 z" fill="{col}"/></marker>')
    s.append("</defs>")
    s.append(f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>')

    # header
    s.append(text(48, 52, "Hermes local agents", 20, t["ink"], 700, "start"))
    s.append(text(48, 74, "8 agents · 2 local models · 1 GPU · nothing leaves the machine", 13, t["muted"], 400, "start"))
    s.append(text(W - 48, 52, "RX 7900 XTX · 24 GB", 13, t["muted"], 600, "end"))
    s.append(text(W - 48, 72, "Ollama · ROCm · Hermes Agent", 12, t["muted"], 400, "end"))

    # entry point
    ew, ey = 300, 96
    s.append(f'<rect x="{W / 2 - ew / 2}" y="{ey}" width="{ew}" height="40" rx="20" fill="{t["card"]}" stroke="{t["line"]}"/>')
    s.append(text(W / 2, ey + 25, "You  ·  Discord · Telegram · CLI", 14, t["ink"], 600))
    s.append(f'<path d="M{W / 2},{ey + 40} V172" stroke="{t["wire"]}" stroke-width="1.6" marker-end="url(#a-wire)"/>')

    # orchestrator
    ox, oy, ow, oh = W / 2 - 160, 176, 320, 86
    s.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="14" fill="{t["card"]}" stroke="{t["fast"]}" stroke-width="1.6"/>')
    s.append(text(W / 2, oy + 31, "Orchestrator", 17, t["ink"], 700))
    s.append(text(W / 2, oy + 51, "classifies and delegates · no work tools", 12, t["muted"]))
    s.append(badge(W / 2, oy + oh - 26, MODEL["fast"] + " · always warm", t["fast"]))

    # tier groups
    pad = 12
    groups = [(0, 1, "fast"), (2, 6, "heavy")]
    for a, b, tier in groups:
        gx, gw = XS[a] - pad, XS[b] + CW - XS[a] + 2 * pad
        s.append(f'<rect x="{gx}" y="{CY - pad}" width="{gw}" height="{CH + 2 * pad}" rx="18" '
                 f'fill="{t[tier + "_tint"]}" stroke="{t[tier]}" stroke-opacity="0.35" stroke-dasharray="2 4"/>')

    # delegation bus (validator is reached through MAVF, not routing)
    bus_y, trunk_x = 294, W / 2 - 70
    s.append(f'<path d="M{trunk_x},{oy + oh} V{bus_y}" stroke="{t["wire"]}" stroke-width="1.6"/>')
    s.append(f'<path d="M{CX[0]},{bus_y} H{CX[-1]}" stroke="{t["wire"]}" stroke-width="1.6" fill="none"/>')
    for i, cx in enumerate(CX):
        if AGENTS[i][0] == "Validator":
            continue
        s.append(f'<path d="M{cx},{bus_y} V{CY - 3}" stroke="{t["wire"]}" stroke-width="1.6" marker-end="url(#a-wire)"/>')
    s.append(f'<circle cx="{trunk_x}" cy="{bus_y}" r="3.5" fill="{t["wire"]}"/>')
    s.append(text(trunk_x - 10, bus_y - 10, "delegates", 11, t["muted"], 500, "end"))

    # MAVF: orchestrator <-> validator, researcher/coder -> validator
    vi = 3
    vx = CX[vi] + 40
    s.append(f'<path d="M{vx},{bus_y - 5} V{bus_y + 5}" stroke="{t["bg"]}" stroke-width="8"/>')
    s.append(f'<path d="M{vx},{oy + oh + 3} V{CY - 3}" stroke="{t["amber"]}" stroke-width="1.8" '
             f'stroke-dasharray="5 4" marker-start="url(#a-amber)" marker-end="url(#a-amber)"/>')
    s.append(text(vx + 10, bus_y - 12, "MAVF verdict", 11, t["amber"], 600, "start"))
    my = CY + CH / 2 - 12
    s.append(f'<path d="M{XS[2] + CW + 3},{my} H{XS[3] - 4}" stroke="{t["amber"]}" stroke-width="1.8" '
             f'stroke-dasharray="5 4" marker-end="url(#a-amber)"/>')
    s.append(f'<path d="M{XS[4] - 3},{my} H{XS[3] + CW + 4}" stroke="{t["amber"]}" stroke-width="1.8" '
             f'stroke-dasharray="5 4" marker-end="url(#a-amber)"/>')

    for x, (name, role, tier, _) in zip(XS, AGENTS):
        s.append(card(x, CY, CW, CH, name, role, tier, t))

    # vault
    vy, vh = 466, 140
    s.append(f'<rect x="{XS[0] - pad}" y="{vy}" width="{XS[-1] + CW - XS[0] + 2 * pad}" height="{vh}" rx="18" '
             f'fill="{t["vault_tint"]}" stroke="{t["vault"]}" stroke-opacity="0.45"/>')
    chip_y = vy + 18
    for cx, x, (_, _, _, folder) in zip(CX, XS, AGENTS):
        s.append(f'<path d="M{cx},{CY + CH} V{chip_y - 4}" stroke="{t["vault"]}" stroke-width="1.4" '
                 f'stroke-opacity="0.8" marker-end="url(#a-vault)"/>')
        s.append(f'<rect x="{x}" y="{chip_y}" width="{CW}" height="44" rx="10" fill="{t["card"]}" stroke="{t["vault"]}" stroke-opacity="0.55"/>')
        s.append(text(cx, chip_y + 27, folder + "/", 13, t["vault"], 650))
    s.append(text(XS[0] + 4, vy + 92, "Shared Obsidian vault", 15, t["ink"], 700, "start"))
    s.append(text(XS[0] + 4, vy + 114,
                  "Every write goes through vault_write.py, which enforces a schema per folder. Notes link by id, "
                  "so a finding links to the verdict that checked it and a daily plan to the goal it advances.",
                  12, t["muted"], 400, "start"))

    # cron: Goals -> Secretary
    gx = XS[0] + CW
    s.append(f'<path d="M{gx + 3},{chip_y + 22} C{gx + 40},{chip_y + 22} {CX[1] - 30},{chip_y - 8} {CX[1] - 30},{CY + CH + 5}" '
             f'fill="none" stroke="{t["fast"]}" stroke-width="1.8" marker-end="url(#a-fast)"/>')
    s.append(text(CX[1] - 44, CY + CH + 32, "07:00 cron", 11, t["fast"], 650, "end"))

    # legend
    ly = H - 34
    items = [
        ("line", t["wire"], "", "delegation"),
        ("line", t["amber"], "5 4", "MAVF verification"),
        ("line", t["vault"], "", "vault write"),
        ("dot", t["fast"], "", "fast tier · 64k ctx · always warm"),
        ("dot", t["heavy"], "", "heavy tier · 128k ctx · loaded on demand"),
    ]
    x = 48
    for kind, col, dash, label in items:
        if kind == "line":
            s.append(f'<path d="M{x},{ly} H{x + 26}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>')
            x += 34
        else:
            s.append(f'<circle cx="{x + 6}" cy="{ly}" r="5" fill="{col}"/>')
            x += 18
        s.append(text(x, ly + 4, label, 12, t["muted"], 400, "start"))
        x += 6.4 * len(label) + 28

    s.append("</svg>")
    return "\n".join(s)


for name, theme in THEMES.items():
    (OUT / f"architecture-{name}.svg").write_text(build(theme), encoding="utf-8")
    print(f"wrote docs/architecture-{name}.svg")
