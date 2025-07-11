import asyncio
from sofi_money_functions import sofi_send_money

async def main():
    telegram_chat_id = "7953184130"  # Your Telegram ID
    recipient_account = "8104965538"  # Opay account
    recipient_bank = "999992"  # Opay bank code
    amount = 100
    pin = "1998"
    result = await sofi_send_money(telegram_chat_id, recipient_account, recipient_bank, amount, pin)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
