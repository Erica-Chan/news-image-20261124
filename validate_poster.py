#!/usr/bin/env python3
"""Local gate validator for news-image-20261124. Fails loudly on any gap;
submit only when it reports 0 failures. Run from the repo directory."""
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# --- image ---------------------------------------------------------------
p = os.path.join(REPO, "entry.png")
check("entry.png exists", os.path.exists(p))
if os.path.exists(p):
    from PIL import Image
    im = Image.open(p)
    check("entry.png is 1024x1024", im.size == (1024, 1024), str(im.size))
    check("entry.png <= 1 MiB", os.path.getsize(p) <= 1024 * 1024,
          f"{os.path.getsize(p)} bytes")
    check("entry.png is PNG", im.format == "PNG")

# --- determinism: compose twice + main.ts twice ---------------------------
outs = []
for i in range(2):
    r = subprocess.run([sys.executable, "compose_poster.py"], cwd=REPO,
                       capture_output=True, text=True, timeout=120)
    check(f"compose_poster.py run {i + 1}", r.returncode == 0,
          r.stderr.strip()[-200:])
    outs.append(sha256(p))
check("compose_poster.py deterministic (two runs identical)",
      outs[0] == outs[1], f"{outs[0][:12]} vs {outs[1][:12]}")

main_outs = []
for d in ("/tmp/val24-out1", "/tmp/val24-out2"):
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ, MAKEFUN_OUTPUT_DIR=d)
    r = subprocess.run(["node", "main.ts"], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=60)
    check(f"main.ts runs ({d})", r.returncode == 0, r.stderr.strip()[:200])
    f = os.path.join(d, "entry.png")
    main_outs.append(sha256(f) if os.path.exists(f) else None)
check("main.ts deterministic (two runs identical)",
      main_outs[0] is not None and main_outs[0] == main_outs[1])
check("main.ts output == committed entry.png",
      main_outs[0] is not None and main_outs[0] == sha256(p))

# --- stories.json: every story dated 24 Nov 2026, sourced, badged ---------
data = json.load(open(os.path.join(REPO, "stories.json")))
stories = data["stories"]
check("stories.json date is 2026-11-24", data.get("date") == "2026-11-24")
check("38 stories", len(stories) == 38, str(len(stories)))
nums = sorted(s["n"] for s in stories)
check("story numbers 1..38, no gaps", nums == list(range(1, 39)))
regions = sorted({s["region"] for s in stories})
check("9 regions", len(regions) == 9, ", ".join(regions))
kinds = {"lead": 0, "medium": 0, "also": 0}
for s in stories:
    kinds[s.get("kind", "also")] += 1
check("3 leads + 13 mediums + 22 also-on",
      kinds == {"lead": 3, "medium": 13, "also": 22}, str(kinds))
CERT = {"CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM", "PENDING", "FORECAST"}
bad_cert = [s["n"] for s in stories if s.get("certainty") not in CERT]
bad_src = [s["n"] for s in stories if not s.get("source")]
check("every story has a certainty label", not bad_cert, str(bad_cert))
check("every story has a source", not bad_src, str(bad_src))
check("every card story has lat/lon for the map",
      all("lat" in s and "lon" in s for s in stories
          if s.get("kind") in ("lead", "medium")))
check("6 big numbers", len(data.get("numbers", [])) == 6)
check("UTC timeline present", len(data.get("timeline", [])) >= 5)
check("date check names exclusions", "Left out" in data.get("date_check", "")
      and "Not yet" in data.get("date_check", ""))
placeholders = ("TODO", "Lorem", "XXX", "TBD", "placeholder")
src_text = open(os.path.join(REPO, "compose_poster.py")).read()
check("no placeholder text in composer",
      not any(t in src_text for t in placeholders))

# --- repo files --------------------------------------------------------------
for f in ["main.ts", "compose_poster.py", "stories.json", "entry.png",
          "README.md", "LICENSE", "package.json", ".makefun/owner.json"]:
    check(f"repo has {f}", os.path.exists(os.path.join(REPO, f)))
owner = json.load(open(os.path.join(REPO, ".makefun/owner.json")))
check("owner.json names make.fun wallet",
      owner.get("wallet") == "7s7sawBWUkxoGttCLFbrjsYJD8eq81ApX21nQLzskk8k")
lic = open(os.path.join(REPO, "LICENSE")).read()
check("LICENSE is MIT", lic.startswith("MIT License"))
readme = open(os.path.join(REPO, "README.md")).read()
check("README has make.fun badges + bounty link",
      "make.fun/bounty/news-image-20261124" in readme
      and "badge/news-image-20261124" in readme)
check("README states 38 stories / 9 regions",
      "38 stories" in readme and "9 regions" in readme)
main_ts = open(os.path.join(REPO, "main.ts")).read()
check("main.ts is Node stdlib-only copy",
      "copyFileSync" in main_ts and "fetch(" not in main_ts)
check("no AI hero images in repo",
      not any(os.path.exists(os.path.join(REPO, f))
              for f in ("hero.png", "hero2.png")))

print(f"\n{len(failures)} failures")
sys.exit(1 if failures else 0)
