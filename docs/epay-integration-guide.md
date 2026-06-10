# 易支付（ePay）接入教程

适用于任何 Python/FastAPI 项目，10 分钟完成支付集成。

---

## 目录

1. [什么是易支付](#1-什么是易支付)
2. [注册服务商并获取凭证](#2-注册服务商并获取凭证)
3. [项目配置](#3-项目配置)
4. [核心代码实现](#4-核心代码实现)
5. [数据库模型](#5-数据库模型)
6. [API 路由](#6-api-路由)
7. [前端对接](#7-前端对接)
8. [本地测试](#8-本地测试)
9. [部署上线](#9-部署上线)
10. [安全注意事项](#10-安全注意事项)

---

## 1. 什么是易支付

易支付（ePay）是国内广泛使用的**第三方支付聚合协议**，不是某一家公司的服务。

**核心特点：**
- 个人可用，不需要营业执照
- 统一 API 接入微信、支付宝、QQ 钱包
- 免签约，注册即可用
- 有 V1（MD5 签名）和 V2（RSA 签名）两个版本

**支付流程：**
```
用户下单 → 你的后端构造签名 → 跳转易支付网关 → 用户扫码/支付
→ 易支付异步回调你的服务器 → 验签 → 更新订单状态 → 完成发货
```

**与官方支付的区别：**

| 对比项 | 官方支付 | 易支付 |
|--------|---------|--------|
| 营业执照 | 必须 | 不需要 |
| 审核周期 | 1-7 天 | 15 分钟 |
| 接入难度 | 高（SDK+证书） | 低（HTTP 表单） |
| 手续费 | 0.38%-0.6% | 1%-2%（含平台费） |
| 资金安全 | 官方结算 | 官方结算，平台不碰钱 |

---

## 2. 注册服务商并获取凭证

### 2.1 选择服务商

搜索关键词「彩虹易支付」「免签约支付」，常见服务商：

| 服务商 | 网址 | 特点 |
|--------|------|------|
| 彩虹易支付（微极速） | https://pay.v8jisu.cn/ | 有公司备案，审核快 |
| 江辰易支付 | https://www.jiangcen.cn/ | 费率低，文档全 |
| 站长付 | https://zhanzhangfu.com/ | 免手续费，适合小额 |
| ezfp | https://www.ezfp.cn/ | 企业级，渠道最全 |

> 选择标准：有 ICP 备案、有公司主体、客服响应快、费率合理。

### 2.2 注册并获取凭证

1. 注册商户账号
2. 提交实名资料（身份证 + 手机号 + 银行卡）
3. 审核通过后，在「API 对接信息」页面获取：

```
商户ID (PID):          1406
MD5密钥 (KEY):         0oSmDZZd3dmmE2Eo3e2XdL3LXOAoU5MD
接口地址 (Gateway URL): https://www.jiangcen.cn/
签名方式:              MD5 (V1)
```

> 本教程使用 V1 + MD5 签名，适用于绝大多数场景。V2 + RSA 签名适合有更高安全要求的项目。

---

## 3. 项目配置

### 3.1 环境变量

在 `.env` 中添加（不要提交到 Git）：

```bash
# ePay 易支付
EPAY_ENABLED=true
EPAY_PID=你的商户ID
EPAY_KEY=你的商户密钥
EPAY_GATEWAY_URL=https://你的服务商地址
EPAY_NOTIFY_URL=https://你的域名/api/payment/notify
EPAY_RETURN_URL=https://你的前端域名/payment/result
EPAY_SIGN_TYPE=MD5
```

### 3.2 配置模型（Pydantic）

```python
# core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class EpayConfig(BaseSettings):
    enabled: bool = Field(default=False)
    pid: str = Field(default="")
    key: str = Field(default="")
    gateway_url: str = Field(default="https://www.jiangcen.cn")
    notify_url: str = Field(default="")
    return_url: str = Field(default="")
    sign_type: str = Field(default="MD5")

    model_config = SettingsConfigDict(env_prefix="epay_")

# 注册到主配置
class AppConfig(BaseSettings):
    # ... 其他配置 ...
    epay: EpayConfig = Field(default_factory=EpayConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )
```

---

## 4. 核心代码实现

### 4.1 易支付客户端

这是整个集成的核心，**可直接复制到任何 Python 项目**：

```python
# core/payment/epay.py
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
    trade_status: str


def _md5_sign(params: dict[str, str], key: str) -> str:
    """ePay V1 MD5 签名算法：
    1. 过滤空值、sign、sign_type
    2. 按 key 字母排序
    3. 拼接为 key=value&key=value
    4. 末尾追加商户密钥
    5. 取 MD5
    """
    filtered = {
        k: v for k, v in sorted(params.items())
        if v != "" and k != "sign" and k != "sign_type"
    }
    query = "&".join(f"{k}={v}" for k, v in filtered.items())
    return hashlib.md5((query + key).encode("utf-8")).hexdigest()


def _generate_trade_no() -> str:
    """生成唯一订单号：SA + 时间戳 + 随机串"""
    ts = int(time.time() * 1000)
    short = uuid.uuid4().hex[:8].upper()
    return f"SA{ts}{short}"


class EpayClient:
    def __init__(
        self,
        pid: str,
        key: str,
        gateway_url: str,
        sign_type: str = "MD5",
    ) -> None:
        self._pid = pid
        self._key = key
        self._gateway_url = gateway_url.rstrip("/")
        self._sign_type = sign_type

    def create_payment(
        self,
        out_trade_no: str,
        name: str,
        money: float,
        channel: str,          # "alipay" | "wxpay" | "qqpay"
        notify_url: str,
        return_url: str,
    ) -> PaymentResult:
        """构造跳转支付链接（submit.php 模式）"""
        if channel not in SUPPORTED_CHANNELS:
            raise ValueError(
                f"Unsupported channel: {channel}. "
                f"Must be one of {SUPPORTED_CHANNELS}"
            )

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
        """验证异步回调签名"""
        received_sign = params.get("sign", "")
        if not received_sign:
            return False
        str_params = {k: str(v) for k, v in params.items()}
        expected_sign = _md5_sign(str_params, self._key)
        return received_sign == expected_sign

    def parse_callback(self, params: dict[str, Any]) -> CallbackData | None:
        """解析并验证回调数据，成功返回 CallbackData，失败返回 None"""
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
            trade_status=trade_status,
        )

    async def query_order(self, out_trade_no: str) -> dict[str, Any] | None:
        """主动查询订单状态（可选）"""
        params = {
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
                return data if data.get("code") == 1 else None
            except (httpx.HTTPError, ValueError) as e:
                logger.error("epay_query_error", error=str(e))
                return None

    @staticmethod
    def generate_trade_no() -> str:
        return _generate_trade_no()
```

### 4.2 使用示例

```python
from studyagent.core.config import load_config
from studyagent.core.payment.epay import EpayClient

config = load_config()
epay = config.epay

client = EpayClient(
    pid=epay.pid,
    key=epay.key,
    gateway_url=epay.gateway_url,
    sign_type=epay.sign_type,
)

# 创建支付
result = client.create_payment(
    out_trade_no="ORDER_001",
    name="AI 学习会员",
    money=29.99,
    channel="alipay",
    notify_url="https://your-domain.com/api/payment/notify",
    return_url="https://your-domain.com/payment/result",
)
print(result.payment_url)  # 跳转用户到这个 URL 即可支付
```

---

## 5. 数据库模型

### 5.1 订单表

```python
# db/models.py (SQLAlchemy)
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="CNY")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending | paid | cancelled | refunded | expired
    payment_channel: Mapped[str | None] = mapped_column(String(50))
    paid_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=lambda: datetime.now(timezone.utc)
    )
```

### 5.2 支付记录表

```python
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    trade_no: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # alipay | wxpay | qqpay
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="created")
    # created | pending | success | failed
    payment_url: Mapped[str | None] = mapped_column(Text)
    epay_trade_no: Mapped[str | None] = mapped_column(String(128))
    callback_raw: Mapped[str | None] = mapped_column(Text)
    paid_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

---

## 6. API 路由

### 6.1 核心 API 设计

```
GET  /api/payment/channels          → 获取可用支付渠道
POST /api/payment/orders            → 创建订单
GET  /api/payment/orders/{id}       → 查询订单详情
POST /api/payment/pay               → 发起支付（返回支付 URL）
POST /api/payment/notify            → 易支付异步回调（ePay 调用）
GET  /api/payment/status/{trade_no} → 查询支付状态（前端轮询）
```

### 6.2 回调接口（最关键）

```python
@router.post("/notify")
async def epay_notify(request: Request):
    """易支付异步回调 —— 用户支付成功后 ePay 会 POST 到这个地址"""
    client = _get_epay_client()

    # 1. 接收表单参数
    form_data = await request.form()
    params = {k: v for k, v in form_data.items()}

    # 2. 验签（防止伪造回调）
    callback = client.parse_callback(params)
    if not callback:
        return "fail"  # ePay 协议：返回 fail 会重试

    # 3. 根据 out_trade_no 找到支付记录
    # 4. 更新状态为 success
    # 5. 更新关联订单为 paid
    # 6. 触发业务逻辑（发货、开通会员等）

    return "success"  # ePay 协议：返回 success 停止重试
```

### 6.3 完整路由文件

```python
# api/routes/payment.py
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from studyagent.core.config import load_config
from studyagent.core.payment.epay import EpayClient
from studyagent.db.engine import create_session_factory
from studyagent.db.models import Order, Payment

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/payment", tags=["payment"])


def _get_epay_client() -> EpayClient | None:
    config = load_config().epay
    if not config.enabled:
        return None
    return EpayClient(
        pid=config.pid,
        key=config.key,
        gateway_url=config.gateway_url,
        sign_type=config.sign_type,
    )


@router.get("/channels")
async def get_payment_channels():
    return {
        "channels": [
            {"id": "alipay", "name": "支付宝"},
            {"id": "wxpay", "name": "微信支付"},
            {"id": "qqpay", "name": "QQ钱包"},
        ]
    }


@router.post("/orders")
async def create_order(title: str, amount: float, user_id: str):
    session_factory = create_session_factory()
    async with session_factory() as session:
        order = Order(
            user_id=user_id,
            order_no=EpayClient.generate_trade_no(),
            title=title,
            amount=amount,
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return {"id": order.id, "order_no": order.order_no, "status": order.status}


@router.post("/pay")
async def create_payment(order_id: str, channel: str):
    client = _get_epay_client()
    if not client:
        return {"error": "ePay not configured"}

    config = load_config().epay
    session_factory = create_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order or order.status != "pending":
            return {"error": "Order not found or not payable"}

        trade_no = EpayClient.generate_trade_no()
        payment = Payment(
            order_id=order.id, trade_no=trade_no,
            channel=channel, amount=order.amount,
        )
        session.add(payment)

        epay_result = client.create_payment(
            out_trade_no=trade_no,
            name=order.title,
            money=float(order.amount),
            channel=channel,
            notify_url=config.notify_url,
            return_url=config.return_url,
        )
        payment.payment_url = epay_result.payment_url
        payment.status = "pending"
        order.payment_channel = channel
        await session.commit()

        return {
            "payment_url": epay_result.payment_url,
            "trade_no": trade_no,
        }


@router.post("/notify")
async def epay_notify(request: Request):
    client = _get_epay_client()
    if not client:
        return "fail"

    form_data = await request.form()
    params = {k: v for k, v in form_data.items()}

    callback = client.parse_callback(params)
    if not callback:
        logger.warning("epay_notify_invalid", params=params)
        return "fail"

    logger.info("epay_notify_success", trade_no=callback.out_trade_no)

    session_factory = create_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(Payment).where(Payment.trade_no == callback.out_trade_no)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return "fail"

        payment.status = "success"
        payment.epay_trade_no = callback.trade_no
        payment.callback_raw = json.dumps(params, ensure_ascii=False)
        payment.paid_at = datetime.now(timezone.utc)

        order = (
            await session.execute(select(Order).where(Order.id == payment.order_id))
        ).scalar_one_or_none()
        if order:
            order.status = "paid"
            order.paid_at = datetime.now(timezone.utc)

        await session.commit()

    return "success"


@router.get("/status/{trade_no}")
async def get_payment_status(trade_no: str):
    session_factory = create_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(Payment).where(Payment.trade_no == trade_no)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return {"error": "not found"}
        return {"status": payment.status, "paid_at": payment.paid_at}
```

---

## 7. 前端对接

### 7.1 支付流程

```typescript
// 1. 创建订单
const order = await api.post('/api/payment/orders', {
  title: 'AI 学习会员',
  amount: 29.99,
  user_id: currentUser.id,
});

// 2. 发起支付，获取跳转 URL
const { payment_url, trade_no } = await api.post('/api/payment/pay', {
  order_id: order.id,
  channel: 'alipay',  // 或 'wxpay'
});

// 3. 跳转到支付页面
window.location.href = payment_url;

// 4. 支付完成后，用户会被重定向回 return_url
// 前端轮询确认支付状态
const pollStatus = async () => {
  const res = await api.get(`/api/payment/status/${trade_no}`);
  if (res.status === 'success') {
    // 支付成功，更新 UI
  }
};
```

### 7.2 React/Vue 组件示例

```tsx
function PaymentPage() {
  const [status, setStatus] = useState('idle');

  const handlePay = async (channel: string) => {
    setStatus('paying');
    const { payment_url } = await createPayment(orderId, channel);
    window.open(payment_url, '_blank');
    // 开始轮询
    pollPaymentStatus(tradeNo, (s) => {
      setStatus(s); // 'success' | 'pending' | 'failed'
    });
  };

  return (
    <div>
      <button onClick={() => handlePay('alipay')}>支付宝</button>
      <button onClick={() => handlePay('wxpay')}>微信支付</button>
      {status === 'paying' && <p>等待支付中...</p>}
      {status === 'success' && <p>支付成功！</p>}
    </div>
  );
}
```

---

## 8. 本地测试

### 8.1 单元测试

```python
# tests/unit/test_epay_client.py
import hashlib
import pytest
from studyagent.core.payment.epay import EpayClient, _md5_sign

@pytest.fixture
def client():
    return EpayClient(
        pid="1001",
        key="test_secret_key",
        gateway_url="https://epay.example.com",
    )

def test_create_payment_url(client):
    result = client.create_payment(
        out_trade_no="ORDER001",
        name="测试商品",
        money=10.00,
        channel="alipay",
        notify_url="https://example.com/notify",
        return_url="https://example.com/return",
    )
    assert "submit.php?" in result.payment_url
    assert "pid=1001" in result.payment_url
    assert "type=alipay" in result.payment_url

def test_verify_callback(client):
    params = {
        "pid": "1001",
        "type": "alipay",
        "out_trade_no": "ORDER001",
        "trade_no": "EPAY123",
        "name": "测试",
        "money": "10.00",
        "trade_status": "TRADE_SUCCESS",
    }
    params["sign"] = _md5_sign(params, "test_secret_key")
    params["sign_type"] = "MD5"

    assert client.verify_callback(params) is True
    result = client.parse_callback(params)
    assert result.out_trade_no == "ORDER001"
    assert result.trade_no == "EPAY123"
```

### 8.2 使用 ngrok 暴露本地端口

ePay 的异步回调需要一个公网可达的 URL。本地开发时用 ngrok：

```bash
# 安装 ngrok
brew install ngrok  # macOS
# 或从 https://ngrok.com 下载

# 启动后端
python -m studyagent.api.main

# 另一个终端，暴露 8000 端口
ngrok http 8000
# 会得到类似 https://xxxx.ngrok-free.app 的地址

# 修改 .env 中的回调地址
EPAY_NOTIFY_URL=https://xxxx.ngrok-free.app/api/payment/notify
EPAY_RETURN_URL=http://localhost:3000/payment/result
```

---

## 9. 部署上线

### 9.1 配置检查清单

- [ ] `.env` 中 `EPAY_ENABLED=true`
- [ ] `EPAY_NOTIFY_URL` 使用 HTTPS 公网域名
- [ ] `EPAY_RETURN_URL` 使用 HTTPS 公网域名
- [ ] 回调接口 `/api/payment/notify` 无需认证（ePay 服务器调用）
- [ ] 数据库已创建 `orders` 和 `payments` 表

### 9.2 数据库迁移

```bash
# 使用 Alembic
alembic revision --autogenerate -m "add payment tables"
alembic upgrade head
```

### 9.3 Nginx 配置示例

```nginx
location /api/payment/notify {
    proxy_pass http://127.0.0.1:8000;
    # ePay 回调使用 form POST，确保 body 大小限制合理
    client_max_body_size 1m;
}
```

---

## 10. 安全注意事项

### 必须做的

1. **永远不要把 KEY 提交到 Git** — `.env` 必须在 `.gitignore` 中
2. **回调必须验签** — `verify_callback` 是防止伪造支付的唯一步骤
3. **回调幂等** — ePay 可能多次发送同一回调，用 `trade_no` 做去重
4. **金额校验** — 回调中的 `money` 必须与订单金额一致
5. **回调 URL 必须用 HTTPS** — 防止中间人攻击

### 建议做的

6. **限制回调 IP** — 只允许 ePay 服务商的 IP 调用 `/notify`
7. **订单过期** — 设置 `payment_expire_minutes`，超时自动关闭
8. **日志审计** — 记录所有支付创建和回调事件
9. **监控告警** — 监控回调失败率和支付成功率

### 绝对不能做的

- 不要在前端暴露 `EPAY_KEY`
- 不要跳过验签直接信任回调参数
- 不要用 GET 请求处理回调（ePay 用 POST）

---

## 附录：ePay V1 协议速查

### 下单参数（submit.php）

| 参数 | 说明 | 必填 |
|------|------|------|
| pid | 商户 ID | 是 |
| type | 支付类型：alipay/wxpay/qqpay | 是 |
| out_trade_no | 商户订单号 | 是 |
| notify_url | 异步回调地址 | 是 |
| return_url | 同步跳转地址 | 是 |
| name | 商品名称 | 是 |
| money | 金额（元，两位小数） | 是 |
| sign | 签名 | 是 |
| sign_type | MD5 | 是 |

### 异步回调参数

| 参数 | 说明 |
|------|------|
| pid | 商户 ID |
| type | 支付类型 |
| out_trade_no | 商户订单号 |
| trade_no | ePay 订单号 |
| name | 商品名称 |
| money | 金额 |
| trade_status | TRADE_SUCCESS |
| sign | 签名 |
| sign_type | MD5 |

### 签名算法

```
1. 过滤空值、sign、sign_type 字段
2. 按字段名 ASCII 字母排序
3. 拼接: key1=value1&key2=value2&...
4. 末尾追加商户密钥
5. MD5 取 32 位小写
```

```
示例：
参数: pid=1001&type=alipay&money=10.00&name=测试
密钥: your_key
签名串: money=10.00&name=测试&pid=1001&type=alipayyour_key
sign = md5(签名串)
```

---

## 复用到其他项目的最小清单

只需复制以下文件，改一下 import 路径：

1. **`core/payment/epay.py`** — 易支付客户端（核心，无需修改）
2. **`core/config.py` 中的 EpayConfig** — 配置类
3. **`db/models.py` 中的 Order + Payment** — 数据库模型
4. **`api/routes/payment.py`** — API 路由（改一下 import）
5. **`.env`** — 填入你的服务商凭证

总计约 300 行代码，10 分钟完成集成。
