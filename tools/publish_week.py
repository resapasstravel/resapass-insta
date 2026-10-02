"""Render a week JSON and write posts/ + daily/ files. Usage: python3 tools/publish_week.py tools/week-YYYY-MM-DD.json"""
import json, shutil, pathlib, subprocess, sys, tempfile
src = sys.argv[1]; root = pathlib.Path(__file__).resolve().parent.parent
base = "https://raw.githubusercontent.com/resapasstravel/resapass-insta/main"
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, str(root/"tools/render.py"), src, tmp], check=True)
for p in json.load(open(pathlib.Path(tmp)/"queue.json")):
    d = root/"posts"/p["date"]; d.mkdir(parents=True, exist_ok=True); urls = []
    for i, f in enumerate(p["images"], 1):
        shutil.copy(pathlib.Path(tmp)/f, d/f"{i}.jpg"); urls.append(f"{base}/posts/{p['date']}/{i}.jpg")
    (root/"daily").mkdir(exist_ok=True)
    json.dump({"date": p["date"], "type": p["type"], "photo_url": urls[0], "caption": p["caption"],
               "carousel": [{"media_type": "IMAGE", "url": u} for u in urls]},
              open(root/"daily"/f"{p['date']}.json", "w"), indent=2, ensure_ascii=False)
    print("ok", p["date"], p["type"], len(urls))
