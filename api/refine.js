/*
 * [선택·실험] 생성형 AI 문장 다듬기 엔드포인트 (Vercel/Netlify 서버리스 함수 형식)
 * - 입력: 엔진이 만든 근거 연결 초안 { clauses:[{i,text}], draft:[{text,src}] }
 * - 출력: 다듬은 문장 [{text, src}] — 반드시 기존 src(원문 절 번호)를 유지
 * - 클라이언트는 CareBridgeEngine.verifyExternalDraft()로 근거·금지표현을 다시 검사하고 통과한 문장만 채택
 * - 환경변수: LLM_API_URL (OpenAI 호환 chat/completions 엔드포인트), LLM_API_KEY, (선택) LLM_MODEL
 *   OpenAI 호환 인터페이스를 제공하는 상용·오픈소스 모델 서버 어디에나 연결할 수 있습니다.
 * 시연판(docs/index.html)은 이 기능을 사용하지 않으며, 메모를 외부로 전송하지 않습니다.
 * 실사용 시에는 외부 모델 전송 여부에 대한 기관 동의·개인정보 처리 근거를 먼저 확정해야 합니다.
 */
const SYSTEM = `당신은 장기요양 기관의 기록 문장 교정 보조자입니다.
규칙:
1) 입력된 초안 문장의 사실만 사용합니다. 새로운 사실·수치·시점·원인을 추가하지 않습니다.
2) 진단, 처방, 질환명, 위험도 판단, 추정 표현을 쓰지 않습니다.
3) '확인 필요', '미확인'은 그대로 유지합니다.
4) 각 문장의 src 배열(원문 절 번호)을 그대로 유지합니다.
5) 출력은 JSON 배열만: [{"text": "...", "src": [1]}]`;

module.exports = async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const url = process.env.LLM_API_URL, key = process.env.LLM_API_KEY;
  if (!url || !key) return res.status(501).json({ error: "LLM_API_URL / LLM_API_KEY not configured" });
  const { draft } = req.body || {};
  if (!Array.isArray(draft) || !draft.length) return res.status(400).json({ error: "draft required" });
  const r = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: "Bearer " + key },
    body: JSON.stringify({
      model: process.env.LLM_MODEL || "default",
      max_tokens: 800,
      temperature: 0,
      messages: [{ role: "system", content: SYSTEM }, { role: "user", content: JSON.stringify(draft) }],
    }),
  });
  if (!r.ok) return res.status(502).json({ error: "LLM request failed", status: r.status });
  const data = await r.json();
  const text = ((data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "").trim();
  let sentences;
  try { sentences = JSON.parse(text.slice(text.indexOf("["), text.lastIndexOf("]") + 1)); }
  catch (e) { return res.status(502).json({ error: "LLM output not JSON" }); }
  return res.status(200).json({ sentences });
};
