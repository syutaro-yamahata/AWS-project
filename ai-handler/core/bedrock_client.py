# ai-handler/core/bedrock_client.py

# ai-handler/core/bedrock_client.py

import json
import os
import boto3

# 環境変数で切り替えできるようにしておく（運用で強い）
DEFAULT_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
DEFAULT_REGION = os.getenv("AWS_REGION", "us-east-1")


def generate_answer(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    """
    ELI5:
    Bedrockに「ルール(system)」と「ユーザー文(user)」を渡して返答をもらう。
    戻り値: (answer_text, used_model)
    """

    client = boto3.client("bedrock-runtime", region_name=DEFAULT_REGION)

    # Claude系のメッセージ形式（※モデルにより形式が違うので、後で調整OK）
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }

    resp = client.invoke_model(
        modelId=DEFAULT_MODEL_ID,
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )

    data = json.loads(resp["body"].read())

    # Claudeの返し方は content 配列のことが多い
    # 例: {"content":[{"type":"text","text":"..."}], ...}
    answer = ""
    if isinstance(data, dict) and "content" in data and data["content"]:
        first = data["content"][0]
        answer = first.get("text", "") if isinstance(first, dict) else ""

    return answer, DEFAULT_MODEL_ID
