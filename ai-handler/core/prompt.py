# ai-handler/core/prompt.py

def build_system_prompt() -> str:
    """
    ELI5:
    システムプロンプトを作る関数。
    ここには AI に対する「全体の指示」を書く。

    例:
      - 「あなたは親切なアシスタントです」
      - 「ユーザーの質問に答えてください」
    """
    return (
        "You are a helpful and friendly AI assistant. "
        "Please answer the user's questions to the best of your ability."
    )

def build_user_prompt(message: str, message_type: str, danger_score: float) -> str:
    """
        "あなたは利用者の相談に寄り添い、安全で適切な回答を返すAIアシスタントです。"
        "個人情報（氏名・住所・電話・SNS IDなど）を尋ねたり共有を促してはいけません。"
        "暴力・自殺・犯罪・ハッキング等の依頼は拒否し、安全な行動を促してください。"
        "口調は丁寧で落ち着いたものにしてください。"
    """
    return (
        f"User Message: {message}\n"
        f"Message Type: {message_type}\n"
        f"Danger Score: {danger_score:.2f}\n"
        "上の分類と危険度を参考に、安全で適切な返答を日本語で出してください。"
    )
