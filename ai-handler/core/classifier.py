# core/classifier.py
from utils.normalize import normalize_text

DANGER_KEYWORDS = ["死にたい", "死ぬ", "自殺", "殺す", "殺したい", "犯罪", "暴力"]
PRIVACY_KEYWORDS = ["住所", "本名", "電話番号", "line", "連絡先", "sns"]
FORBIDDEN_KEYWORDS = ["ハッキング", "不正アクセス", "裏技", "突破方法", "バイパス"]
CONSULT_KEYWORDS = ["相談", "困っている", "どうすれば", "助けて", "教えて", "わからない"]
SMALLTALK_KEYWORDS = ["こんにちは", "おはよう", "こんばんは", "寒い", "暑い", "眠い", "疲れた", "元気"]

def contains_keyword(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)

def classify_user_input(text: str) -> str:
    if text is None or not isinstance(text, str):
        return "unknown"

    text = normalize_text(text)

    if contains_keyword(text, DANGER_KEYWORDS):
        return "danger"
    if contains_keyword(text, PRIVACY_KEYWORDS):
        return "privacy-risk"
    if contains_keyword(text, FORBIDDEN_KEYWORDS):
        return "forbidden"
    if contains_keyword(text, CONSULT_KEYWORDS):
        return "consult"
    if contains_keyword(text, SMALLTALK_KEYWORDS):
        return "smalltalk"
    return "unknown"
