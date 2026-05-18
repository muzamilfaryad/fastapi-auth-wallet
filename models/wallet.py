from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func

from core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (UniqueConstraint("user_id", name="uq_wallets_user_id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_address = Column(String, nullable=False)
    wallet_type = Column(String, nullable=False)
    attached_at = Column(DateTime(timezone=True), server_default=func.now())
