'''Questo file è il file principale per la parte di OCR.'''
from ImageToOCR.text_detector import detect_text
from ImageToOCR.scrape_infos import scrape_infos
# from img_manipulator import enhance_image


def string_to_price(price_string: str):
    """Converte una stringa in un float."""
    return float(price_string.replace("€", "").replace(",", "."))


def scrape_image(path: str) -> dict:
    """
    Funzione principale del progetto,
    elabora l'immagine che gli arriva e
    ritorna i dati estrapolati dello scontrino.
    """
    text_def: str = detect_text(path, "default")
    text_doc: str = detect_text(path, "document")
    if text_def is None or text_doc is None:
        print("Errore, nessun testo rilevato.")
        return dict(message="Errore, nessun testo rilevato.")
    infos_def: dict = scrape_infos(text_def)
    infos_doc: dict = scrape_infos(text_doc)
    if infos_def is None and infos_doc is None:
        print("Errore, nessuna informazione rilevata.")
        return dict(message="Errore, nessuna informazione rilevata.")
    final_infos: dict = best_infos(infos_def, infos_doc)
    print("Best infos: ", final_infos)
    return final_infos


def best_infos(infos_def: dict, infos_doc: dict) -> dict:
    """Ritorna il miglior dizionario di informazioni."""
    # Caso peggiore, entrambi None
    if infos_doc is None and infos_def is None:
        return dict(title="", price="0.00")
    # Caso migliore, entrambi hanno trovato la stessa soluzione
    if infos_def == infos_doc:
        return infos_def
    # Valuto la validità di 'price' di entrambi
    infos_doc_price_valid: bool = False
    infos_def_price_valid: bool = False
    try:
        if infos_doc is not None:
            string_to_price(infos_doc["price"])
            infos_doc_price_valid = True
        else:
            return infos_def
    except:
        try:
            if infos_def is not None:
                string_to_price(infos_def["price"])
                infos_def_price_valid = True
            else:
                return dict(title=infos_doc['title'], price="0.00")
        except:
            # se nessuno dei due ha 'price' valido, ritorno 0.00 come 'price'
            return dict(title=infos_doc["title"], price="0.00")

    # Caso in cui solo uno ha trovato soluzione
    if infos_def is None:
        return infos_doc

    # Se entrambi sono validi, ritorno il doc, se il doc non è valido ritorno il def
    if infos_doc_price_valid:
        return infos_doc
    if infos_def_price_valid:
        return infos_def
    return infos_doc

#if __name__ == '__main__':
#    scrape_image('images/burger.jpg')
#    scrape_image('images/eurospesa.jpg')
#    scrape_image('images/povo.jpg')
#    scrape_image('images/povo2.jpg')
