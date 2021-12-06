'''File che gestisce creazione e meccaniche del bot telegram di Scontrino.'''
import json
from pathlib import Path
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from ImageToOCR.ocr import scrape_image

def log_event(command: str, upd: Updater) -> None:
    '''Funzione che logga ogni evento causato dall'utente e dal bot'''
    print(" -> Eseguito /" + command + " da parte di " + get_username(upd))


def reply_user(text: str, upd: Updater) -> None:
    '''Rinominazione comoda della funzione che invia messaggi all'utente'''
    upd.message.reply_text(text)


def get_username(upd: Updater) -> str:
    '''Funzione che dato l'update ritorna il nome dell'utente'''
    return upd.message.chat.first_name


COMANDS_REPLY = '''\nPrima di tutto prova ad eseguire uno di questi comandi:
- /start | Per inizializzare il bot
- /help | Per avere aiuto'''
HELP_REPLY = '\nCon questo bot puoi gestire la botnet di Microsoft Rewards!' + COMANDS_REPLY


def start(update: Updater, _) -> None:
    '''Funzione per l'handling di /start'''
    log_event("start", update)
    if check_permissions(update) is True:
        update.message.reply_text('Benvenuto '
                                  + get_username(update)
                                  + '.'
                                  + HELP_REPLY,
                                  reply_markup=ReplyKeyboardMarkup(
                                    [['Start', 'Help', 'Contabilizza']],
                                    one_time_keyboard=False
                                  )
                                  )
    else:
        reply_user("Mi dispiace " + get_username(update) +
                   " ma non hai il permesso di eseguire questo bot.", update)


def handle_help(update: Updater, _) -> None:
    '''Funzione per l'handling di /help'''
    log_event("help", update)
    if check_permissions(update) is True:
        reply_user(HELP_REPLY, update)
    else:
        reply_user("Mi dispiace " + get_username(update) +
                   " ma non hai il permesso di eseguire questo bot.", update)


def handle_error(update: Updater, _) -> None:
    '''Funzione per handling di errori generici'''
    print("Errore: ")
    print(update)
    try:
        reply_user("C'è stato un errore! Presto chiamate gli sviluppatori!", update)
    except AttributeError:
        try:
            update.callback_query.message.reply_text(
                "C'è stato un errore! Presto chiamate gli sviluppatori!")
        except AttributeError:
            pass


def contab(update: Updater) -> None:
    '''Funzione che gestisce la contabilizzazione su Notion'''
    return None


def handle_text(update: Updater, _) -> None:
    '''Funzione per handling di messaggi generici ricevuti'''
    if check_permissions(update) is True:
        print("Testo: " + update.message.text)
        if update.message.text == "Start":
            return start(update, _)
        if update.message.text == "Help":
            return handle_help(update, _)
        if update.message.text == "Contabilizza":
            return reply_user("Ok, sono pronto, inviami un'immagine e contabilizzo subito!", update)
    else:
        reply_user("Mi dispiace " + get_username(update) +
                   " ma non hai il permesso di eseguire questo bot.", update)


def handle_callback_query(update: Updater, _) -> None:
    '''Funzione per handling di messaggi inline'''
    print("-> Data: " + update.callback_query.data)    
    if update.callback_query.data is not None:
        data_in = update.callback_query.data
        print(" -> " + get_username(update.callback_query) +
                " ha richiesto la contabilizzazione di un nuovo scontrino. ")
        reply_user(
            ("Potrebbe volerci qualche secondo,"
                " prenditi un caffè nel mentre."),
            update.callback_query
        )
        # Eseguo il comando di contabilizzazione
        # response = image_to_notion(data_in)
        print(" -> Rispondo a " + get_username(update.callback_query) + " con:")
        # Risposta al callback
        # reply_user(response, update.callback_query)
    return None


def image_handler(update: Updater, _) -> None:
    '''Funzione che gestisce l'invio di immagini'''
    print("Inviata immagine senza compressione.")
    return reply_user("Inviamela senza compressione pezzemmerd!", update)


def file_handler(update: Updater, context) -> None:
    '''Funzione che gestisce il download di file'''
    # context.bot.get_file(update.message.document).download()
    # Salvo l'immagine nella cartella 'images'
    with open("images/image.png", 'wb') as img_file:
        context.bot.get_file(update.message.document).download(out=img_file)
    reply_user("Immagine scaricata, contabilizzo...", update)
    # Eseguo il comando di contabilizzazione
    scraped_data: dict = scrape_image("images/image.png")
    if 'message' in scraped_data.keys():
        return reply_user(scraped_data['message'], update)
    
    return reply_user(f"Titolo: {scraped_data['title']}, Iva: {scraped_data['iva']}, Price: {scraped_data['price']}", update)
    # response = image_to_notion('images/image.png')
    # print(" -> Rispondo a " + get_username(update) + " con:")
    # Risposta al callback
    # reply_user(response, update)



def check_permissions(update: Updater) -> bool:
    '''Funzione che controlla se l'utente ha il permesso di svolgere un dato comando'''
    permitted = ['Giulian']
    if get_username(update) in permitted:
        return True
    return False


def main() -> None:
    '''Funzione main() del bot telegram, qua viene dichiarato e costruito il bot stesso'''
    # Token supersegreto identificativo del bot
    telegram_bot_token = None
    path: Path = Path(__file__).parent / 'token.json'
    with path.open("r", encoding="UTF-8") as json_data_file:
        config = json.load(json_data_file)
        telegram_bot_token = config['telegramBotToken']
    # Creo l'updater ed il dispatcher
    updater = Updater(telegram_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Aggiungo gli handler per i comandi
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", handle_help))
    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
    dispatcher.add_handler(MessageHandler(Filters.document, file_handler))

    # Aggiungo l'handler per testo normale
    dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

    # Aggiungo l'handler per i messaggi inline
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))

    # add an handler for errors
    # dispatcher.add_error_handler(handle_error)

    print("Bot inizializzato con successo!")
    # Eseguo il bot
    updater.start_polling()

    # Tengo aperto il bot finchè non viene richiesto Ctrl+C
    updater.idle()


if __name__ == '__main__':
    print("Inizializzo il bot...")
    main()
