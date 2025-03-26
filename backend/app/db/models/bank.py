""" Model for Banks """
from tortoise import fields
from tortoise.models import Model

class Bank(Model):
    """ Model for Banks """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    description = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    