from sqlalchemy import Column, ForeignKey, Integer, Text

from .financial_base import FinancialBase


class Donation(FinancialBase):
    comment = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
