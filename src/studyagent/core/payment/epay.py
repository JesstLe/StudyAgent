from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
import structlog

logger = structlog.get_logger(__name__)

SUPPORTED_CHANNELS = ("alipay", "wxpay", "qqpay")


@dataclass(frozen=True)
class PaymentParams:
    pid: str
    trade_type: str
    out_trade_no: str
    notify_url: str
    return_url: str
    name: str
    money: str
    sign: str
    sign_type: str


@dataclass(frozen=True)
class PaymentResult:
    trade_no: str
    payment_url: str
    qr_url: str | None


@dataclass(frozen=True)
class CallbackData:
    pid: str
    trade_type: str
    out_trade_no: str
    trade_no: str
    name: str
    money: str
    sign: str
    sign_type: str
    trade_status: str


def _md5_sign(params: dict[str, str], key: str) -> str:
    filtered = {k: v for k, v in sorted(params.items()) if v != "" and k != "sign" and k != "sign_type"}
    query = "&".join(f"{k}={v}" for k, v in filtered.items())
    return hashlib.md5((query + key).encode("utf-8")).hexdigest()


def _generate_trade_no() -> str:
    ts = int(time.time() * 1000)
    short = uuid.uuid4().hex[:8].upper()
    return f"SA{ts}{short}"


class EpayClient:
    def __init__(self, pid: str, key: str, gateway_url: str, sign_type: str = "MD5") -> None:
        self._pid = pid
        self._key = key
        self._gateway_url = gateway_url.rstrip("/")
        self._sign_type = sign_type

    def create_payment(
        self,
        out_trade_no: str,
        name: str,
        money: float,
        channel: str,
        notify_url: str,
        return_url: str,
    ) -> PaymentResult:
        if channel not in SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel: {channel}. Must be one of {SUPPORTED_CHANNELS}")

        params: dict[str, str] = {
            "pid": self._pid,
            "type": channel,
            "out_trade_no": out_trade_no,
            "notify_url": notify_url,
            "return_url": return_url,
            "name": name,
            "money": f"{money:.2f}",
        }
        params["sign"] = _md5_sign(params, self._key)
        params["sign_type"] = self._sign_type

        payment_url = f"{self._gateway_url}/submit.php?{urlencode(params)}"
        return PaymentResult(
            trade_no=out_trade_no,
            payment_url=payment_url,
            qr_url=None,
        )

    def verify_callback(self, params: dict[str, Any]) -> bool:
        received_sign = params.get("sign", "")
        if not received_sign:
            return False

        str_params = {k: str(v) for k, v in params.items()}
        expected_sign = _md5_sign(str_params, self._key)
        return received_sign == expected_sign

    def parse_callback(self, params: dict[str, Any]) -> CallbackData | None:
        if not self.verify_callback(params):
            logger.warning("epay_callback_verify_failed", params=params)
            return None

        trade_status = params.get("trade_status", "")
        if trade_status != "TRADE_SUCCESS":
            logger.info("epay_callback_not_success", status=trade_status)
            return None

        return CallbackData(
            pid=str(params.get("pid", "")),
            trade_type=str(params.get("type", "")),
            out_trade_no=str(params.get("out_trade_no", "")),
            trade_no=str(params.get("trade_no", "")),
            name=str(params.get("name", "")),
            money=str(params.get("money", "")),
            sign=str(params.get("sign", "")),
            sign_type=str(params.get("sign_type", "")),
            trade_status=trade_status,
        )

    async def query_order(self, out_trade_no: str) -> dict[str, Any] | None:
        params: dict[str, str] = {
            "act": "order",
            "pid": self._pid,
            "key": self._key,
            "out_trade_no": out_trade_no,
        }
        url = f"{self._gateway_url}/api.php?{urlencode(params)}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                if data.get("code") == 1:
                    return data
                logger.warning("epay_query_failed", data=data)
                return None
            except (httpx.HTTPError, ValueError) as e:
                logger.error("epay_query_error", error=str(e))
                return None

    @staticmethod
    def generate_trade_no() -> str:
        return _generate_trade_no()
