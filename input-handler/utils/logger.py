import hashlib
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def mask_user_id(user_id: Optional[str]) -> str:
    """
    CloudWatchにPIIを出さないためのマスキング。
    userIdの末尾4文字 + ハッシュ短縮を出す。
    """
    if not user_id:
        return "unknown"

    suffix = user_id[-4:]
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:8]
    return f"****{suffix}({digest})"


def info(event: str, detail: Dict[str, Any]) -> None:
    """
    JSONで構造化ログを出す（本文は入れない）
    """
    payload = {"event": event, **detail}
    logger.info(json.dumps(payload, ensure_ascii=False))
