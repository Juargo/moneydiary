from tortoise import fields
from tortoise.models import Model


class Subcategory(Model):
    """ Model for Subcategories """ 
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255, null=True)
    # Relaciones inversas definidas en otros modelos
    # transactions: ReverseRelation["Transaction"]

    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Subcategory """
        table = "subcategories"
