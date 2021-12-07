'''Questo file è il file principale per la parte di OCR.'''
from ImageToOCR.text_detector import detect_text
from ImageToOCR.scrape_infos import scrape_infos
from ImageToOCR.img_manipulator import enhance_image

def scrape_image(path: str) -> dict:
    """
    Funzione principale del progetto,
    elabora l'immagine che gli arriva e
    ritorna i dati estrapolati dello scontrino.
    """
    recognized: str = enhance_image(path)
    if recognized is None:
        print("Errore, nessun'immagine rilevata.")
        return dict(message="Errore, nessun'immagine rilevata.")
    text: str = detect_text(recognized)
    if text is None:
        print("Errore, nessun testo rilevato.")
        return dict(message="Errore, nessun testo rilevato.")
    infos: dict = scrape_infos(text)
    if infos is None:
        print("Errore, nessuna informazione rilevata.")
        return dict(message="Errore, nessuna informazione rilevata.")
    print("Infos: ", infos)
    return infos

if __name__ == '__main__':
    scrape_image('images/image.png')