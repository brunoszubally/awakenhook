from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Membership(BaseModel):
    id: int
    title: str
    price: str
    period: str
    period_type: str


class Member(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    display_name: str
    registered_at: str


class SubscriptionData(BaseModel):
    id: str
    subscr_id: str
    gateway: str
    price: str
    period: str
    period_type: str
    status: str
    created_at: str
    total: str
    membership: Membership
    member: Member
    cc_last4: Optional[str] = None
    cc_exp_month: Optional[str] = None
    cc_exp_year: Optional[str] = None


class MemberpressWebhook(BaseModel):
    event: str
    type: str
    data: SubscriptionData


class MailerliteSubscriber(BaseModel):
    email: str
    fields: dict
    groups: Optional[List[str]] = None
    status: str = "active"
