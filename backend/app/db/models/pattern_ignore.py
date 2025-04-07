""" Pattern Ignore model for managing transaction patterns to ignore
    in the application.
"""

from tortoise import fields
from tortoise.models import Model

class PatternIgnore(Model):
    """ Model for Pattern Ignore """
    id = fields.IntField(pk=True)
    match_text = fields.CharField(max_length=255)
    description = fields.TextField()
    
    # Relation to User
    user = fields.ForeignKeyField('models.User', related_name='pattern_ignores')
    
    # Audit fields
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """ Meta class for PatternIgnore """
        table = "pattern_ignore"
