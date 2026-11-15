"""Adds a guestbook entry to README.md from a new issue titled 'guestbook: <message>'."""
import json, os, re, datetime
from html import escape
ev = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
issue = ev["issue"]
title = issue["title"]
msg = re.sub(r"^\s*guestbook\s*:\s*", "", title, flags=re.I)
msg = re.sub(r"https?://\S+", "[link]", msg)
msg = re.sub(r"[<>`|*_\[\]\\]", "", msg).strip()[:80]
ok = bool(msg)
if ok:
    user = issue["user"]["login"]
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    row = f'| <img src="https://github.com/{user}.png?size=40" width="20"> [@{user}](https://github.com/{user}) | {escape(msg)} | {date} |'
    r = open("README.md").read()
    m = re.search(r"<!-- GUESTBOOK:START -->\n(.*?)<!-- GUESTBOOK:END -->", r, re.S)
    rows = [l for l in m.group(1).splitlines() if l.startswith("| <img")]
    rows = ([row] + rows)[:8]
    block = "<!-- GUESTBOOK:START -->\n| Visitor | Message | Date |\n|:--|:--|:--|\n" + "\n".join(rows) + "\n<!-- GUESTBOOK:END -->"
    r = r[:m.start()] + block + r[m.end():]
    open("README.md", "w").write(r)
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"ok={'true' if ok else 'false'}\n")
