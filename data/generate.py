# -*- coding: utf-8 -*-
"""
합성 관찰메모 데이터셋 생성기
- 절(clause) 단위 학습셋 / 템플릿 분리(held-out) 검증셋 / 메모(여러 절) 단위 셋 생성
- 템플릿마다 마지막 1개 문형을 검증용으로 분리하여, 학습 때 보지 못한 문형에서의 일반화 성능을 측정
- 증강: 베트남어 성조부호 제거(현장 스마트폰 입력 습관), 문장부호 생략, 소문자화
실행: python data/generate.py  → data/clauses_train.jsonl, data/clauses_heldout.jsonl, data/memos_synth.jsonl
"""
import json
import random
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(__file__))
from templates import *  # noqa

random.seed(20261031)
OUT = os.path.dirname(__file__)
DEV = "०१२३४५६७८९"


def strip_tone(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not (0x300 <= ord(c) <= 0x36F))
    return unicodedata.normalize("NFC", s).replace("đ", "d").replace("Đ", "D")


def rand_time(lang):
    hh = random.randint(8, 17)
    mm = random.choice([0, 0, 0, 30, 10, 40])
    if lang == "ko":
        return random.choice([f"{hh}시", f"오전 {hh}시" if hh < 12 else f"오후 {hh-12 if hh>12 else 12}시", f"{hh}:{mm:02d}", f"{hh}시 {mm}분" if mm else f"{hh}시"])
    if lang == "vi":
        return random.choice([f"{hh} giờ", f"{hh}h{mm:02d}" if mm else f"{hh}h", f"{hh}:{mm:02d}", f"{hh} giờ {mm} phút" if mm else f"{hh} giờ sáng" if hh < 12 else f"{hh} giờ chiều"])
    if lang == "ne":
        d = "".join(DEV[int(c)] for c in str(hh))
        return random.choice([d, str(hh), f"बिहान {d}" if hh < 12 else f"दिउँसो {d}"])
    if lang == "id":
        return random.choice([f"{hh}.{mm:02d}", f"{hh:02d}:{mm:02d}", f"{hh}"])
    if lang == "uz":
        return random.choice([f"{hh}:{mm:02d}", f"{hh}"])


def fill(tpl, lang, cls, extra=None):
    extra = extra or {}
    subj_pool = SUBJ_PLAIN if cls in ("SLEEP", "MOOD", "EXCRETION", "EVENT") else SUBJ
    s = random.choice(subj_pool[lang])
    o = random.choice(OBJ[lang])
    out = tpl.replace("{s}", s).replace("{s2}", o).replace("{s3}", o)
    for k, v in extra.items():
        out = out.replace("{" + k + "}", v)
    out = " ".join(out.split())
    if out and lang in ("vi", "id", "uz"):
        out = out[0].upper() + out[1:]
    return out


def gen_items(lang, holdout: bool):
    """(text, cls, label, sublabel) 생성. holdout=True면 각 목록의 마지막 문형만 사용"""
    pick = (lambda lst: lst[-1:]) if holdout else (lambda lst: lst[:-1] if len(lst) > 1 else lst)
    items = []
    # MEAL: 시점 x 양
    for amt, tpls in MEAL_AMT[lang].items():
        for tpl in pick(tpls):
            for tm, words in MEAL_TIME[lang].items():
                for w in words:
                    items.append((fill(tpl, lang, "MEAL", {"t": w}), "MEAL", amt, tm))
    for cls, table in (("MEDICATION", MED), ("SLEEP", SLEEP), ("MOOD", MOOD), ("EXCRETION", EXCR), ("EVENT", EVENT), ("SUPPORT", SUPPORT)):
        for lab, tpls in table[lang].items():
            for tpl in pick(tpls):
                items.append((fill(tpl, lang, cls), cls, lab, None))
    for tpl in pick(DISCOMFORT_T[lang]):
        for part, words in BODY[lang].items():
            for w in words:
                items.append((fill(tpl, lang, "DISCOMFORT", {"p": w}), "DISCOMFORT", part, None))
    if not holdout:  # 핵심 표현(anchor): 학습셋에만 추가
        for cls, table in ANCHOR.items():
            for lab, phrases in table[lang].items():
                for ph in phrases:
                    if cls == "MEAL":
                        for tm, words in MEAL_TIME[lang].items():
                            w = random.choice(words)
                            if lang == "ko":
                                items.append((f"{w.rstrip('을를')}은 {ph}" if tm != "UNSPEC" else ph, cls, lab, tm if tm != "UNSPEC" else "UNSPEC"))
                            else:
                                items.append((f"{ph} {w}", cls, lab, tm))
                    else:
                        subj = random.choice((SUBJ_PLAIN if cls in ("SLEEP", "MOOD", "EXCRETION", "EVENT") else SUBJ)[lang])
                        items.append((ph, cls, lab, None))
                        items.append((f"{subj} {ph}".strip(), cls, lab, None))
    for tpl in pick(VISIT[lang]):
        items.append((fill(tpl, lang, "VISIT", {"h": rand_time(lang)}), "VISIT", None, None))
    return items


def augment(text, lang):
    out = [text]
    if lang == "ko":
        short = text
        for a, b in KO_SHORT:
            if short.endswith(a):
                short = short[: -len(a)] + b
                break
        if short != text:
            out.append(short)
    if lang == "vi":
        out.append(strip_tone(text))
    if random.random() < 0.5:
        out.append(text.lower())
    return out


def build_clause_set(holdout, reps):
    rows = []
    for lang in LANGS:
        for _ in range(reps):
            for text, cls, lab, sub in gen_items(lang, holdout):
                for t in augment(text, lang):
                    rows.append({"lang": lang, "text": t, "cls": cls, "label": lab, "meal_time": sub})
    # 중복 제거
    seen, uniq = set(), []
    for r in rows:
        k = (r["lang"], r["text"], r["cls"], r["label"], r["meal_time"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    random.shuffle(uniq)
    return uniq


def build_memos(n_per_lang=60):
    """여러 절을 이어붙인 메모(엔드투엔드 평가용, held-out 문형만 사용)"""
    memos = []
    for lang in LANGS:
        pool = gen_items(lang, holdout=True)
        by_cls = {}
        for it in pool:
            by_cls.setdefault(it[1], []).append(it)
        for i in range(n_per_lang):
            k = random.randint(2, 5)
            classes = random.sample([c for c in by_cls if c != "VISIT"], k)
            if random.random() < 0.6:
                classes = ["VISIT"] + classes
            parts = [random.choice(by_cls[c]) for c in classes]
            text = ""
            for j, p in enumerate(parts):
                text += p[0]
                text += random.choice(JOINERS[lang]) if j < len(parts) - 1 else random.choice([".", "", "!"]) if lang != "ne" else "।"
            memos.append({"id": f"S-{lang}-{i:03d}", "lang": lang, "text": text,
                          "gold": [{"cls": p[1], "label": p[2], "meal_time": p[3]} for p in parts]})
    return memos


if __name__ == "__main__":
    train = build_clause_set(False, reps=4)
    held = build_clause_set(True, reps=2)
    memos = build_memos()
    for name, rows in (("clauses_train.jsonl", train), ("clauses_heldout.jsonl", held), ("memos_synth.jsonl", memos)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    print("train", len(train), Counter(r["lang"] for r in train))
    print("heldout", len(held), Counter(r["cls"] for r in held))
    print("memos", len(memos))
