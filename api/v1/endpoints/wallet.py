from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.wallet import (
    AttachWalletRequest,
    BalanceResponse,
    BalanceUpdateRequest,
    RedeemPointsRequest,
    RedeemResponse,
    WalletResponse,
)
from services.points_service import get_points_balance, redeem_points, update_points_balance
from services.wallet_service import attach_wallet, get_wallet

router = APIRouter()


@router.post("/attach", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def attach_user_wallet(
    payload: AttachWalletRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wallet = attach_wallet(db, current_user, payload.wallet_address, payload.wallet_type)
    return WalletResponse(wallet_address=wallet.wallet_address, wallet_type=wallet.wallet_type)


@router.get("/me", response_model=WalletResponse)
def read_user_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = get_wallet(db, current_user)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not attached")
    return WalletResponse(wallet_address=wallet.wallet_address, wallet_type=wallet.wallet_type)


@router.get("/balance", response_model=BalanceResponse)
def read_balance(current_user: User = Depends(get_current_user)):
    return BalanceResponse(points_balance=get_points_balance(current_user))


@router.post("/balance/update", response_model=BalanceResponse)
def balance_update(
    payload: BalanceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        balance = update_points_balance(db, current_user, payload.amount, payload.reason)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BalanceResponse(points_balance=balance)


@router.post("/redeem", response_model=RedeemResponse)
def redeem_user_points(
    payload: RedeemPointsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        redeem_points(db, current_user, payload.points, payload.reason)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RedeemResponse(message="Points redeemed successfully", points_balance=get_points_balance(current_user))
