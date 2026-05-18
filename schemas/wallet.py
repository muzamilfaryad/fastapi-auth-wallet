from pydantic import BaseModel


class AttachWalletRequest(BaseModel):
    wallet_address: str
    wallet_type: str


class BalanceUpdateRequest(BaseModel):
    amount: int
    reason: str


class RedeemPointsRequest(BaseModel):
    points: int
    reason: str


class WalletResponse(BaseModel):
    wallet_address: str
    wallet_type: str


class BalanceResponse(BaseModel):
    points_balance: int


class RedeemResponse(BaseModel):
    message: str
    points_balance: int
