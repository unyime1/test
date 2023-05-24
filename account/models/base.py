from tortoise import fields
from tortoise.models import Model


class AbstractBaseModel(Model):
    """Define abstract base model."""

    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted = fields.BooleanField(default=False)

    class Meta:
        abstract = True
