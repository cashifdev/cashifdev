"""Rebuilds the neon project cards and the terminal `ls ./projects` line
from the owner's public repositories. Run by .github/workflows/projects.yml."""
import json, os, re, textwrap, urllib.request
from html import escape

OWNER = os.environ.get("OWNER", "cashifdev")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
MAX_CARDS = 6
EXTRA_TERMINAL = []          # shown after the repo names
COLORS = ["#00ff9c", "#00e5ff", "#ff2bd6"]
FONT = "font-family:'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"

def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

repos = api(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&sort=pushed")
repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"].lower() != OWNER.lower() and not r["name"].lower().endswith(".github.io")]
repos.sort(key=lambda r: (-r["stargazers_count"], r["pushed_at"]), reverse=False)
repos.sort(key=lambda r: r["pushed_at"], reverse=True)
repos = repos[:MAX_CARDS]
# keep the mix varied: niche add-on repos go after the rest
repos.sort(key=lambda r: r["name"].lower().startswith("codychat-"))

def card(r, col):
    w, h = 420, 150
    desc = r["description"] or "No description yet."
    lines = textwrap.wrap(desc, 44)[:2]
    if len(textwrap.wrap(desc, 44)) > 2: lines[1] = lines[1][:41] + "..."
    lang = r["language"] or "code"
    tag = f"{lang.upper()}  ·  ★ {r['stargazers_count']}"
    title = r["name"] if len(r["name"]) <= 28 else r["name"][:27] + "…"
    body = "".join(f'<text x="24" y="{106+i*20}" fill="#8b949e" style="font-size:13.5px">{escape(l)}</text>' for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>text{{{FONT}}} .b{{stroke-dasharray:120 1000;animation:run 4s linear infinite}} @keyframes run{{to{{stroke-dashoffset:-1120}}}}
.p{{animation:p 2s ease-in-out infinite}} @keyframes p{{50%{{opacity:.3}}}}</style>
<rect x="2" y="2" width="{w-4}" height="{h-4}" rx="12" fill="#0b0f14" stroke="{col}" stroke-opacity=".25"/>
<rect class="b" x="2" y="2" width="{w-4}" height="{h-4}" rx="12" fill="none" stroke="{col}" stroke-width="2.5" style="filter:drop-shadow(0 0 4px {col})"/>
<text x="24" y="40" fill="{col}" style="font-size:12px;letter-spacing:3px"><tspan class="p">■</tspan> {escape(tag)}</text>
<text x="24" y="76" fill="#eafff5" style="font-size:22px;font-weight:700">{escape(title)}</text>
{body}
</svg>'''

os.makedirs("assets/cards", exist_ok=True)
keep = set()
html = []
for i, r in enumerate(repos):
    fn = f"assets/cards/{r['name']}.svg"; keep.add(os.path.basename(fn))
    open(fn, "w").write(card(r, COLORS[i % len(COLORS)]))
    html.append(f'  <a href="{r["html_url"]}"><img src="{fn}" width="49%" alt="{escape(r["name"])}"></a>')
for f in os.listdir("assets/cards"):
    if f not in keep: os.remove(os.path.join("assets/cards", f))

block = "<!-- PROJECTS:START -->\n<p align=\"center\">\n" + "\n".join(html) + "\n</p>\n<!-- PROJECTS:END -->"
readme = open("README.md").read()
readme = re.sub(r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->", block, readme, flags=re.S)
open("README.md", "w").write(readme)

# terminal line
names = [r["name"] + "/" for r in repos[:3]] + EXTRA_TERMINAL
line = "   ".join(names)
term = open("assets/terminal.svg").read()
term = re.sub(r'(<text id="ls-out"[^>]*>)(.*?)(<animate)', lambda m: m.group(1) + escape(line) + m.group(3), term, flags=re.S)
open("assets/terminal.svg", "w").write(term)
print("cards:", [r["name"] for r in repos])
