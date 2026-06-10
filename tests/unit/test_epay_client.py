from __future__ import annotations

import hashlib

import pytest

from studyagent.core.payment.epay import EpayClient, _md5_sign, _generate_trade_no


@pytest.fixture
def client() -> EpayClient:
    return EpayClient(
        pid="1001",
        key="test_secret_key_abc",
        gateway_url="https://epay.example.com",
        sign_type="MD5",
    )


class TestMd5Sign:
    def test_basic_sign(self) -> None:
        params = {
            "pid": "1001",
            "type": "alipay",
            "out_trade_no": "ORDER001",
            "notify_url": "https://example.com/notify",
            "return_url": "https://example.com/return",
            "name": "Test Product",
            "money": "10.00",
        }
        key = "secret123"

        result = _md5_sign(params, key)

        sorted_items = sorted(params.items())
        query = "&".join(f"{k}={v}" for k, v in sorted_items)
        expected = hashlib.md5((query + key).encode("utf-8")).hexdigest()
        assert result == expected

    def test_empty_value_excluded(self) -> None:
        params = {"pid": "1001", "type": "", "money": "5.00"}
        key = "key"
        result = _md5_sign(params, key)

        filtered = {k: v for k, v in sorted(params.items()) if v != ""}
        query = "&".join(f"{k}={v}" for k, v in filtered.items())
        expected = hashlib.md5((query + key).encode("utf-8")).hexdigest()
        assert result == expected

    def test_sign_key_excluded(self) -> None:
        params = {"pid": "1001", "sign": "old_sign", "money": "5.00"}
        key = "key"
        result = _md5_sign(params, key)

        filtered = {k: v for k, v in sorted(params.items()) if k not in ("sign", "sign_type")}
        query = "&".join(f"{k}={v}" for k, v in filtered.items())
        expected = hashlib.md5((query + key).encode("utf-8")).hexdigest()
        assert result == expected


class TestGenerateTradeNo:
    def test_starts_with_sa_prefix(self) -> None:
        trade_no = _generate_trade_no()
        assert trade_no.startswith("SA")

    def test_unique(self) -> None:
        nos = {_generate_trade_no() for _ in range(100)}
        assert len(nos) == 100


class TestCreatePayment:
    def test_returns_payment_url(self, client: EpayClient) -> None:
        result = client.create_payment(
            out_trade_no="ORDER001",
            name="Test Product",
            money=10.00,
            channel="alipay",
            notify_url="https://example.com/notify",
            return_url="https://example.com/return",
        )
        assert "submit.php?" in result.payment_url
        assert "pid=1001" in result.payment_url
        assert "type=alipay" in result.payment_url
        assert "out_trade_no=ORDER001" in result.payment_url

    def test_includes_sign(self, client: EpayClient) -> None:
        result = client.create_payment(
            out_trade_no="ORDER001",
            name="Test",
            money=5.00,
            channel="wxpay",
            notify_url="https://example.com/notify",
            return_url="https://example.com/return",
        )
        assert "sign=" in result.payment_url
        assert "sign_type=MD5" in result.payment_url

    def test_unsupported_channel_raises(self, client: EpayClient) -> None:
        with pytest.raises(ValueError, match="Unsupported channel"):
            client.create_payment(
                out_trade_no="ORDER001",
                name="Test",
                money=5.00,
                channel="bitcoin",
                notify_url="https://example.com/notify",
                return_url="https://example.com/return",
            )


class TestVerifyCallback:
    def test_valid_callback(self, client: EpayClient) -> None:
        params = {
            "pid": "1001",
            "type": "alipay",
            "out_trade_no": "ORDER001",
            "trade_no": "EPAY12345",
            "name": "Test",
            "money": "10.00",
            "trade_status": "TRADE_SUCCESS",
        }
        params["sign"] = _md5_sign(params, "test_secret_key_abc")
        params["sign_type"] = "MD5"

        assert client.verify_callback(params) is True

    def test_invalid_sign(self, client: EpayClient) -> None:
        params = {
            "pid": "1001",
            "sign": "wrong_sign",
            "sign_type": "MD5",
        }
        assert client.verify_callback(params) is False

    def test_missing_sign(self, client: EpayClient) -> None:
        assert client.verify_callback({"pid": "1001"}) is False


class TestParseCallback:
    def test_valid_success_callback(self, client: EpayClient) -> None:
        params = {
            "pid": "1001",
            "type": "alipay",
            "out_trade_no": "ORDER001",
            "trade_no": "EPAY12345",
            "name": "Test",
            "money": "10.00",
            "trade_status": "TRADE_SUCCESS",
        }
        params["sign"] = _md5_sign(params, "test_secret_key_abc")
        params["sign_type"] = "MD5"

        result = client.parse_callback(params)
        assert result is not None
        assert result.out_trade_no == "ORDER001"
        assert result.trade_no == "EPAY12345"
        assert result.trade_status == "TRADE_SUCCESS"

    def test_non_success_status_returns_none(self, client: EpayClient) -> None:
        params = {
            "pid": "1001",
            "type": "alipay",
            "out_trade_no": "ORDER001",
            "trade_no": "EPAY12345",
            "name": "Test",
            "money": "10.00",
            "trade_status": "TRADE_PENDING",
        }
        params["sign"] = _md5_sign(params, "test_secret_key_abc")
        params["sign_type"] = "MD5"

        result = client.parse_callback(params)
        assert result is None

    def test_invalid_sign_returns_none(self, client: EpayClient) -> None:
        params = {
            "pid": "1001",
            "type": "alipay",
            "sign": "invalid",
            "trade_status": "TRADE_SUCCESS",
        }
        result = client.parse_callback(params)
        assert result is None
