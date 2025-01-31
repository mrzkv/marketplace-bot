import asyncio

async def check_phone_number(phone_number: str) -> bool:
    if phone_number[0] == '8':
        if len(phone_number) == 11:
            return True
    elif phone_number[0:2] == '+7':
        if len(phone_number) == 12:
            return True
    return False
