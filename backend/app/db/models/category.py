from tortoise import fields
from tortoise.models import Model


class Category(Model):
    """ Model for Category """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255, null=True)
    
    # Relaciones
    budget = fields.ForeignKeyField('models.Budget', related_name='categories')
    # Relaciones inversas
    # subcategories: ReverseRelation["Subcategory"]
    
    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Category """
        table = "category"
        # Aseguramos que el nombre sea único para un presupuesto específico
        unique_together = (("name", "budget"),)
