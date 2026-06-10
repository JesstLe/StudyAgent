from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from studyagent.core.config import load_config
from studyagent.core.payment.epay import SUPPORTED_CHANNELS, EpayClient
from studyagent.db.engine import create_session_factory
from studyagent.db.models import Order, Payment
from studyagent.api.schemas.payment import (
    ChannelInfo,
    CreateOrderRequest,
    CreatePaymentRequest,
    CreatePaymentResult,
    OrderListResponse,
    OrderResponse,
    PaymentChannelsResponse,
    PaymentCallbackResponse,
    PaymentResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])


def _get_epay_client() -> EpayClient | None:
    config = load_config()
    epay = config.epay
    if not epay.enabled or not epay.pid or not epay.key:
        return None
    return EpayClient(
        pid=epay.pid,
        key=epay.key,
        gateway_url=epay.gateway_url,
        sign_type=epay.sign_type,
    )


def _get_session():
    return create_session_factory()


def _order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        title=order.title,
        description=order.description,
        amount=float(order.amount),
        currency=order.currency,
        status=order.status,
        payment_channel=order.payment_channel,
        paid_at=order.paid_at,
        created_at=order.created_at,
    )


def _payment_to_response(payment: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        trade_no=payment.trade_no,
        channel=payment.channel,
        amount=float(payment.amount),
        fee_rate=float(payment.fee_rate),
        fee_amount=float(payment.fee_amount),
        status=payment.status,
        payment_url=payment.payment_url,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
    )


@router.get("/channels", response_model=PaymentChannelsResponse)
async def get_payment_channels():
    channels = [
        ChannelInfo(id="alipay", name="支付宝", fee_rate=0.0),
        ChannelInfo(id="wxpay", name="微信支付", fee_rate=0.0),
        ChannelInfo(id="qqpay", name="QQ钱包", fee_rate=0.0),
    ]
    return PaymentChannelsResponse(channels=channels)


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    req: CreateOrderRequest,
    user_id: str = Query(..., description="User ID"),
):
    session_factory = _get_session()
    async with session_factory() as session:
        trade_no = EpayClient.generate_trade_no()
        order = Order(
            user_id=user_id,
            order_no=trade_no,
            title=req.title,
            description=req.description,
            amount=req.amount,
            currency=req.currency,
            status="pending",
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return _order_to_response(order)


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    user_id: str = Query(...),
    status: str | None = Query(None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    session_factory = _get_session()
    async with session_factory() as session:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        if status:
            stmt = stmt.where(Order.status == status)
        total_stmt = select(Order).where(Order.user_id == user_id)
        if status:
            total_stmt = total_stmt.where(Order.status == status)

        result = await session.execute(stmt.offset(offset).limit(limit))
        orders = result.scalars().all()

        from sqlalchemy import func

        count_result = await session.execute(select(func.count()).select_from(total_stmt.subquery()))
        total = count_result.scalar() or 0

        return OrderListResponse(
            orders=[_order_to_response(o) for o in orders],
            total=total,
        )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    session_factory = _get_session()
    async with session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        return _order_to_response(order)


@router.post("/pay", response_model=CreatePaymentResult)
async def create_payment(req: CreatePaymentRequest):
    client = _get_epay_client()
    if not client:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="ePay not configured")

    config = load_config()
    session_factory = _get_session()
    async with session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == req.order_id))
        order = result.scalar_one_or_none()
        if not order:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "pending":
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Order status is {order.status}, cannot pay")

        trade_no = EpayClient.generate_trade_no()
        payment = Payment(
            order_id=order.id,
            trade_no=trade_no,
            channel=req.channel,
            amount=order.amount,
            status="created",
        )
        session.add(payment)

        epay_result = client.create_payment(
            out_trade_no=trade_no,
            name=order.title,
            money=float(order.amount),
            channel=req.channel,
            notify_url=config.epay.notify_url,
            return_url=config.epay.return_url,
        )

        payment.payment_url = epay_result.payment_url
        payment.status = "pending"
        order.payment_channel = req.channel

        await session.commit()
        await session.refresh(payment)

        return CreatePaymentResult(
            payment=_payment_to_response(payment),
            payment_url=epay_result.payment_url,
            qr_url=epay_result.qr_url,
        )


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

    logger.info("epay_notify_received", trade_no=callback.out_trade_no, money=callback.money)

    session_factory = _get_session()
    async with session_factory() as session:
        result = await session.execute(
            select(Payment).where(Payment.trade_no == callback.out_trade_no)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            logger.warning("epay_notify_payment_not_found", trade_no=callback.out_trade_no)
            return "fail"

        payment.status = "success"
        payment.epay_trade_no = callback.trade_no
        payment.callback_raw = json.dumps(params, ensure_ascii=False)
        payment.paid_at = datetime.now(timezone.utc)

        order_result = await session.execute(select(Order).where(Order.id == payment.order_id))
        order = order_result.scalar_one_or_none()
        if order:
            order.status = "paid"
            order.paid_at = datetime.now(timezone.utc)

        await session.commit()

    return "success"


@router.get("/status/{trade_no}", response_model=PaymentResponse)
async def get_payment_status(trade_no: str):
    session_factory = _get_session()
    async with session_factory() as session:
        result = await session.execute(select(Payment).where(Payment.trade_no == trade_no))
        payment = result.scalar_one_or_none()
        if not payment:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Payment not found")
        return _payment_to_response(payment)
