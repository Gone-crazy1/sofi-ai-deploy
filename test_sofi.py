from assistant import get_assistant
import asyncio

async def test_group_welcome():
    assistant = get_assistant()
    response, data = await assistant.process_telegram_message(
        chat_id="123456789",
        message="",
        chat_type="group",
        group_id="1002527980655",
        is_admin=True,
        new_member={"username": "testuser"}
    )
    print("Group Welcome Response:", response)
    print("Function Data:", data)

async def test_group_announce():
    assistant = get_assistant()
    response, data = await assistant.process_telegram_message(
        chat_id="123456789",
        message="sofi announce Please DM Sofi to set up your account for league rewards!",
        chat_type="group",
        group_id="1002527980655",
        is_admin=True
    )
    print("Group Announce Response:", response)
    print("Function Data:", data)

async def test_private_onboarding():
    assistant = get_assistant()
    response, data = await assistant.process_telegram_message(
        chat_id="123456789",
        message="I want to set up my account",
        chat_type="private"
    )
    print("Private Onboarding Response:", response)
    print("Function Data:", data)

if __name__ == "__main__":
    asyncio.run(test_group_welcome())
    asyncio.run(test_group_announce())
    asyncio.run(test_private_onboarding())
