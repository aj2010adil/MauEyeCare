from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from dependencies import get_current_user_id
from schemas import PosCheckout, CheckoutResponse
from pos import PosOrder, PosOrderLine, Payment, LoyaltyAccount
from product import Product
from stock import StockBatch


router = APIRouter()


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(payload: PosCheckout, db: AsyncSession = Depends(get_db_session), user_id: str = Depends(get_current_user_id)):
    if not payload.lines:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate totals
    subtotal = 0
    gst_amount = 0
    for ln in payload.lines:
        line_total = ln.price * ln.quantity
        subtotal += line_total
        gst_amount += line_total * float(ln.gst_rate) / 100
    total = subtotal + gst_amount - float(payload.discount_amount)
    paid = sum(float(p.get("amount", 0)) for p in payload.payments)

    order = PosOrder(
        patient_id=payload.patient_id,
        order_no="INV-" + str(func.random()),
        subtotal=subtotal,
        gst_amount=gst_amount,
        discount_amount=payload.discount_amount,
        total=total,
        paid_amount=paid,
    )
    db.add(order)
    await db.flush()

    for ln in payload.lines:
        db.add(PosOrderLine(order_id=order.id, product_id=ln.product_id, batch_id=ln.batch_id, quantity=ln.quantity, price=ln.price, gst_rate=ln.gst_rate, discount_rate=ln.discount_rate))
        if ln.batch_id:
            batch = await db.get(StockBatch, ln.batch_id)
            if batch and batch.quantity >= ln.quantity:
                batch.quantity -= ln.quantity

    for p in payload.payments:
        db.add(Payment(order_id=order.id, method=p.get("method", "cash"), amount=p.get("amount", 0), reference=p.get("reference")))

    # Loyalty simple: earn 1 point per 100 spent
    if payload.patient_id and total > 0:
        points = int(total // 100)
        acct = (await db.execute(select(LoyaltyAccount).where(LoyaltyAccount.patient_id == payload.patient_id))).scalar_one_or_none()
        if not acct:
            acct = LoyaltyAccount(patient_id=payload.patient_id, points=0)
            db.add(acct)
            await db.flush()
        acct.points += points
        order.loyalty_points_earned = points

    await db.commit()
    return {"order_id": order.id, "total": float(total), "paid": float(paid)}
