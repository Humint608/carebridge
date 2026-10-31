# -*- coding: utf-8 -*-
"""
문장(절) → 해시 특징 벡터. 브라우저(web/engine.js)와 완전히 동일한 규칙으로 구현되어
학습한 가중치를 그대로 온디바이스 추론에 사용한다.
- 정규화: 소문자 → NFD → 라틴 결합 성조부호(U+0300–036F) 제거, đ→d → NFC
  (베트남어를 성조 없이 입력해도 같은 특징이 나오도록)
- 특징: 문자 2~4-gram + 단어 unigram, FNV-1a 32bit 해시 → DIM 버킷, 이진값, L2 정규화
"""
import re
import unicodedata
import math

DIM = 1 << 13  # 8192
_APOS = re.compile(r"[ʻ’`‘ʼ]")
_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[.,!?;:\"()\[\]।]")


def normalize(text: str) -> str:
    t = text.lower()
    t = _APOS.sub("'", t)
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if not (0x300 <= ord(ch) <= 0x36F))
    t = t.replace("đ", "d")
    t = unicodedata.normalize("NFC", t)
    t = _PUNCT.sub(" ", t)
    t = _WS.sub(" ", t).strip()
    return t


def fnv1a(s: str) -> int:
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def feature_keys(text: str):
    t = normalize(text)
    keys = []
    padded = " " + t + " "
    chars = list(padded)
    for n in (2, 3, 4):
        for i in range(len(chars) - n + 1):
            keys.append("c" + "".join(chars[i:i + n]))
    for w in t.split(" "):
        if w:
            keys.append("w" + w)
    return keys


def featurize(text: str):
    """returns dict{index: value} (binary, L2-normalized)"""
    idx = sorted(set(fnv1a(k) % DIM for k in feature_keys(text)))
    if not idx:
        return {}
    v = 1.0 / math.sqrt(len(idx))
    return {i: v for i in idx}
