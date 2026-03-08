import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from loguru import logger
from src.config import settings
from src.fetcher import fetcher
from src.analyzer import analyzer
from src.database import db
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🚀 **IKI INTEL PRO** v2.0\n\n"
        f"Halo {user.first_name}! Saya adalah radar finansial pribadi Anda.\n\n"
        "📜 **Command Tersedia:**\n"
        "• /analyze - Jalankan analisis pasar detik ini juga.\n"
        "• /status - Cek kondisi kesehatan sistem bot.\n"
        "• /help - Panduan penggunaan dan terminologi.\n\n"
        "Bot ini juga akan mengirimkan update otomatis setiap hari.",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **PANDUAN IKI INTEL PRO**\n\n"
        "**Apa yang kami pantau?**\n"
        "Kami memantau pergerakan Harga Emas Antam (logam mulia) dan Indeks Harga Saham Gabungan (IHSG) secara real-time melalui radar AI.\n\n"
        "**Kenapa AI?**\n"
        "AI kami menyisir berita ekonomi terbaru dari ribuan sumber, meringkasnya, dan memberikan rekomendasi objektif.\n\n"
        "**Terminologi:**\n"
        "• 🟢 **Sentimen Positif**: Pasar sedang optimis.\n"
        "• 🔴 **Sentimen Negatif**: Pasar sedang berisiko.\n"
        "• 🟡 **Sentimen Netral**: Pasar sedang konsolidasi."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def run_analysis(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None):
    logger.info("Starting market analysis...")
    try:
        # Step 1: Fetch
        search_results = await fetcher.fetch_market_data()

        # Step 2: Analyze
        analysis = await analyzer.analyze(search_results)

        # Step 3: Get previous data for comparison
        prev_data = db.get_latest_price()

        # Step 4: Save to DB
        db.save_analysis(analysis)

        # Step 5: Comparison Logic
        gold_change_str = ""
        ihsg_change_str = ""
        if prev_data:
            prev_gold, prev_ihsg = prev_data
            if prev_gold and analysis.gold_price:
                diff = float(analysis.gold_price) - float(prev_gold)
                percent = (diff / float(prev_gold)) * 100
                symbol = "🔼" if diff > 0 else "🔻"
                gold_change_str = f" ({symbol} {percent:+.2f}%)"

            if prev_ihsg and analysis.ihsg_point:
                diff = float(analysis.ihsg_point) - float(prev_ihsg)
                percent = (diff / float(prev_ihsg)) * 100
                symbol = "🔼" if diff > 0 else "🔻"
                ihsg_change_str = f" ({symbol} {percent:+.2f}%)"

        # Step 6: Format Report
        report = (
            f"🔔 **IKI INTEL UPDATE**\n"
            f"📅 Tanggal Data: `{analysis.data_date}`\n\n"
            f"💰 **KONDISI SAAT INI**\n"
            f"- 🟡 Harga Emas: `Rp {analysis.gold_price:,.0f}/gr`{gold_change_str}\n"
            f"- 📊 IHSG: `{analysis.ihsg_point:,.2f}`{ihsg_change_str}\n\n"
            f"📈 **PREDIKSI & SENTIMEN**\n"
            f"Sentimen: **{analysis.sentiment}**\n"
            f"{analysis.summary}\n\n"
            f"🚦 **REKOMENDASI**\n"
            f"**[{analysis.recommendation}]**\n"
            f"Alasan: {analysis.reasoning}\n\n"
            f"⚠️ *Disclaimer: Ini adalah analisis AI, bukan saran keuangan mutlak.*"
        )

        if update:
            await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
        else:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
            await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=report, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception("Analysis failed")
        # Menggunakan pesan error yang generik untuk mencegah kebocoran informasi sensitif
        error_msg = "❌ **Terjadi kesalahan saat melakukan analisis.** Mohon coba lagi nanti atau hubungi administrator."
        if update:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Sedang memproses radar... mohon tunggu.")
    await run_analysis(update, context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot aktif dan radar berfungsi normal.")

def main():
    logger.info("Starting IKI INTEL PRO application...")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN.get_secret_value()).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))

    # Scheduler setup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_analysis, 'interval', minutes=settings.REFRESH_INTERVAL_MINUTES)
    scheduler.start()
    logger.info(f"Scheduler started with interval: {settings.REFRESH_INTERVAL_MINUTES} minutes")

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
