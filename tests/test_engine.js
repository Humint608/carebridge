/* 엔진 단위 테스트: node tests/test_engine.js */
const fs = require("fs"), path = require("path"), assert = require("assert");
const E = require(path.join(__dirname, "..", "web", "engine.js"));
const model = new E.Model(JSON.parse(fs.readFileSync(path.join(__dirname, "..", "model", "carebridge_model.json"))));
let n = 0; const t = (name, fn) => { fn(); n++; console.log("✓", name); };

t("제안서 예시(한국어): 식사 절반·무릎 불편·복약 미확인", () => {
  const r = E.analyze("점심을 절반 드셨고 무릎이 불편하다고 말씀하셨습니다. 복약 여부는 확인하지 못했습니다.", "ko", model);
  const got = r.clauses.map((c) => c.cls + ":" + c.label);
  assert.deepStrictEqual(got, ["MEAL:HALF", "DISCOMFORT:KNEE", "MEDICATION:NOT_CONFIRMED"]);
  assert.ok(r.checks.some((c) => c.field === "복약"));
});
t("성조 없는 베트남어 입력", () => {
  const r = E.analyze("ba an het com trua. ba noi dau lung", "vi", model);
  assert.strictEqual(r.clauses[0].label, "ALL"); assert.strictEqual(r.clauses[1].label, "BACK");
});
t("원문에 없는 방문 시각은 채우지 않음", () => {
  const r = E.analyze("Nenek tidur nyenyak semalam.", "id", model);
  assert.ok(r.checks.some((c) => c.field === "방문 시점"));
  assert.ok(!r.draft.some((d) => /\d{2}:\d{2}/.test(d.text)));
});
t("모든 초안 문장은 원문 근거 번호를 가짐", () => {
  const r = E.analyze("Soat 9 da keldim. Bobo nonushtani to'liq yedi. Buvi yiqilib tushdi.", "uz", model);
  assert.ok(r.guard.grounded); assert.strictEqual(r.guard.blocked.length, 0);
  assert.ok(r.alerts.length === 1);
});
t("개인정보 가림: 이름·전화번호, 일반 단어는 유지", () => {
  const m = E.maskPII("김순자 어르신 010-1234-5678. Bà ăn cơm. Bà Lan bị ngã.");
  assert.ok(!m.text.includes("김순자") && !m.text.includes("010-1234-5678") && !m.text.includes("Lan"));
  assert.ok(m.text.includes("Bà ăn"));
});
t("외부 생성형 문장 검증: 근거 없음·의료판단 표현 거부", () => {
  const clauses = [{ i: 1 }, { i: 2 }];
  const v = E.verifyExternalDraft([{ text: "점심 절반 섭취.", src: [1] }, { text: "관절염 의심됨.", src: [2] }, { text: "혈압 정상.", src: [] }], clauses);
  assert.deepStrictEqual(v.map((x) => x.accepted), [true, false, false]);
});
t("시각 추출(5개 언어)", () => {
  assert.strictEqual(E.extractTime("오후 2시 방문"), "14:00");
  assert.strictEqual(E.extractTime("बिहान ९ बजे पुगेँ"), "09:00");
  assert.strictEqual(E.extractTime("Tiba pukul 14.00"), "14:00");
});
console.log(`\n${n}개 테스트 통과`);
