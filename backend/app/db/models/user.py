""" Model for Users """
from tortoise import fields
from tortoise.models import Model

class User(Model):
    """ Model for Users """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
