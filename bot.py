import os, tempfile, fitz
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]
DPI = int(os.environ.get("DPI", "150"))

def rasterize(in_path, out_path, dpi=DPI):
    doc = fitz.open(in_path)
    out = fitz.open()
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        p = out.new_page(width=page.rect.width, height=page.rect.height)
        p.insert_image(p.rect, pixmap=pix)
    out.save(out_path, deflate=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a PDF and I'll send back a flattened version.")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not (doc.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text("Please send a PDF file.")
        return
    await update.message.reply_text("Processing your PDF...")
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "input.pdf")
        out_path = os.path.join(tmp, "output.pdf")
        tg_file = await doc.get_file()
        await tg_file.download_to_drive(in_path)
        rasterize(in_path, out_path)
        with open(out_path, "rb") as f:
            await update.message.reply_document(f, filename="rasterized.pdf")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.run_polling()

if __name__ == "__main__":
    main()
