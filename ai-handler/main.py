# ai-handler/main.py

import json
import time
from typing import Any, Dict

from core.classifier import classify
from core.danger_score import danger_score
from core.prompt import build_system_prompt, build_user_prompt
from core.bedrock_client import generate_answer
from utils.logger import get_logger


logger = get_logger(__name__)


def _parse_event(event: Dict[str, Any]) -> Dict[str, str]:
    """
    ELI5:
    Lambdaに来るeventは形が色々あるので、
    最終的に { "userId": "...", "message": "..." } にそろえて取り出す。
    """

    # 1) 直で {userId, message} が来てるケース（内部呼び出しなど）
    if isinstance(event, dict) and "userId" in event and "message" in event:
        return {"userId": str(event.get("userId")), "message": str(event.get("message"))}

    # 2) API Gateway 経由で body に JSON 文字列が入ってるケース
    body = event.get("body") if isinstance(event, dict) else None
    if body:
        try:
            if isinstance(body, str):
                data = json.loads(body)
            elif isinstance(body, dict):
                data = body
            else:
                data = {}
            return {"userId": str(data.get("userId", "")), "message": str(data.get("message", ""))}
        except Exception:
            # body が JSON じゃないなど
            return {"userId": "", "message": ""}

    return {"userId": "", "message": ""}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda の入口（エントリポイント）
    入力: event（userId, message）
    出力: 仕様で決めた JSON（v1.0）
    """

    start = time.time()

    parsed = _parse_event(event)
    user_id = parsed.get("userId", "")
    message = parsed.get("message", "")

    # ログ（個人情報は残さない方針なら、ここで message を直接出さない）
    logger.info(
        "ai-handler received event",
        extra={"hasUserId": bool(user_id), "messageLength": len(message) if isinstance(message, str) else 0},
    )

    # 1) 分類
    msg_type = classify(message)

    # 2) 危険スコア
    score = danger_score(message, msg_type)

    # 3) Bedrock 用プロンプト生成
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(message=message, message_type=msg_type, danger_score=score)

    # 4) Bedrock 呼び出し（推論）
    used_model = "unknown"
    answer_text = ""
    try:
        answer_text, used_model = generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as e:
        # Bedrock が落ちた時の保険（ユーザーには安全な返答）
        logger.exception("bedrock inference failed", extra={"error": str(e)})
        answer_text = "ごめんね、今うまく返答できなかったよ。少し時間をおいてもう一度送ってみて。"
        used_model = "error"

    elapsed_ms = int((time.time() - start) * 1000)

    # 5) 仕様で確定した JSON（v1.0）を組み立て
    result = {
        "userId": user_id,
        "timestamp": int(time.time()),  # epoch秒（AI側で付与する方針）
        "inputMessage": message,
        "ai": {
            "answer": answer_text,               # LINEにそのまま返す文章
            "type": msg_type,                    # 6分類
            "dangerScore": float(score),         # 0.0〜1.0
            "usedModel": used_model,             # モデル名
            "responseTimeMs": elapsed_ms,        # 推論+処理時間
        },
    }

    # 推論ログ（本文は避けてメタ情報中心）
    logger.info(
        "ai-handler response ready",
        extra={
            "type": msg_type,
            "dangerScore": float(score),
            "usedModel": used_model,
            "responseTimeMs": elapsed_ms,
        },
    )

    # API Gateway 経由でも使えるように HTTP レスポンス形式で返す
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(result, ensure_ascii=False),
    }
