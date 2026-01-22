import os
from typing import Any, Dict

from service.input_service import (
    _get_header,
    _get_raw_body,
    verify_line_signature,
    parse_line_events,
    extract_user_and_message,
    reply_text,
    build_ai_payload,
    invoke_ai_handler,
)
from utils.logger import info, mask_user_id


UNSUPPORTED_MESSAGE = "現在テキストメッセージのみ対応しています。テキストで送ってください。"
EMPTY_TEXT_MESSAGE = "メッセージが空でした。テキストを入力して送ってください。"


def _response(status_code: int, body: str = '{"ok":true}') -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": body,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    channel_secret = os.environ.get("LINE_CHANNEL_SECRET", "")
    access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

    raw_body = _get_raw_body(event)
    signature = _get_header(event, "X-Line-Signature") or ""

    # 署名検証（不正なら即終了）
    if not channel_secret or not signature or not verify_line_signature(raw_body, signature, channel_secret):
        info("invalid_signature", {"requestId": getattr(context, "aws_request_id", "unknown")})
        return _response(401, '{"ok":false,"reason":"invalid signature"}')

    events = parse_line_events(raw_body)
    info("webhook_received", {"requestId": getattr(context, "aws_request_id", "unknown"), "eventCount": len(events)})

    # 複数eventsが来ることがあるので順に処理
    for evt in events:
        if evt.get("type") != "message":
            continue

        user_id, text, reply_token = extract_user_and_message(evt)
        info("message_event", {"user": mask_user_id(user_id), "hasText": bool(text)})

        # replyTokenがないケースは基本ないが、念のため
        if not reply_token:
            continue

        # text以外 → 未対応返信
        if text is None:
            if access_token:
                reply_text(reply_token, UNSUPPORTED_MESSAGE, access_token)
            continue

        # 空文字チェック
        if not text.strip():
            if access_token:
                reply_text(reply_token, EMPTY_TEXT_MESSAGE, access_token)
            continue

        # ここで AI-handler に渡すデータを作る（Step3で実際に呼び出す）
        payload = build_ai_payload(user_id=user_id or "", message=text)

        info("ai_payload_ready", {"user": mask_user_id(payload.get("userId")), "messageLength": len(text)})

        ai_fn = os.environ.get("AI_HANDLER_FUNCTION_NAME", "")
        if not ai_fn:
            reply_text(reply_token, "（サーバ設定が未完了です：AI_HANDLER_FUNCTION_NAME）", access_token)
            continue

        try:
            reply = invoke_ai_handler(ai_fn, payload)
        except Exception as e:
            info("ai_invoke_failed", {"error": str(e)})
            reply = "（ただいま混み合っています。もう一度送ってください）"

        if access_token:
            reply_text(reply_token, reply, access_token)

        # 本文をログに出さない
        info("ai_payload_ready", {"user": mask_user_id(payload.get("userId")), "messageLength": len(text)})

        # Step3でここに「ai-handler呼び出し」を追加する
        # 例: forward_to_ai(payload)

    return _response(200)
