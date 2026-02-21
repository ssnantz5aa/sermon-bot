import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

user_mode = {}

# 시작 메뉴
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📁 설교교안 파일 제출", callback_data="file")],
        [InlineKeyboardButton("🚫 설교교안 미보고", callback_data="no_report")],
    ]
    await update.message.reply_text(
        "제출 유형을 선택하세요.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# 버튼 처리
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # 파일 제출 선택
    if query.data == "file":
        user_mode[user_id] = "file"
        await query.message.reply_text("설교교안 파일을 업로드하세요.")

    # 미보고 선택
    elif query.data == "no_report":
        user_mode[user_id] = "text"
        await query.message.reply_text(
            "※ 설교교안 미보고 예시\n\n"
            "지파번호. ○○지파: ○○지파 ○○교회(신 42. 1. 11.) → 이전 총회장님 말씀 영상 예배의 경우\n\n"
            "지파번호. ○○지파: 총회장님 왕림 예배\n\n"
            "위 형식에 맞게 작성하여 보내주세요."
        )

    # 특이사항 버튼 (파일 제출 후 등장)
    elif query.data == "special":
        user_mode[user_id] = "special_text"
        await query.message.reply_text(
            "※ 교안 특이사항 예시\n\n"
            "지파번호. ○○지파: 0/0 교안에서 표현이 일부 수정 됨\n"
            "지파번호. ○○지파: 0/0 교안 재보고(지파 연합 예배로 변경됨)\n"
            "지파번호. ○○지파: 0/0 교안 중 뒷 부분 4절부터 진행\n\n"
            "위 형식에 맞게 작성하여 보내주세요."
        )

# 메시지 처리
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mode = user_mode.get(user_id)

    # 파일 제출 모드
    if mode == "file":
        if update.message.document or update.message.photo or update.message.video:
            await update.message.forward(chat_id=ADMIN_CHAT_ID)
            await update.message.reply_text("파일 제출 완료되었습니다.")

            # 파일 제출 후 특이사항 버튼 표시
            keyboard = [
                [InlineKeyboardButton("⚠ 교안 특이사항 제출", callback_data="special")]
            ]
            await update.message.reply_text(
                "교안 특이사항이 있습니까?",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

            user_mode[user_id] = None
        else:
            await update.message.reply_text("텍스트는 제출할 수 없습니다. 파일만 업로드하세요.")

    # 미보고 텍스트 제출
    elif mode == "text":
        if update.message.text:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=update.message.text
            )
            await update.message.reply_text("미보고 제출 완료되었습니다.")
            user_mode[user_id] = None
        else:
            await update.message.reply_text("텍스트로 작성해주세요.")

    # 특이사항 텍스트 제출
    elif mode == "special_text":
        if update.message.text:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="※ 교안 특이사항\n" + update.message.text
            )
            await update.message.reply_text("특이사항 제출 완료되었습니다.")
            user_mode[user_id] = None
        else:
            await update.message.reply_text("텍스트로 작성해주세요.")

telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))
telegram_app.add_handler(MessageHandler(filters.ALL, handle_message))

if __name__ == "__main__":
    telegram_app.run_polling()
