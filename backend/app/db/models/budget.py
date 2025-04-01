from tortoise import fields
from tortoise.models import Model


class Budget(Model):
    """ Model for Budget """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=255, null=True)
    
    # Relaciones
    user = fields.ForeignKeyField('models.User', related_name='budgets')
    # Relaciones inversas
    # categories: ReverseRelation["Category"]
    
    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Budget """
        table = "budget"
        # Aseguramos que el nombre sea único para un usuario específico
        unique_together = (("name", "user"),)
