import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging ayarları (detaylı hata ayıklama için DEBUG seviyesi)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Bot token'ı (BotFather'dan aldığınız token ile değiştirin)
TOKEN = "8435669727:AAGoKJa1kwcS4RYExyGyZbTMUCGnVzy95kM"  # BURAYA GEÇERLİ TOKEN'INIZI YAZIN

# is.gd link kısaltma API'si
SHORTENER_URL = "https://is.gd/create.php"

# /start komutu için handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("start komutu alındı")
    await update.message.reply_text("Merhaba! Bana bir dosya gönder, sana doğrudan indirilebilir kısa bir link vereyim.")

# Link kısaltma fonksiyonu
def shorten_url(long_url):
    logger.debug(f"Link kısaltma isteği: {long_url}")
    try:
        params = {"format": "simple", "url": long_url}
        response = requests.get(SHORTENER_URL, params=params)
        if response.status_code == 200 and response.text.startswith("https://"):
            logger.debug(f"Kısaltılmış link: {response.text.strip()}")
            return response.text.strip()
        else:
            logger.error(f"Link kısaltma hatası: {response.text}")
            return long_url
    except Exception as e:
        logger.error(f"Link kısaltma hatası: {e}")
        return long_url

# Dosya alındığında çalışacak handler
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Dosya alındı")
    document = update.message.document
    if document:
        try:
            file_name = document.file_name
            file_id = document.file_id
            logger.debug(f"Dosya: {file_name}, ID: {file_id}")

            # Dosyayı Telegram'dan al
            file = await context.bot.get_file(file_id)
            file_url = file.file_path
            logger.debug(f"Doğrudan dosya URL'si: {file_url}")

            # Linki kısalt
            short_url = shorten_url(file_url)
            await update.message.reply_text(
                f"Dosya alındı: {file_name}\n"
                f"Doğrudan indirme linki: {short_url}\n"
                f"⚠️ Not: Bu link Telegram sunucularında saklanır ve genellikle kalıcıdır, ancak Telegram politikalarına bağlıdır."
            )
        except Exception as e:
            logger.error(f"Dosya işleme hatası: {e}")
            await update.message.reply_text(f"Bir hata oluştu: {str(e)}. Lütfen tekrar deneyin.")
    else:
        logger.debug("Dosya bulunamadı")
        await update.message.reply_text("Lütfen bir dosya gönderin.")

# Hata yönetimi
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    try:
        logger.debug("Bot başlatılıyor...")
        # Bot uygulamasını başlat
        app = Application.builder().token(TOKEN).build()

        # Komut ve mesaj handler'larını ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: update.message.reply_text("Lütfen bir dosya gönderin.")))

        # Hata handler'ı
        app.add_error_handler(error)

        # Botu başlat
        logger.info("Bot çalışıyor...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot başlatma hatası: {e}")
        print(f"Bot başlatılırken hata oluştu: {e}")

if __name__ == '__main__':
    main()