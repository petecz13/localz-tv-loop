"""Add (or refresh) the Christmas overlay in deploy/loop.html.

    python3 tools/add_christmas.py          # add / update the overlay
    python3 tools/add_christmas.py --remove # take it back out

loop.html is a bundle: the real page lives as a JSON string inside
<script type="__bundler/template">. This unpacks it, drops the overlay
script (tools/christmas_overlay.js) in before </body>, hooks it into the
slide change, and packs it back up. Safe to run more than once.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOOP = ROOT / "deploy" / "loop.html"
OVERLAY = ROOT / "tools" / "christmas_overlay.js"

START, END = "<!--XMAS-START-->", "<!--XMAS-END-->"
HOOK = "try { window.__xmas && window.__xmas.next(); } catch (_) {}"
HOOK_AFTER = "    curEl = el;\n"

TPL_RE = re.compile(r'(<script type="__bundler/template">)(.*?)(</script>)', re.S)


def main():
    remove = "--remove" in sys.argv
    src = LOOP.read_text(encoding="utf-8")
    m = TPL_RE.search(src)
    if not m:
        sys.exit("template block not found in loop.html")
    tpl = json.loads(m.group(2))

    # strip any previous copy
    tpl = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", tpl, flags=re.S)
    tpl = tpl.replace(HOOK_AFTER + "    " + HOOK + "\n", HOOK_AFTER)

    if not remove:
        if HOOK_AFTER not in tpl or "</body>" not in tpl:
            sys.exit("loop.html layout changed; hook points not found")
        tpl = tpl.replace(HOOK_AFTER, HOOK_AFTER + "    " + HOOK + "\n", 1)
        block = START + "\n<script>\n" + OVERLAY.read_text(encoding="utf-8") + "</script>\n" + END + "\n"
        tpl = tpl.replace("</body>", block + "</body>", 1)

    packed = "\n" + json.dumps(tpl).replace("/", "\\u002F") + "\n"
    out = src[: m.start(2)] + packed + src[m.end(2):]
    LOOP.write_text(out, encoding="utf-8")
    print(("removed from " if remove else "added to ") + str(LOOP.relative_to(ROOT)))


if __name__ == "__main__":
    main()
