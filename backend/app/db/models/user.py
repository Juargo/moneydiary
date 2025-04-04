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
    
    # Reverse relation with PatternIgnore is automatically handled through the
    # related_name='pattern_ignores' in the PatternIgnore model

    class Meta:
        """ Meta class for User """
        table = "user"
