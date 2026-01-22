# ai-handler/main.py

import json
import time
from typing import Any, Dict

from core.classifier import classify_user_input
from core.danger_score import danger_score_from_type

from core.prompt import build_system_prompt, build_user_prompt
from core.bedrock_client import generate_answer

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _parse_event(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Lambdaに来るeventは形が色々あるので、
    最終的に {"userId": "...", "message": "..."} にそろえる。
    """

    # 1) 直で {userId, message} が来るケース
    if isinstance(event, dict) and "userId" in event and "message" in event:
        return {
            "userId": str(event.get("userId", "")),
            "message": str(event.get("message", "")),
        }

    # 2) API Gateway 経由で body に JSON が入ってるケース
    body = event.get("body") if isinstance(event, dict) else None
    if body:
        try:
            if isinstance(body, str):
                data = json.loads(body)
            elif isinstance(body, dict):
                data = body
            else:
                data = {}

            return {
                "userId": str(data.get("userId", "")),
                "message": str(data.get("message", "")),
            }
        except Exception:
            return {"userId": "", "message": ""}

    return {"userId": "", "message": ""}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda の入口（エントリポイント）
    入力: event（userId, message）
    出力: API Gateway 互換のHTTPレスポンス
    """
    start = time.time()

    parsed = _parse_event(event)
    user_id = parsed.get("userId", "")
    message = parsed.get("message", "")

    # 1) 分類
    msg_type = classify_user_input(message)

    # 2) 危険スコア（分類結果から算出）
    score = danger_score_from_type(msg_type)

    # 3) Bedrock 用プロンプト生成
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(message=message, message_type=msg_type, danger_score=score)

    # 4) Bedrock 呼び出し
    answer_text = ""
    used_model = "unknown"
    try:
        # generate_answer は (answer_text, used_model) を返す想定
        answer_text, used_model = generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as e:
        logger.exception("bedrock inference failed", extra={"error": str(e)})
        answer_text = "ごめんね、今うまく返答できなかったよ。少し時間をおいてもう一度送ってみて。"
        used_model = "error"

    elapsed_ms = int((time.time() - start) * 1000)

    # 5) 仕様で確定した JSON（v1.0）
    result = {
        "userId": user_id,
        "timestamp": int(time.time()),
        "inputMessage": message,
        "ai": {
            "answer": answer_text,
            "type": msg_type,
            "dangerScore": float(score),
            "usedModel": used_model,
            "responseTimeMs": elapsed_ms,
        },
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(result, ensure_ascii=False),
    }


# Lambda のハンドラー名は main.lambda_handler を想定
def lambda_handler(event, context):
    return handler(event, context)
