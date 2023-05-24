import random
import string


async def create_random_code(number):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(number))
