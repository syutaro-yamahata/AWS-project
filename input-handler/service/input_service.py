import base64
import hashlib
import hmac
import json
import boto3
from typing import Any, Dict, List, Optional, Tuple
from urllib import request
from urllib.error import URLError, HTTPError

from utils.logger import info, mask_user_id


LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"
_lambda = boto3.client("lambda")


def _get_header(event: Dict[str, Any], name: str) -> Optional[str]:
    headers = event.get("headers") or {}
    # API Gatewayはヘッダ名が小文字化されることがあるので両対応
    for k, v in headers.items():
        if k.lower() == name.lower():
            return v
    return None


def _get_raw_body(event: Dict[str, Any]) -> bytes:
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        return base64.b64decode(body)
    return body.encode("utf-8")


def verify_line_signature(raw_body: bytes, signature: str, channel_secret: str) -> bool:
    mac = hmac.new(channel_secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def parse_line_events(raw_body: bytes) -> List[Dict[str, Any]]:
    payload = json.loads(raw_body.decode("utf-8"))
    return payload.get("events", [])


def extract_user_and_message(evt: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    戻り値: (userId, messageText, replyToken)
    """
    source = evt.get("source") or {}
    user_id = source.get("userId")

    reply_token = evt.get("replyToken")
    message = evt.get("message") or {}
    msg_type = message.get("type")

    if msg_type != "text":
        return user_id, None, reply_token

    text = message.get("text")
    return user_id, text, reply_token


def reply_text(reply_token: str, text: str, channel_access_token: str) -> None:
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    req = request.Request(
        LINE_REPLY_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {channel_access_token}",
        },
    )

    try:
        with request.urlopen(req, timeout=5) as resp:
            _ = resp.read()
    except HTTPError as e:
        info("line_reply_http_error", {"status": e.code})
        raise
    except URLError as e:
        info("line_reply_url_error", {"reason": str(e.reason)})
        raise


def build_ai_payload(user_id: str, message: str) -> Dict[str, str]:
    # 仕様：AI-handlerへは userId / message のみ
    return {"userId": user_id, "message": message}


def invoke_ai_handler(function_name: str, payload: Dict[str, str]) -> str:
    """
    ai-handler を同期呼び出しして、body内の ai.answer を返す
    ai-handler の戻り値:
        { "statusCode": 200, "body": "{\"ai\":{\"answer\":\"...\"}, ...}" }
    """
    resp = _lambda.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )

    raw = resp["Payload"].read().decode("utf-8")

    # Lambda側で例外が起きて FunctionError が付く場合もある
    if resp.get("FunctionError"):
        info("ai_handler_function_error", {"rawLength": len(raw)})
        return "（回答の生成に失敗しました。もう一度送ってください）"

    data: Any = json.loads(raw)

    # ai-handler は API Gateway 互換の形式で返す（statusCode/body）
    if isinstance(data, dict) and "body" in data:
        body = data["body"]
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception:
                # body が文字列だけの場合は、そのまま返信文として返す
                return body

        # ここが本命：result["ai"]["answer"]
        answer = ""
        if isinstance(body, dict):
            ai = body.get("ai") or {}
            if isinstance(ai, dict):
                answer = ai.get("answer", "")

        if isinstance(answer, str) and answer.strip():
            return answer

    info("ai_handler_unexpected_response", {"rawLength": len(raw)})
    return "（回答の生成に失敗しました。もう一度送ってください）"
