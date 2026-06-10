from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChannelInfo(BaseModel):
    id: str
    name: str
    fee_rate: float = 0.0
    fixed_fee: float = 0.0
    min_amount: float = 0.01
    max_amount: float = 50000.0


class PaymentChannelsResponse(BaseModel):
    channels: list[ChannelInfo]


class CreateOrderRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="CNY", max_length=10)


class CreatePaymentRequest(BaseModel):
    order_id: str
    channel: str = Field(..., pattern=r"^(alipay|wxpay|qqpay)$")


class OrderResponse(BaseModel):
    id: str
    order_no: str
    title: str
    description: str | None
    amount: float
    currency: str
    status: str
    payment_channel: str | None
    paid_at: datetime | None
    created_at: datetime


class PaymentResponse(BaseModel):
    id: str
    trade_no: str
    channel: str
    amount: float
    fee_rate: float
    fee_amount: float
    status: str
    payment_url: str | None
    paid_at: datetime | None
    created_at: datetime


class CreatePaymentResult(BaseModel):
    payment: PaymentResponse
    payment_url: str | None
    qr_url: str | None


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int


class PaymentCallbackResponse(BaseModel):
    success: bool
    message: str = ""
