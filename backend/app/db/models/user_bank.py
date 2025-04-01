""" Model for User Bank relationship """
from tortoise import fields
from tortoise.models import Model

class UserBank(Model):
    """ Model for User Bank relationship """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='bank')
    bank = fields.ForeignKeyField('models.Bank', related_name='user')
    balance = fields.DecimalField(max_digits=15, decimal_places=0, default=0)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for UserBank """
        table = "user_bank"
        unique_together = (("user", "bank"),)
