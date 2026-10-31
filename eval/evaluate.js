/*
 * CareBridge 검증 스크립트 — 웹 시제품과 "동일한" engine.js로 평가
 * 실행: node eval/evaluate.js   → eval/results.json, eval/REPORT.md
 *
 * 평가 1) 특징 추출 정합성(Python 학습 ↔ JS 추론)
 * 평가 2) 절 단위: 학습에 쓰지 않은 문형(held-out template)에서 항목·세부값 정확도
 * 평가 3) 메모 단위(합성 300건): 절 분리 포함 엔드투엔드 필드 정밀도/재현율
 * 평가 4) 자유서술 현장형 25건(템플릿과 무관하게 별도 작성): 질의답변서의 검증 지표
 *         - 중요한 사실의 누락률, 원문에 없는 사실 추가율, 잘못된 보류 해제(미확인→복용), 개인정보 마스킹 재현율
 */
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const E = require(path.join(ROOT, "web", "engine.js"));
const model = new E.Model(JSON.parse(fs.readFileSync(path.join(ROOT, "model", "carebridge_model.json"))));
const jl = (p) => fs.readFileSync(p, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const R = {};

// 1) parity
const ref = JSON.parse(fs.readFileSync(path.join(ROOT, "eval", "parity_ref.json"), "utf8"));
let same = 0;
ref.forEach((r) => { const f = E.featurize(r.text, model.dim).idx; if (JSON.stringify(f) === JSON.stringify(r.idx)) same++; });
R.parity = { checked: ref.length, identical: same };

// 2) clause-level held-out
const held = jl(path.join(ROOT, "data", "clauses_heldout.jsonl"));
const per = {}; const langs = ["ko", "vi", "ne", "id", "uz"];
function acc(key, ok) { per[key] = per[key] || [0, 0]; per[key][0] += ok ? 1 : 0; per[key][1]++; }
const conf = {};
held.forEach((r) => {
  const f = E.featurize(r.text, model.dim);
  const pc = model.predict("cls", f);
  acc("cls", pc.label === r.cls); acc("cls_" + r.lang, pc.label === r.cls);
  conf[r.cls] = conf[r.cls] || {}; conf[r.cls][pc.label] = (conf[r.cls][pc.label] || 0) + 1;
  if (r.label && model.heads[r.cls]) { const ps = model.predict(r.cls, f); acc("sub", ps.label === r.label); acc("sub_" + r.cls, ps.label === r.label); acc("sub_" + r.lang, ps.label === r.label); }
  if (r.cls === "MEAL") { acc("meal_time", model.predict("MEAL_TIME", f).label === r.meal_time); }
});
const pct = (a) => (a ? +(100 * a[0] / a[1]).toFixed(1) : null);
R.clause = { n: held.length, cls_acc: pct(per.cls), sub_acc: pct(per.sub), meal_time_acc: pct(per.meal_time),
  by_lang: Object.fromEntries(langs.map((l) => [l, { cls: pct(per["cls_" + l]), sub: pct(per["sub_" + l]) }])),
  by_field: Object.fromEntries(Object.keys(per).filter((k) => k.startsWith("sub_") && !langs.includes(k.slice(4))).map((k) => [k.slice(4), pct(per[k])])),
  confusion: conf };

// field matcher
function predFields(res) {
  return res.clauses.filter((c) => c.status === "ok").map((c) => ({ cls: c.cls, label: c.cls === "VISIT" ? null : c.label, meal_time: c.cls === "MEAL" ? c.mealTime : null }));
}
function key(f, strict) { return f.cls + "|" + (f.cls === "VISIT" ? "" : f.label) + (strict && f.cls === "MEAL" ? "|" + f.meal_time : ""); }
function score(set) {
  let tp = 0, fp = 0, fn = 0, holds = 0, falseRelease = 0, nGold = 0, nPred = 0, n = 0, ms = 0;
  const details = [];
  set.forEach((m) => {
    const res = E.analyze(m.text, m.lang, model); n++; ms += res.ms;
    const pred = predFields(res).map((f) => key(f, true));
    const gold = m.gold.map((g) => key({ cls: g.cls, label: g.label || null, meal_time: g.meal_time || null }, true));
    holds += res.guard.holds; nGold += gold.length; nPred += pred.length;
    const g = gold.slice(); let mtp = 0;
    const fps = [];
    pred.forEach((p) => { const i = g.indexOf(p); if (i >= 0) { g.splice(i, 1); tp++; mtp++; } else { fp++; fps.push(p); } });
    fn += g.length;
    if (m.gold.some((x) => x.label === "NOT_CONFIRMED") && pred.includes("MEDICATION|TAKEN")) falseRelease++;
    details.push({ id: m.id, lang: m.lang, ok: g.length === 0 && fps.length === 0, missed: g, added: fps, holds: res.guard.holds, grounded: res.guard.grounded, blocked: res.guard.blocked.length });
  });
  const P = tp / Math.max(1, tp + fp), Rc = tp / Math.max(1, tp + fn);
  return { memos: n, gold_fields: nGold, pred_fields: nPred, precision: +(100 * P).toFixed(1), recall: +(100 * Rc).toFixed(1), f1: +(200 * P * Rc / Math.max(1e-9, P + Rc)).toFixed(1),
    added_rate: +(100 * fp / Math.max(1, nPred)).toFixed(1), missed_rate: +(100 * fn / Math.max(1, nGold)).toFixed(1), holds, false_release: falseRelease,
    perfect_memos: details.filter((d) => d.ok).length, all_grounded: details.every((d) => d.grounded), blocked_terms: details.reduce((a, d) => a + d.blocked, 0), avg_ms: +(ms / n).toFixed(1), details };
}
R.memo_synth = score(jl(path.join(ROOT, "data", "memos_synth.jsonl")));
const free = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "freetext_test.json"), "utf8"));
R.freetext = score(free);
R.freetext.by_lang = Object.fromEntries(langs.map((l) => { const s = score(free.filter((m) => m.lang === l)); return [l, { precision: s.precision, recall: s.recall, perfect: s.perfect_memos + "/" + s.memos }]; }));
delete R.freetext.by_lang_details;
const blind = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "blind_test.json"), "utf8"));
R.blind = score(blind);
// PII
let piiGold = 0, piiHit = 0;
free.forEach((m) => { (m.pii || []).forEach((v) => { piiGold++; const res = E.maskPII(m.text); if (!res.text.includes(v)) piiHit++; }); });
let fpMask = 0, nTexts = 0;
free.concat(blind).forEach((m) => { nTexts++; E.maskPII(m.text).spans.forEach((sp) => { if (!(m.pii || []).some((v) => v.includes(sp.value) || sp.value.includes(v))) fpMask++; }); });
R.pii = { gold: piiGold, masked: piiHit, recall: +(100 * piiHit / Math.max(1, piiGold)).toFixed(1), false_masks: fpMask, texts: nTexts };
R.model = { version: model.version, dim: model.dim, heads: Object.keys(model.heads).length, size_kb: Math.round(fs.statSync(path.join(ROOT, "model", "carebridge_model.json")).size / 1024) };

fs.writeFileSync(path.join(ROOT, "eval", "results.json"), JSON.stringify(R, null, 1));
const f = R.freetext, s = R.memo_synth;
console.log("parity", R.parity, "\nclause", { cls: R.clause.cls_acc, sub: R.clause.sub_acc, meal_time: R.clause.meal_time_acc, by_lang: R.clause.by_lang },
  "\nmemo_synth", { P: s.precision, R: s.recall, F1: s.f1, added: s.added_rate, missed: s.missed_rate, holds: s.holds, perfect: s.perfect_memos },
  "\nfreetext", { P: f.precision, R: f.recall, F1: f.f1, added: f.added_rate, missed: f.missed_rate, holds: f.holds, false_release: f.false_release, perfect: f.perfect_memos, grounded: f.all_grounded, blocked: f.blocked_terms, ms: f.avg_ms }, f.by_lang,
  "\npii", R.pii);
const b = R.blind; console.log("BLIND", { P: b.precision, R: b.recall, F1: b.f1, added: b.added_rate, missed: b.missed_rate, holds: b.holds, false_release: b.false_release, perfect: b.perfect_memos + "/" + b.memos });
console.log("blind errors:", JSON.stringify(b.details.filter((d) => !d.ok)));
console.log("freetext errors:", JSON.stringify(f.details.filter((d) => !d.ok), null, 0));
