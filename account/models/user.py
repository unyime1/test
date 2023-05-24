from tortoise import fields

from models.base import AbstractBaseModel


class Users(AbstractBaseModel):
    """Define users database model"""

    email = fields.CharField(max_length=500, null=True)
    first_name = fields.CharField(max_length=500, null=True)
    last_name = fields.CharField(max_length=500, null=True)
    password_hash = fields.CharField(max_length=3000, null=True)
    user_class = fields.CharField(max_length=3000, default="base", null=True)
    is_verified = fields.BooleanField(default=False)


class UserFeedback(AbstractBaseModel):
    user = fields.ForeignKeyField(
        "models.Users", related_name="feedback", on_delete="CASCADE"
    )
    message = fields.TextField()
