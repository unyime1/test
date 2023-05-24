"""
This module handles main service authentication related
functions.
"""
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashService:
    async def get_hash(self, string: str) -> str:
        """Hash a piece of string."""
        return pwd_context.hash(string)

    async def verify_hash(self, string: str, hash: str) -> bool:
        """Verify that hash is valid."""
        return pwd_context.verify(string, hash)


hash_service = HashService()
