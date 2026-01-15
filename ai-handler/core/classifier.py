# ai-handler/core/classifier.py

from ai-handler.unils.normalize import normalize_text

# カテゴリごとのキーワード定義

denger_keywords = [
      "死にたい", "死ぬ", "自殺", "殺す", "殺したい", "ぶっ殺す", "犯罪", "暴力"
]

private_keywords = [
    "住所", "本名", "電話番号", "line", "連絡先", "sns"
]

forbidden_keywords = [
   "ハッキング", "不正アクセス", "裏技", "突破方法", "ルール無視", "バイパス"
]

counsult_keywords = [
   "相談", "困っている", "どうすれば", "助けて", "教えて", "わからない"
]

small_talk_keywords = [
   "こんにちは", "おはよう", "こんばんは", "寒い", "暑い", "眠い", "疲れた", "元気"
]

def contains_keyword(text: str, keywords: list[str]) -> bool:
    """
    ELI5:
    text（文章）の中に、keywords（単語リスト）のどれか1つでも入ってたら True（はい）
    1つも入ってなかったら False（いいえ）
    """

    # keywords を 1個ずつ取り出してチェックする
    # 例: keyword="住所" のとき、「住所」が text に入ってたら True
    # any(...) は「1つでも True があれば True」を返す魔法の関数
    return any(keyword in text for keyword in keywords)


def classify_user_input(text: str) -> str:
    """
    ELI5:
    ユーザーの文章を見て、どのタイプの話かを決める関数。
    まずは「ちゃんとした文章か？」をチェックして、ダメなら 'unknown' にする。
    """

    # ここは「安全チェック（ガード）」：
    # text が空っぽ（""）だったり None だったりしたら判定できない
    # また、text が文字（str）じゃなかったら判定できない（例: 数字や辞書）
    if not text or not isinstance(text, str):
        return "unknown"  # 何の文章かわからないので unknown にする

    # ここから先に、本当の分類処理（danger → privacy…）が続く想定
    # 今はまだ “入口のチェックだけ” を書いてる状態
    # 例:
    # if contains_keyword(text, danger_keywords): return "danger"
    # ...
    return "unknown"  # ひとまず仮（この下に分類ロジックを足していく）





    # 正規化（ひらがな/半角/小文字化など）
    text = normalize_text(text)

# 優先順位: danger > privacy-risk > forbidden > consult > smalltalk > unknown
 if contains_keyword(text, denger_keywords):
        return "danger"

 if contains_keyword(text, private_keywords):
        return "privacy-risk"

 if contains_keyword(text, forbidden_keywords):
        return "forbidden"

 if contains_keyword(text, counsult_keywords):
        return "consult"

 if contains_keyword(text, small_talk_keywords):
        return "smalltalk"

        return "unknown"    
