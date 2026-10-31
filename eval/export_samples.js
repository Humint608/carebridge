/* 샘플 결과물 생성: 자유서술·블라인드 메모 40건의 실제 엔진 출력 → eval/sample_outputs.json, eval/SAMPLE_OUTPUTS.md */
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const E = require(path.join(ROOT, "web", "engine.js"));
const model = new E.Model(JSON.parse(fs.readFileSync(path.join(ROOT, "model", "carebridge_model.json"))));
const sets = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "freetext_test.json"))).concat(JSON.parse(fs.readFileSync(path.join(ROOT, "data", "blind_test.json"))));
const LN = { ko: "한국어", vi: "베트남어", ne: "네팔어", id: "인도네시아어", uz: "우즈베크어" };
const out = [], md = ["# 케어브릿지 샘플 결과물 (실제 엔진 출력)", "", "`node eval/export_samples.js`로 재생성됩니다. 모든 메모는 직접 작성한 합성 문장입니다.", ""];
sets.forEach((m) => {
  const r = E.analyze(m.text, m.lang, model);
  out.push({ id: m.id, lang: m.lang, input: m.text, masked: r.masked, clauses: r.clauses.map((c) => ({ n: c.i, text: c.text, item: E.KO.cls[c.cls], value: c.label || c.value || null, meal_time: c.mealTime || null, confidence: +(Math.min(c.clsProb, c.labelProb ?? 1)).toFixed(3), status: c.status, evidence_words: (c.evidence || []).map((e) => e.word) })), draft_ko: r.draft.map((d) => ({ text: d.text, source_clauses: d.src })), checks: r.checks, alerts: r.alerts, guard: r.guard });
  md.push(`## ${m.id} · ${LN[m.lang]}`, "", "**입력 원문**", "", "> " + m.text.replace(/\n/g, " "), "");
  if (r.pii.length) md.push(`개인정보 가림: ${r.pii.map((p) => p.type).join(", ")}`, "");
  md.push("| # | 원문 절 | 항목 | 판단 | 신뢰도 |", "|---|---|---|---|---|");
  r.clauses.forEach((c) => md.push(`| ${c.i} | ${c.text} | ${c.status === "hold" ? "판단 보류" : E.KO.cls[c.cls]} | ${c.status === "hold" ? c.holdReason : (c.label || c.value || "-") + (c.mealTime ? " / " + c.mealTime : "")} | ${Math.round(Math.min(c.clsProb, c.labelProb ?? 1) * 100)}% |`));
  md.push("", "**한국어 기록 초안**", "");
  r.draft.forEach((d) => md.push(`- ${d.text} ← 원문 ${d.src.map(E.circ).join("")}`));
  const ck = r.checks.filter((c) => c.level !== "info");
  if (ck.length || r.alerts.length) { md.push("", "**확인 필요 / 즉시 보고**", ""); r.alerts.forEach((a) => md.push("- [즉시 보고] " + a.text)); ck.forEach((c) => md.push(`- [${c.field}] ${c.text}`)); }
  md.push("", `가드레일: 근거 없는 문장 ${r.guard.ungrounded} · 의료 판단 표현 ${r.guard.blocked.length} · 보류 ${r.guard.holds}`, "");
});
fs.writeFileSync(path.join(ROOT, "eval", "sample_outputs.json"), JSON.stringify(out, null, 1));
fs.writeFileSync(path.join(ROOT, "eval", "SAMPLE_OUTPUTS.md"), md.join("\n"));
console.log("samples", out.length);
