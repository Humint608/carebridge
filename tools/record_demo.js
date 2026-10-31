/*
 * 데모 시연 영상 자동 녹화 (Playwright) — 실제 시제품을 조작하며 자막을 띄워 녹화
 * 실행: node tools/record_demo.js  → demo/raw.webm  (ffmpeg로 mp4 변환)
 */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
const ROOT = path.join(__dirname, "..");
const OUT = path.join(ROOT, "demo");
fs.mkdirSync(OUT, { recursive: true });
const W = 1280, H = 800;

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: OUT, size: { width: W, height: H } }, colorScheme: "light", deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto("file://" + path.join(ROOT, "docs", "index.html"));
  await p.addStyleTag({ content: `
    #cap{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);max-width:1040px;background:rgba(14,22,19,.9);color:#fff;font:600 21px/1.5 "IBM Plex Sans KR","Noto Sans CJK KR",sans-serif;padding:12px 22px;border-radius:12px;z-index:99;text-align:center;transition:opacity .25s}
    #cap small{display:block;font-weight:400;font-size:15px;opacity:.85}
    #cur{position:fixed;width:22px;height:22px;border-radius:50%;background:rgba(27,106,85,.35);border:2px solid #1B6A55;z-index:100;pointer-events:none;left:640px;top:400px;transition:left .55s ease,top .55s ease,transform .15s}
    #card{position:fixed;inset:0;background:#0F1F19;color:#fff;z-index:200;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:14px;font-family:"IBM Plex Sans KR","Noto Sans CJK KR",sans-serif;text-align:center;transition:opacity .5s}
    #card h1{font-size:46px;margin:0}#card p{font-size:21px;margin:0;opacity:.85;max-width:900px;line-height:1.6}#card .k{font-size:15px;opacity:.6}` });
  await p.evaluate(() => { const c = document.createElement("div"); c.id = "cap"; c.style.opacity = 0; document.body.appendChild(c); const u = document.createElement("div"); u.id = "cur"; document.body.appendChild(u); });
  const wait = (ms) => p.waitForTimeout(ms);
  const cap = async (t, sub, ms = 3200) => { await p.evaluate(([t, s]) => { const c = document.getElementById("cap"); c.innerHTML = t + (s ? "<small>" + s + "</small>" : ""); c.style.opacity = 1; }, [t, sub || ""]); await wait(ms); };
  const capOff = () => p.evaluate(() => (document.getElementById("cap").style.opacity = 0));
  const card = async (h, t, k, ms) => { await p.evaluate(([h, t, k]) => { let c = document.getElementById("card"); if (!c) { c = document.createElement("div"); c.id = "card"; document.body.appendChild(c); } c.style.opacity = 1; c.style.display = "flex"; c.innerHTML = `<h1>${h}</h1><p>${t}</p><div class="k">${k}</div>`; }, [h, t, k]); await wait(ms); await p.evaluate(() => { const c = document.getElementById("card"); c.style.opacity = 0; setTimeout(() => (c.style.display = "none"), 500); }); await wait(600); };
  const move = async (sel, nth = 0) => { const el = p.locator(sel).nth(nth); await el.scrollIntoViewIfNeeded(); const b = await el.boundingBox(); await p.evaluate(([x, y]) => { const u = document.getElementById("cur"); u.style.left = x - 11 + "px"; u.style.top = y - 11 + "px"; }, [b.x + b.width / 2, b.y + b.height / 2]); await wait(650); return el; };
  const click = async (sel, nth = 0) => { const el = await move(sel, nth); await p.evaluate(() => { const u = document.getElementById("cur"); u.style.transform = "scale(.7)"; setTimeout(() => (u.style.transform = ""), 160); }); await el.click(); await wait(500); };
  const scrollTo = (y) => p.evaluate((y) => window.scrollTo({ top: y, behavior: "smooth" }), y);

  // 0. 오프닝
  await card("케어브릿지 CareBridge", "외국인 돌봄인력의 다국어 관찰메모를<br>원문 근거가 연결된 한국어 기록 초안으로", "2026 AI 라이프 솔루션 챌린지 · 아이디어 13번 「케어브릿지」 구현 · 합성 데이터 시연", 4000);
  await cap("요양보호사 65.4만 명, 2033년까지 33.2만 명 추가 필요", "외국인 돌봄인력은 늘지만, 짧고 비정형적인 관찰 메모는 담당자의 재질문·재작성으로 이어집니다", 4600);
  await move(".side nav a", 0); await cap("요양보호사 · 기관 담당자 · 교육기관이 한 작업공간을 씁니다", "왼쪽 메뉴로 역할별 화면을 오가고, 상단에서 확인 필요 항목을 확인합니다", 4000);

  // 1. 작성 — 베트남어 (제안서 예시)
  await cap("① 요양보호사가 모국어로 짧게 메모합니다", "화면 문구도 작성자의 언어로 바뀝니다 · 지금은 베트남어", 3400);
  await move(".device"); await cap("요양보호사용 모바일 앱 화면", "", 2200); await move("#memo"); await cap("제안서 예시 문장: 점심 절반 · 무릎 불편 · 복약은 확인하지 못함", "", 3000);
  await click("#runBtn");
  await move("#result .pipe"); await cap("개인정보 가림 → 절 분리 → 항목 분류 → 근거 연결 → 가드레일", "원문의 절마다 기록 항목과 세부값을 판단하고 근거를 연결합니다", 4200);
  await move("#result .clause", 0); await cap("노란 표시는 AI가 판단의 근거로 삼은 단어입니다", "'một nửa'(절반) → 식사 · 절반 섭취", 3800);
  await move("#result .clause", 2); await cap("'복약 미확인'은 '복용'으로 채우지 않고 그대로 둡니다", "확인하지 않은 사실을 AI가 추정하지 않는 것이 제안자의 원칙입니다", 4000);
  await scrollTo(380); await wait(700);
  await cap("한국어 초안의 모든 문장에 원문 번호(①②③)가 붙습니다", "근거 없는 문장 0건 · 의료 판단 표현 0건 — 진단·처방·위험판정은 하지 않습니다", 4400);
  await scrollTo(0); await wait(500);

  // 2. 성조 없는 베트남어 직접 입력
  await capOff();
  await p.fill("#memo", "");
  await move("#memo");
  await p.type("#memo", "10h den nha. ba an het com trua. ba noi dau lung. toi giup ba tam", { delay: 38 });
  await cap("스마트폰에서 성조 부호 없이 입력해도 인식합니다", "", 2200);
  await click("#runBtn"); await move("#result .clause", 1);
  await cap("10:00 방문 · 점심 전량 섭취 · 허리 불편 · 목욕 지원", "현장 입력 습관을 학습 데이터 증강에 반영했습니다", 4200);

  // 3. 네팔어 · 우즈베크어
  await click('#langChips [data-l="ne"]'); await cap("네팔어", "데바나가리 문자 · 숫자 시각까지 처리", 3000);
  await click('#langChips [data-l="uz"]'); await cap("우즈베크어 · 인도네시아어 · 한국어까지 5개 언어", "한국어는 현장 축약체(드심·하심)도 지원합니다", 3200);
  await click('#langChips [data-l="id"]');
  await p.selectOption("#sampleSel", "F-id-04"); await wait(900);
  await move("#result .pipe"); await cap("이름·전화번호는 분석 전에 자동으로 가립니다", "Nenek Siti → Nenek ○○ · 0812-… → [전화번호]", 4000);
  await move("#result .clause", 0); await cap("낙상 기재는 '즉시 보고' 확인 항목으로 넘깁니다", "", 3000);
  await scrollTo(400); await wait(400);
  await click("#sendBtn"); await wait(400);

  // 4. 검토·승인
  await click("#bellBtn"); await move("#notif [data-n]", 0); await cap("상단 알림에서 확인 필요 항목을 바로 열 수 있습니다", "항목을 누르면 해당 기록의 검토 화면으로 이동합니다", 3600);
  await click('.side nav a[data-v="review"]'); await wait(500);
  await move("#kpi"); await cap("② 담당자 대시보드: 검토 대기 · 승인 · 확인 필요 · 즉시 보고", "", 3000);
  await cap("원문과 초안을 나란히 대조합니다", "", 2600);
  await move(".doc .src", 0); await cap("번호에 마우스를 올리면 해당 원문 절이 강조됩니다", "", 3200);
  await move(".doc .src", 1); await wait(900);
  await move("#apBtn"); await cap("확인 항목을 모두 처리하기 전에는 승인할 수 없습니다", "", 3000);
  const n = await p.locator("#reviewMain [data-done]:not([disabled])").count();
  for (let k = 0; k < n; k++) { const sel = "#reviewMain [data-done]:not([disabled])"; if (k === 1) { await move("[data-note]", 0); await p.fill("[data-note]", "보호자 통화로 오전 방문 시각 확인"); } await click(sel, 0); }
  await cap("담당자의 확인 메모와 수정 이력이 함께 남습니다", "", 2800);
  const inp = p.locator(".doc td input").first(); await move(".doc td input", 0);
  await click("#apBtn"); await cap("승인 완료", "", 2000);
  await click("#famBtn"); await move(".family"); await cap("가족 안내문은 승인된 값만으로, 승인 후에만 만들어집니다", "발송은 기관의 공유 권한 확인 후 기관 시스템에서 진행합니다", 4800);

  // 5. 교육
  await click('.side nav a[data-v="train"]'); await wait(600);
  await cap("③ 교육기관: 상황 카드를 보고 기록을 연습합니다", "E-7 유학생 요양보호사 양성 과정의 기록·인수인계 교육", 3600);
  await click('#trainLang [data-l="vi"]');
  await move("#trainMemo");
  await p.type("#trainMemo", "Bà ăn được một nửa bữa trưa. Bà kêu đau đầu gối.", { delay: 32 });
  await click("#gradeBtn"); await move("#trainOut");
  await cap("빠진 핵심 사실을 바로 알려 줍니다", "복약 확인 여부가 빠졌다는 피드백", 4000);
  await click("#exBtn"); await cap("모범 메모로 3/3 확인", "", 2800);

  // 6. 검증
  await click('.side nav a[data-v="model"]'); await wait(600);
  await cap("④ AI 검증 결과 — 웹과 동일한 엔진 코드로 측정", "블라인드 자유서술 15건: 정밀도 97.1% · 재현율 91.7% · 미확인 복약 오처리 0건", 5200);
  await scrollTo(360); await wait(800);
  await cap("평가 세트별 정밀도·재현율과 언어별 분류 정확도", "", 4200);
  await scrollTo(800); await wait(600);
  await cap("5개 언어 · 근거 연결 · 확인 필요 · 담당자 승인", "", 3400);
  await capOff();
  await card("케어브릿지", "AI가 쓰고, 사람이 확인하고, 근거가 남는 돌봄 기록", "humint608.github.io/carebridge · github.com/Humint608/carebridge", 4200);
  await ctx.close(); await browser.close();
  const f = fs.readdirSync(OUT).filter((x) => x.endsWith(".webm")).map((x) => path.join(OUT, x)).sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
  fs.renameSync(f, path.join(OUT, "raw.webm"));
  console.log("recorded", path.join(OUT, "raw.webm"));
})();
