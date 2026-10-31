# -*- coding: utf-8 -*-
"""
CareBridge 온디바이스 경량 AI 모델 학습
- 구조: 공유 해시 특징(문자 n-gram) + 다중 헤드 소프트맥스 회귀(멀티태스크)
  head 'cls'  : 9개 기록 항목 분류 (VISIT, SUPPORT, MEAL, SLEEP, DISCOMFORT, MEDICATION, EXCRETION, MOOD, EVENT)
  하위 head   : 항목별 세부값 (식사량, 식사시점, 복약 상태, 수면, 불편 부위, 지원 유형, 정서, 배변, 사건)
- 출력: model/carebridge_model.json (int8 양자화, 브라우저에서 그대로 로드)
실행: python model/train.py
"""
import json
import os
import sys
import base64
import time
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model"))
from features import featurize, DIM  # noqa

HEADS = {
    "cls": ["VISIT", "SUPPORT", "MEAL", "SLEEP", "DISCOMFORT", "MEDICATION", "EXCRETION", "MOOD", "EVENT"],
    "MEAL": ["ALL", "MOST", "HALF", "LITTLE", "NONE", "UNSPEC"],
    "MEAL_TIME": ["BREAKFAST", "LUNCH", "DINNER", "SNACK", "UNSPEC"],
    "MEDICATION": ["TAKEN", "NOT_CONFIRMED", "REFUSED"],
    "SLEEP": ["GOOD", "POOR", "WOKE"],
    "DISCOMFORT": ["KNEE", "BACK", "HEAD", "STOMACH", "LEG", "SHOULDER", "CHEST", "UNSPEC"],
    "SUPPORT": ["BATH", "WALK", "DRESS", "MEAL_ASSIST", "CLEAN", "REPOSITION"],
    "MOOD": ["GOOD", "LOW", "AGITATED"],
    "EXCRETION": ["NORMAL", "NONE", "LOOSE"],
    "EVENT": ["FALL", "NEAR_FALL"],
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def to_matrix(texts):
    rows, cols, vals = [], [], []
    for i, t in enumerate(texts):
        for j, v in featurize(t).items():
            rows.append(i); cols.append(j); vals.append(v)
    return csr_matrix((vals, (rows, cols)), shape=(len(texts), DIM), dtype=np.float32)


def head_data(rows, head):
    if head == "cls":
        sel = rows; y = [r["cls"] for r in rows]
    elif head == "MEAL_TIME":
        sel = [r for r in rows if r["cls"] == "MEAL"]; y = [r["meal_time"] for r in sel]
    else:
        sel = [r for r in rows if r["cls"] == head]; y = [r["label"] for r in sel]
    return [r["text"] for r in sel], y


def train(C=8.0):
    rows = load(os.path.join(ROOT, "data", "clauses_train.jsonl"))
    model = {"version": "1.0.0", "dim": DIM, "trained_at": time.strftime("%Y-%m-%d"), "heads": {}}
    clfs = {}
    for head, labels in HEADS.items():
        X_text, y = head_data(rows, head)
        X = to_matrix(X_text)
        clf = LogisticRegression(C=C, max_iter=3000, class_weight="balanced")
        clf.fit(X, y)
        Wc, bc = clf.coef_, clf.intercept_
        if Wc.shape[0] == 1:  # 이진 분류 → classes_ 순서의 2행으로 확장
            Wc = np.vstack([-Wc[0] / 2, Wc[0] / 2]); bc = np.array([-bc[0] / 2, bc[0] / 2])
        order = [list(clf.classes_).index(l) for l in labels]
        W, b = Wc[order], bc[order]
        scale = np.abs(W).max(axis=1) / 127.0 + 1e-12
        q = np.clip(np.round(W / scale[:, None]), -127, 127).astype(np.int8)
        model["heads"][head] = {
            "labels": labels,
            "scale": [float(s) for s in scale],
            "bias": [round(float(x), 5) for x in b],
            "w": base64.b64encode(q.tobytes()).decode("ascii"),
            "n_train": len(y),
        }
        clfs[head] = (labels, scale, q, b)
        print(f"[{head}] n={len(y)} classes={labels}")
    out = os.path.join(ROOT, "model", "carebridge_model.json")
    with open(out, "w") as f:
        json.dump(model, f)
    print("saved", out, os.path.getsize(out) // 1024, "KB")
    return model


if __name__ == "__main__":
    train()
