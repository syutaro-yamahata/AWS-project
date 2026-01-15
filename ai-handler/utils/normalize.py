# ai-handler/utils/normalize.py

import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    ELI5:
    文章を「比べやすい形」に整える関数。

    例：
    - " ＬＩＮＥ　ID 教えて！ " みたいにバラバラな文字でも
      → "line id 教えて!" のように、同じルールにそろえる

    こうすると classifier の「キーワード判定」が当たりやすくなる！
    """

    # 1) text が文字じゃない / None のときは安全に空にする
    if not isinstance(text, str) or text is None:
        return ""

    # 2) 前後の空白を削る（"  こんにちは  " → "こんにちは"）
    text = text.strip()

    # 3) 全角/半角などを統一する（日本語で超大事）
    #    NFKC: "ＬＩＮＥ" → "LINE"、"１" → "1" などに寄せる
    text = unicodedata.normalize("NFKC", text)

    # 4) 英字を小文字に統一（"LINE" と "line" を同じ扱いにする）
    text = text.lower()

    # 5) 連続する空白を1つにする（"a   b" → "a b"）
    text = re.sub(r"\s+", " ", text)

    return text
