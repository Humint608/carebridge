# -*- coding: utf-8 -*-
"""Python 학습 특징 ↔ 브라우저 추론 특징이 비트 단위로 동일한지 검증하기 위한 기준값 생성"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model"))
from features import featurize  # noqa

rows = [json.loads(l) for l in open(os.path.join(ROOT, "data", "clauses_heldout.jsonl"), encoding="utf-8")][:300]
out = [{"text": r["text"], "idx": sorted(featurize(r["text"]).keys())} for r in rows]
json.dump(out, open(os.path.join(ROOT, "eval", "parity_ref.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("parity refs", len(out))
