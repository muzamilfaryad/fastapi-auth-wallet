from sqlalchemy.orm import Session

from models.points import PointRedeem, PointsLedger
from models.user import User


def get_points_balance(user: User) -> int:
    return user.points_balance or 0


def update_points_balance(db: Session, user: User, amount: int, reason: str) -> int:
    if amount == 0:
        return get_points_balance(user)
    if amount < 0 and get_points_balance(user) < abs(amount):
        raise ValueError("Insufficient points balance")

    user.points_balance = get_points_balance(user) + amount
    db.add(user)
    db.add(
        PointsLedger(
            user_id=user.id,
            amount=abs(amount),
            transaction_type="credit" if amount > 0 else "debit",
            reason=reason,
        )
    )
    db.commit()
    db.refresh(user)
    return get_points_balance(user)


def redeem_points(db: Session, user: User, points: int, reason: str) -> PointRedeem:
    if points <= 0:
        raise ValueError("Redeem points must be greater than zero")
    if get_points_balance(user) < points:
        raise ValueError("Insufficient points balance")

    user.points_balance = get_points_balance(user) - points
    redeem = PointRedeem(user_id=user.id, points_used=points, status="completed")
    db.add(user)
    db.add(redeem)
    db.add(
        PointsLedger(
            user_id=user.id,
            amount=points,
            transaction_type="debit",
            reason=reason,
        )
    )
    db.commit()
    db.refresh(user)
    db.refresh(redeem)
    return redeem
