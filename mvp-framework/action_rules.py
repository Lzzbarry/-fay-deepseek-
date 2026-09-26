"""
职坐标数字人框架 - 动作语义匹配
根据回复文本匹配动作规则表，输出 Action 语义对象。
前端通过 behavior/affect 驱动 Live2D 动作与表情。
"""
import csv
import os

_RULES = []


def _load_rules():
    """加载动作规则表"""
    global _RULES
    if _RULES:
        return _RULES
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "action_rules.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            _RULES.append({
                "code": row["code"],
                "behavior": row["behavior"],
                "affect": row["affect"],
                "intensity": float(row["intensity"]),
                "priority": int(row["priority"]),
                "sentimentHint": float(row["sentimentHint"]),
                "keywords": [k.strip() for k in row["keywords"].split("|") if k.strip()],
            })
    return _RULES


def match_action(text):
    """
    匹配动作规则。
    返回 Action 字典（含 code/behavior/affect/intensity/priority/matchedKeywords）。
    若无匹配返回 None（前端会回退到 Sentiment 驱动）。
    """
    rules = _load_rules()
    # 按 priority 降序匹配，优先级高的先匹配
    for rule in sorted(rules, key=lambda r: r["priority"], reverse=True):
        for kw in rule["keywords"]:
            if kw in text:
                return {
                    "code": rule["code"],
                    "behavior": rule["behavior"],
                    "affect": rule["affect"],
                    "intensity": rule["intensity"],
                    "priority": rule["priority"],
                    "matchedKeywords": [kw],
                    "sentimentHint": rule["sentimentHint"],
                }
    return None


if __name__ == "__main__":
    # 自测
    for t in ["你好", "请进，这边请", "太好了，恭喜你", "抱歉，这个问题我不太确定"]:
        print(t, "->", match_action(t))
