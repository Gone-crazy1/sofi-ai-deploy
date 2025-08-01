import asyncio
import os
from dotenv import load_dotenv
from functions.beneficiary_functions import save_beneficiary
from test_env import setup_test_environment

setup_test_environment()
load_dotenv()

print("✅ Script started")

async def test_save():
    print("🚀 Inside test_save function")
    try:
        print("➡️ Calling save_beneficiary()")
        result = await save_beneficiary(
            user_id="816378282",
            beneficiary_name="Janet Chinedu",
            account_number="3050111828",
            bank_code="999143",
            bank_name="9PSB",
            nickname="Janet",
            telegram_chat_id="816378282"
        )
        print("✅ Result:", result)
    except Exception as e:
        print("❌ Error during test_save:", str(e))

if __name__ == "__main__":
    asyncio.run(test_save())
