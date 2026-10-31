# -*- coding: utf-8 -*-
"""web/app.template.html 에 엔진·모델·예시·검증결과를 넣어 단일 파일 web/index.html 생성
(정적 호스팅 어디서나 동작: GitHub Pages, Vercel, Netlify, 로컬 파일)"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()
tpl = rd("web", "app.template.html")
cases = json.loads(rd("data", "freetext_test.json"))
cases = [{k: c[k] for k in ("id", "lang", "title", "text")} for c in cases]
res = json.loads(rd("eval", "results.json"))
for k in ("memo_synth", "freetext", "blind"):
    res[k].pop("details", None)
res["clause"].pop("confusion", None)
safe = lambda s: s.replace("</", "<\\/")
html = (tpl.replace("__MODEL__", safe(rd("model", "carebridge_model.json")))
           .replace("__CASES__", safe(json.dumps(cases, ensure_ascii=False)))
           .replace("__RESULTS__", safe(json.dumps(res, ensure_ascii=False)))
           .replace("__ENGINE__", rd("web", "engine.js")))
open(os.path.join(ROOT, "web", "index.html"), "w", encoding="utf-8").write(html)
# 독립 실행용(브라우저에서 바로 열 수 있는 완전한 HTML 문서)
full = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0">' + html + "</body></html>"
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8").write(full)
print("built web/index.html", len(html) // 1024, "KB; docs/index.html (GitHub Pages)")
