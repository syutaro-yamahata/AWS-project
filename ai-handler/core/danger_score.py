# ai-handler/core/danger_score.py

from __future__ import annotations


def danger_score_from_type(message_type: str) -> float:
    """
    ELI5:
    「この文章は danger とか privacy-risk とか、どのタイプ？」が分かったら、
    それに対応する危険スコア（0.0〜1.0）を返す関数。

    例:
      - "danger"       -> 1.0
      - "privacy-risk" -> 0.5
      - "forbidden"    -> 0.7
      - "consult"      -> 0.2（基本値）
      - "smalltalk"    -> 0.0
      - "unknown"      -> 0.0
    """

    if not isinstance(message_type, str) or not message_type:
        return 0.0

    message_type = message_type.strip().lower()

    # ルールは「固定値」でまず運用する（チーム開発でブレない）
    mapping: dict[str, float] = {
        "danger": 1.0,
        "privacy-risk": 0.5,
        "forbidden": 0.7,
        "consult": 0.2,     # consult は 0.1〜0.3 の範囲 → まずは中間の 0.2
        "smalltalk": 0.0,
        "unknown": 0.0,
    }

    # もし知らないタイプが来ても落ちないように 0.0 を返す
    return float(mapping.get(message_type, 0.0))


def danger_score(text: str, message_type: str) -> float:
    """
    ELI5:
    将来スコアを少しだけ賢くしたくなった時のために用意しておく関数。
    今は「typeベース」で返すだけ（= 結果は danger_score_from_type と同じ）。

    ※ text を引数に入れているのは、
       例えば「相談だけど強めの言葉が多いなら 0.3 に寄せる」など、
       後で拡張できるようにするため。
    """
    # 今は設計通り、typeだけで固定値を返す
    return danger_score_from_type(message_type)
