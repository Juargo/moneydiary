""" Model for User """
from tortoise import fields
from tortoise.models import Model

class User(Model):
    """ Model for User """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for User """
        table = "user"
