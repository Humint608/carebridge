/*!
 * CareBridge Engine v1.0 — 다국어 돌봄 관찰메모 → 한국어 구조화 기록 초안
 * 온디바이스(브라우저/Node) 추론. 외부 서버 전송 없음.
 *  1) PII 마스킹  2) 절 분리  3) 다중헤드 분류(학습 모델)  4) 근거 연결·확인필요 생성
 *  5) 한국어 초안 렌더링  6) 가드레일(근거 대조·의료판단 표현 차단·저신뢰 보류)
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CareBridgeEngine = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /* ---------- 1. 특징 추출 (model/features.py 와 동일 규칙) ---------- */
  var APOS = /[ʻ’`‘ʼ]/g, PUNCT = /[.,!?;:"()\[\]।]/g, WS = /\s+/g;
  function normalize(text) {
    var t = text.toLowerCase().replace(APOS, "'");
    t = t.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d").normalize("NFC");
    return t.replace(PUNCT, " ").replace(WS, " ").trim();
  }
  function fnv1a(s) {
    var h = 2166136261 >>> 0;
    for (var ch of s) { h = Math.imul((h ^ ch.codePointAt(0)) >>> 0, 16777619) >>> 0; }
    return h >>> 0;
  }
  function featureKeys(text) {
    var t = normalize(text), keys = [];
    var chars = Array.from(" " + t + " ");
    for (var n = 2; n <= 4; n++)
      for (var i = 0; i + n <= chars.length; i++) keys.push("c" + chars.slice(i, i + n).join(""));
    t.split(" ").forEach(function (w) { if (w) keys.push("w" + w); });
    return keys;
  }
  function featurize(text, dim) {
    var set = new Set();
    featureKeys(text).forEach(function (k) { set.add(fnv1a(k) % dim); });
    var idx = Array.from(set).sort(function (a, b) { return a - b; });
    var v = idx.length ? 1 / Math.sqrt(idx.length) : 0;
    return { idx: idx, v: v };
  }

  /* ---------- 2. 모델 ---------- */
  function b64ToInt8(b64) {
    var bin = typeof atob === "function" ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
    var out = new Int8Array(bin.length);
    for (var i = 0; i < bin.length; i++) { var c = bin.charCodeAt(i); out[i] = c > 127 ? c - 256 : c; }
    return out;
  }
  function Model(json) {
    this.dim = json.dim; this.version = json.version; this.heads = {};
    for (var h in json.heads) {
      var H = json.heads[h];
      this.heads[h] = { labels: H.labels, scale: H.scale, bias: H.bias, w: b64ToInt8(H.w) };
    }
  }
  Model.prototype.predict = function (head, f) {
    var H = this.heads[head], k = H.labels.length, dim = this.dim, logits = [];
    for (var r = 0; r < k; r++) {
      var s = 0, off = r * dim;
      for (var j = 0; j < f.idx.length; j++) s += H.w[off + f.idx[j]];
      logits.push(s * H.scale[r] * f.v + H.bias[r]);
    }
    var m = Math.max.apply(null, logits), ex = logits.map(function (x) { return Math.exp(x - m); });
    var z = ex.reduce(function (a, b) { return a + b; }, 0), probs = ex.map(function (e) { return e / z; });
    var best = 0; for (var i = 1; i < k; i++) if (probs[i] > probs[best]) best = i;
    return { label: H.labels[best], prob: probs[best], probs: probs, row: best };
  };
  /* 단어별 판단 기여도(설명가능성): 해당 단어의 n-gram이 예측 라벨 점수에 기여한 양 */
  Model.prototype.wordEvidence = function (head, row, clauseText) {
    var H = this.heads[head], dim = this.dim, off = row * dim, out = [];
    var re = /\S+/g, m;
    while ((m = re.exec(clauseText))) {
      var keys = featureKeys(m[0]).filter(function (k) { return k.length > 3 || k[0] === "w"; });
      var s = 0, seen = new Set();
      keys.forEach(function (k) { var ix = fnv1a(k) % dim; if (!seen.has(ix)) { seen.add(ix); s += H.w[off + ix] * H.scale[row]; } });
      out.push({ word: m[0], start: m.index, end: m.index + m[0].length, score: s });
    }
    return out;
  };

  /* ---------- 3. 개인정보 마스킹 ---------- */
  var PII_RULES = [
    { type: "전화번호", re: /(?:\+?\d{1,3}[-\s]?)?0\d{1,3}[-\s]?\d{3,4}[-\s]?\d{4}/g },
    { type: "주민번호", re: /\d{6}[-\s]?[1-4]\d{6}/g },
    { type: "이름", re: /[가-힣]{2,4}(?=\s?(?:어르신|할머니|할아버지|님|씨))/g },
    { type: "이름", re: /\b(?:Bà|Ông|Cụ|Chị|Anh)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+)/g, group: 1 },
    { type: "이름", re: /\b(?:Nenek|Kakek|Ibu|Bapak|Oma|Opa)\s+([A-Z][a-z]+)/g, group: 1 },
    { type: "이름", re: /\b([A-Z][a-z]+(?:ova|ov|eva|ev))\b/g, group: 1 },
  ];
  function maskPII(text) {
    var spans = [];
    PII_RULES.forEach(function (r) {
      r.re.lastIndex = 0; var m;
      while ((m = r.re.exec(text))) {
        var val = r.group ? m[r.group] : m[0];
        if (r.group && val[0] === val[0].toLowerCase()) continue; // 대문자로 시작하는 고유명사만 (예: 'Bà ăn' 오탐 방지)
        var st = r.group ? m.index + m[0].indexOf(val, m[0].length - val.length - 0) : m.index;
        if (r.group) st = m.index + m[0].lastIndexOf(val);
        spans.push({ type: r.type, start: st, end: st + val.length, value: val });
      }
    });
    spans.sort(function (a, b) { return a.start - b.start; });
    var merged = [];
    spans.forEach(function (s) { if (!merged.length || s.start >= merged[merged.length - 1].end) merged.push(s); });
    var out = "", last = 0;
    merged.forEach(function (s) {
      out += text.slice(last, s.start) + (s.type === "이름" ? "○○" : s.type === "전화번호" ? "[전화번호]" : "[주민번호]");
      last = s.end;
    });
    out += text.slice(last);
    return { text: out, spans: merged };
  }

  /* ---------- 4. 절 분리 ---------- */
  var CONJ = { vi: /\s+và\s+|\s+va\s+/gi, id: /\s+dan\s+/gi, uz: /\s+va\s+/gi, ne: /\s+र\s+/g, ko: /\s+그리고\s+/g };
  function segment(text, lang) {
    var marks = [];
    var hard = /\.(?!\d)|(?<!\d)\.|[!?;।\n]|,(?!\d)|(?<!\d),/g, m;
    while ((m = hard.exec(text))) marks.push([m.index, m.index + m[0].length]);
    var cj = CONJ[lang]; if (cj) { cj.lastIndex = 0; while ((m = cj.exec(text))) marks.push([m.index, m.index + m[0].length]); }
    if (lang === "ko") {
      // 연결어미(-고/-며/-서) 뒤 공백을 절 경계로 사용 (어미는 앞 절에 남김)
      var kr = /(?<=[셨했었았였겠시하드셔해워])(?:고|며|서)\s+/g;
      while ((m = kr.exec(text))) marks.push([m.index + 1, m.index + m[0].length]);
    }
    marks.sort(function (a, b) { return a[0] - b[0]; });
    var out = [], pos = 0;
    marks.concat([[text.length, text.length]]).forEach(function (mk) {
      if (mk[0] < pos) return;
      var seg = text.slice(pos, mk[0]), lead = seg.length - seg.trimStart().length;
      var t = seg.trim();
      if (t.length >= 2) out.push({ text: t, start: pos + lead, end: pos + lead + t.length });
      pos = mk[1];
    });
    return out;
  }

  /* ---------- 5. 시각 추출 ---------- */
  var DEV = "०१२३४५६७८९";
  function devToAscii(s) { return s.replace(/[०-९]/g, function (d) { return String(DEV.indexOf(d)); }); }
  function extractTime(clause) {
    var s = devToAscii(clause), m, hh, mm = 0;
    var pm = /(오후|chiều|दिउँसो|sore)/.test(s);
    if ((m = s.match(/(\d{1,2})[:.h](\d{2})/))) { hh = +m[1]; mm = +m[2]; }
    else if ((m = s.match(/(\d{1,2})\s*(?:시|giờ|gio|h\b|बजे)(?:\s*(\d{1,2})\s*(?:분|phút|phut))?/))) { hh = +m[1]; mm = m[2] ? +m[2] : 0; }
    else if ((m = s.match(/(?:jam|pukul|soat|lúc|luc)\s*(\d{1,2})/i))) { hh = +m[1]; }
    else return null;
    if (pm && hh < 12) hh += 12;
    if (hh > 23 || mm > 59) return null;
    return pad(hh) + ":" + pad(mm);
  }
  function pad(x) { x = String(x); return x.length < 2 ? "0" + x : x; }

  /* ---------- 6. 한국어 표현 사전 ---------- */
  var KO = {
    cls: { VISIT: "방문 시점", SUPPORT: "제공한 지원", MEAL: "식사", SLEEP: "수면", DISCOMFORT: "불편감 표현", MEDICATION: "복약 관련 관찰", EXCRETION: "배변·배뇨", MOOD: "정서·의사소통", EVENT: "특이사항(사건)" },
    SUPPORT: { BATH: "목욕·세면 지원", WALK: "이동·보행 지원", DRESS: "옷 갈아입기 지원", MEAL_ASSIST: "식사 보조(떠먹임 등)", CLEAN: "환경 정리·세탁", REPOSITION: "체위 변경" },
    MEAL: { ALL: "전량 섭취", MOST: "대부분 섭취", HALF: "절반 섭취", LITTLE: "소량 섭취", NONE: "섭취 안 함", UNSPEC: "섭취함(양 미기재)" },
    MEAL_TIME: { BREAKFAST: "아침", LUNCH: "점심", DINNER: "저녁", SNACK: "간식", UNSPEC: "시점 미기재" },
    MEDICATION: { TAKEN: "복용 관찰됨", NOT_CONFIRMED: "복약 여부 미확인", REFUSED: "복약 거부 관찰" },
    SLEEP: { GOOD: "잘 주무심(본인·관찰)", POOR: "잠을 잘 못 주무심", WOKE: "밤중 여러 차례 깸" },
    DISCOMFORT: { KNEE: "무릎", BACK: "허리·등", HEAD: "머리", STOMACH: "배", LEG: "다리", SHOULDER: "어깨", CHEST: "가슴", UNSPEC: "부위 미특정" },
    MOOD: { GOOD: "기분 좋아 보임", LOW: "기운 없음·말수 적음", AGITATED: "불안·초조 또는 화냄" },
    EXCRETION: { NORMAL: "배변·배뇨 있음", NONE: "배변·배뇨 없음 또는 적음", LOOSE: "묽은 변" },
    EVENT: { FALL: "넘어짐(낙상) 원문 기재", NEAR_FALL: "넘어질 뻔함 원문 기재" },
  };
  /* 초안에 절대 나오면 안 되는 의료 판단·추정 표현 (가드레일) */
  var BLOCKED = ["진단", "처방", "의심됨", "질환", "관절염", "치매 악화", "고위험", "위험도", "투약 지시", "용량", "추정됨", "가능성이 높"];

  var TH = { cls: 0.55, sub: 0.5 };

  /* ---------- 7. 분석 파이프라인 ---------- */
  function analyze(rawText, lang, model) {
    var t0 = (typeof performance !== "undefined" ? performance.now() : Date.now());
    var pii = maskPII(rawText);
    var text = pii.text;
    var clauses = segment(text, lang).map(function (c, i) {
      var f = featurize(c.text, model.dim);
      var pc = model.predict("cls", f);
      var cl = { i: i + 1, text: c.text, start: c.start, end: c.end, cls: pc.label, clsProb: pc.prob, status: "ok" };
      if (pc.prob < TH.cls) { cl.status = "hold"; cl.holdReason = "항목 판단 신뢰도 낮음(" + Math.round(pc.prob * 100) + "%)"; }
      if (cl.cls === "VISIT") { cl.value = extractTime(c.text); }
      else if (model.heads[cl.cls]) {
        var ps = model.predict(cl.cls, f);
        cl.label = ps.label; cl.labelProb = ps.prob;
        if (ps.prob < TH.sub && cl.status === "ok") { cl.status = "hold"; cl.holdReason = "세부값 신뢰도 낮음(" + Math.round(ps.prob * 100) + "%)"; }
        var ev = model.wordEvidence(cl.cls, ps.row, c.text);
        var evc = model.wordEvidence("cls", pc.row, c.text);
        ev.forEach(function (e, k) { e.score += evc[k].score * 0.5; });
        cl.evidence = ev.filter(function (e) { return e.score > 0; }).sort(function (a, b) { return b.score - a.score; }).slice(0, 2);
        if (cl.cls === "MEAL") { var pt = model.predict("MEAL_TIME", f); cl.mealTime = pt.label; cl.mealTimeProb = pt.prob; }
      }
      return cl;
    });
    var rec = buildRecord(clauses);
    var t1 = (typeof performance !== "undefined" ? performance.now() : Date.now());
    return { lang: lang, raw: rawText, masked: text, pii: pii.spans, clauses: clauses, record: rec.fields, checks: rec.checks, alerts: rec.alerts, draft: rec.draft, guard: guard(rec, clauses), ms: Math.max(1, Math.round(t1 - t0)), modelVersion: model.version };
  }

  function buildRecord(clauses) {
    var F = { VISIT: [], SUPPORT: [], MEAL: [], SLEEP: [], DISCOMFORT: [], MEDICATION: [], EXCRETION: [], MOOD: [], EVENT: [] };
    var checks = [], alerts = [], draft = [];
    clauses.forEach(function (c) {
      if (c.status === "hold") { checks.push({ level: "hold", field: "판단 보류", text: "AI가 항목을 확정하지 않음 — 원문 " + circ(c.i) + " 직접 확인", src: [c.i] }); return; }
      F[c.cls].push(c);
    });
    // 방문 시점
    var v = F.VISIT.filter(function (c) { return c.value; })[0];
    if (v) draft.push({ text: v.value + " 방문(작성자 기재).", src: [v.i] });
    else checks.push({ level: "check", field: "방문 시점", text: "원문에 방문 시각이 없음 — 작성자에게 확인", src: [] });
    // 제공한 지원
    F.SUPPORT.forEach(function (c) { draft.push({ text: KO.SUPPORT[c.label] + " 제공.", src: [c.i] }); });
    // 식사
    F.MEAL.forEach(function (c) {
      var when = c.mealTime && c.mealTime !== "UNSPEC" ? KO.MEAL_TIME[c.mealTime] + " 식사" : "식사";
      draft.push({ text: when + " " + KO.MEAL[c.label] + " 관찰.", src: [c.i] });
      if (c.label === "LITTLE") checks.push({ level: "check", field: "식사", text: "'조금' 등 표현만 있음 — 실제 섭취량(정량) 확인", src: [c.i] });
      if (c.label === "UNSPEC") checks.push({ level: "check", field: "식사", text: "섭취량이 기재되지 않음 — 추정하지 않고 확인 필요", src: [c.i] });
      if (c.mealTime === "UNSPEC") checks.push({ level: "check", field: "식사", text: "어느 끼니인지 기재되지 않음 — 시점 확인", src: [c.i] });
    });
    F.SLEEP.forEach(function (c) { draft.push({ text: "수면: " + KO.SLEEP[c.label] + ".", src: [c.i] }); });
    F.DISCOMFORT.forEach(function (c) {
      draft.push({ text: KO.DISCOMFORT[c.label] + " 불편감을 본인이 표현함.", src: [c.i] });
      checks.push({ level: "check", field: "불편감", text: KO.DISCOMFORT[c.label] + " 불편 — 지속 여부·정도를 다음 방문 시 확인하고 기관 절차에 따라 보고", src: [c.i] });
    });
    F.MEDICATION.forEach(function (c) {
      draft.push({ text: KO.MEDICATION[c.label] + (c.label === "NOT_CONFIRMED" ? "(작성자가 확인하지 못함)." : "."), src: [c.i] });
      if (c.label === "NOT_CONFIRMED") checks.push({ level: "check", field: "복약", text: "복약 여부 미확인 — 담당자가 확인 후 기록 (AI는 복용 여부를 채우지 않음)", src: [c.i] });
      if (c.label === "REFUSED") checks.push({ level: "check", field: "복약", text: "복약 거부 관찰 — 기관 절차에 따라 담당자에게 보고", src: [c.i] });
    });
    if (!F.MEDICATION.length) checks.push({ level: "info", field: "복약", text: "복약 관련 기재 없음 — 해당 시 확인", src: [] });
    F.EXCRETION.forEach(function (c) { draft.push({ text: "배변·배뇨: " + KO.EXCRETION[c.label] + ".", src: [c.i] }); });
    F.MOOD.forEach(function (c) { draft.push({ text: "정서: " + KO.MOOD[c.label] + "(관찰).", src: [c.i] }); });
    F.EVENT.forEach(function (c) {
      draft.push({ text: "특이사항: " + KO.EVENT[c.label] + ".", src: [c.i] });
      alerts.push({ text: KO.EVENT[c.label] + " — 기관 사고보고 절차 대상인지 담당자가 즉시 판단", src: [c.i] });
    });
    return { fields: F, checks: checks, alerts: alerts, draft: draft };
  }

  function guard(rec, clauses) {
    var srcSet = new Set(clauses.map(function (c) { return c.i; }));
    var ungrounded = rec.draft.filter(function (d) { return !d.src.length || d.src.some(function (s) { return !srcSet.has(s); }); });
    var all = rec.draft.map(function (d) { return d.text; }).join(" ");
    var blocked = BLOCKED.filter(function (w) { return all.indexOf(w) >= 0; });
    var holds = clauses.filter(function (c) { return c.status === "hold"; }).length;
    return { grounded: ungrounded.length === 0, ungrounded: ungrounded.length, blocked: blocked, holds: holds, sentences: rec.draft.length };
  }

  /* LLM(선택) 결과 검증용: 외부 생성형 모델이 만든 문장도 동일한 근거 대조를 통과해야 채택 */
  function verifyExternalDraft(sentences, clauses) {
    var srcSet = new Set(clauses.map(function (c) { return c.i; }));
    return sentences.map(function (s) {
      var okSrc = Array.isArray(s.src) && s.src.length && s.src.every(function (x) { return srcSet.has(x); });
      var bad = BLOCKED.filter(function (w) { return (s.text || "").indexOf(w) >= 0; });
      return { text: s.text, src: s.src, accepted: !!okSrc && !bad.length, reason: !okSrc ? "근거 절 없음" : bad.length ? "의료판단 표현: " + bad.join(",") : "" };
    });
  }

  function circ(n) { return "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"[n - 1] || "(" + n + ")"; }

  return { normalize: normalize, fnv1a: fnv1a, featurize: featurize, featureKeys: featureKeys, Model: Model, maskPII: maskPII, segment: segment, extractTime: extractTime, analyze: analyze, verifyExternalDraft: verifyExternalDraft, KO: KO, BLOCKED: BLOCKED, circ: circ, TH: TH };
});
