from tortoise import fields
from tortoise.models import Model


class Subcategory(Model):
    """ Model for Subcategory """ 
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255, null=True)
    amount = fields.IntField(description="Amount in CLP without decimals")
    
    # Relaciones
    category = fields.ForeignKeyField('models.Category', related_name='subcategories')
    # Relaciones inversas
    # patterns: ReverseRelation["Pattern"]
    # transactions: ReverseRelation["Transaction"]

    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Subcategory """
        table = "subcategory"
        # Aseguramos que el nombre sea único para una categoría específica
        unique_together = (("name", "category"),)
