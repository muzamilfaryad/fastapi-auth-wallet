from sqlalchemy.orm import Session

from models.user import User
from models.wallet import Wallet


def attach_wallet(db: Session, user: User, wallet_address: str, wallet_type: str) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if wallet:
        wallet.wallet_address = wallet_address
        wallet.wallet_type = wallet_type
    else:
        wallet = Wallet(user_id=user.id, wallet_address=wallet_address, wallet_type=wallet_type)
        db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def get_wallet(db: Session, user: User) -> Wallet | None:
    return db.query(Wallet).filter(Wallet.user_id == user.id).first()

