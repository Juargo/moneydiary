from tortoise import fields
from tortoise.models import Model


class Pattern(Model):
    """ Model for identification patterns """
    id = fields.IntField(pk=True)
    match_text = fields.CharField(max_length=255, description="Pattern expression for identification")
    
    # Relaciones
    subcategory = fields.ForeignKeyField('models.Subcategory', related_name='patterns')
    
    # Campos de auditoría
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for Pattern """
        table = "pattern"
        # Aseguramos que la expresión sea única para una subcategoría específica
        unique_together = (("match_text", "subcategory"),)
