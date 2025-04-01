""" Transaction model for managing financial transactions
    in the application.
"""

from enum import Enum
from datetime import datetime

from tortoise import fields
from tortoise.models import Model

class TransactionType(str, Enum):
    """ Enum for transaction types """
    INGRESO = "Ingreso"
    GASTO = "Gasto"


class Transaction(Model):
    """ Model for Transactions """
    id = fields.IntField(pk=True)
    transaction_date = fields.DatetimeField(default=datetime.now)
    description = fields.CharField(max_length=255)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    type = fields.CharEnumField(TransactionType)

    # Relaciones
    user = fields.ForeignKeyField('models.User', related_name='transactions')
    bank = fields.ForeignKeyField('models.Bank', related_name='transactions')
    subcategory = fields.ForeignKeyField('models.Subcategory', related_name='transactions')

    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Transaction """
        table = "transactions"
