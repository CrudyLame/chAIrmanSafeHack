from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import httpx
from src.config import get_settings

settings = get_settings()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
tx_cache = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Welcome to chAIrman bot! You can start chatting, and I'll forward your messages to the AI.")

@dp.message()
async def handle_message(message: types.Message):
    async with httpx.AsyncClient() as client:
        response = await client.post("YOUR_CHATBOT_ENDPOINT", json={"message": message.text})
        await message.answer(response.json()["response"])

async def send_tx_confirmation(tx_hash: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Confirm", callback_data=f"c_{tx_hash[:32]}"),
                InlineKeyboardButton(text="Reject", callback_data=f"r_{tx_hash[:32]}")
            ]
        ]
    )
    tx_cache[tx_hash[:32]] = tx_hash
    
    for admin_id in settings.ADMIN_IDS:
        await bot.send_message(
            chat_id=admin_id,
            text=f"Do you want to confirm transaction {tx_hash}?",
            reply_markup=keyboard
        )

@dp.callback_query(lambda c: c.data.startswith(("c_", "r_")))
async def process_tx_callback(callback: types.CallbackQuery):
    try:
        action, short_hash = callback.data.split("_")
        tx_hash = tx_cache.get(short_hash)
        if not tx_hash:
            await callback.answer("Transaction expired or not found")
            return
        
        if action == "c":
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "http://cow-service:3000/api/safe/confirm",
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json"
                        },
                        json={
                            "signer": settings.HUMAN_SIGNER_1_PRIVATE_KEY,
                            "safeAddress": settings.SAFE_ADDRESS,
                            "safeTxHash": tx_hash
                        }
                    )
                await callback.message.edit_text("Transaction confirmed!")
            except Exception as e:
                await callback.message.edit_text(f"Failed to confirm transaction: {str(e)}")
        else:
            await callback.message.edit_text("Please go to safe dashboard to reject the transaction")
        
        del tx_cache[short_hash]
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Error processing callback: {str(e)}")
