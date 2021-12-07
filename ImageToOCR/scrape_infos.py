'''Questo file gestisce lo scraping di informazioni dall'output di Google Cloud Vision.'''
from Levenshtein import ratio as levenshtein_ratio


def check_similarity(word: str, dataset: list[str]) -> bool:
    '''
    Questa funzione calcola un indice di similarità
    tra parola e dataset ritornando True se trova almeno
    una parola nel dataset con similarità > threshold
    nei rispetti del primo argomento 'word'
    '''
    #  Caso base, se word è in dataset non calcolo neanche la similarità
    if word.lower() in dataset or word in dataset:
        return True
    similarity: float = 0
    for item in dataset:
        # Calculate the Levenshtein distance between word and item
        if levenshtein_ratio(word.lower(), item.lower()) > similarity:
            similarity = levenshtein_ratio(word.lower(), item.lower())
        if levenshtein_ratio(word, item) > similarity:
            similarity = levenshtein_ratio(word, item)
    # If the similarity is greater than the threshold, return True
    if similarity > 0.75:
        # print("Similarity: ", similarity, " for word: ", word)
        return True
    return False


def find_in_vocab(word: str) -> str:
    '''
    Questa funzione ricerca nei vocabolari inglesi ed
    italiani la parola più simile a 'word' e la ritorna
    '''
    with open("datasets/words_english.txt", "r") as voc:
        vocab_en: list[str] = voc.read().splitlines()
    with open("datasets/words_italian.txt", "r") as voc:
        vocab_it: list[str] = voc.read().splitlines()
    with open("datasets/my_vocab.txt", "r") as voc:
        my_vocab: list[str] = voc.read().splitlines()
    max_similarity: float = 0
    max_word: str = None
    for line in vocab_en:
        if levenshtein_ratio(word.lower(), line) > max_similarity:
            max_similarity = levenshtein_ratio(word.lower(), line)
            max_word = line
    for line in vocab_it:
        if levenshtein_ratio(word.lower(), line) > max_similarity:
            max_similarity = levenshtein_ratio(word.lower(), line)
            max_word = line
    for line in my_vocab:
        if levenshtein_ratio(word.lower(), line) > max_similarity:
            max_similarity = levenshtein_ratio(word.lower(), line)
            max_word = line
    if max_similarity > 0.88:
        return max_word.upper()
    else:
        return word.upper()


def scrape_infos(res: str) -> dict[str, str]:
    '''
    Questa funzione prende in input una stringa
    contenente una risposta di Google Cloud Vision
    e restituisce un dizionario con le informazioni contenute
    res: stringa contenente una risposta di Google Cloud Vision
    '''
    # Y_TOT: posizione y di dove si trova 'Totale'
    # Y_COM: posizione y di dove si trova 'Complessivo'
    y_tot: int = None
    y_com: int = None
    epsilon = 25  # Errore di tolleranza
    # Array symbols è per evitare che il titolo esca fuori uno dei caratteri speciali inutili che usano negli scontrino per far bellino
    symbols: list[str] = ["*", "-", "/", "\\",
                          "_", ".", ",", ":", ";", "+", "'"]
    totales: list[str] = ["TOTALE", "TOTANE", "OTALE",
                          "TOTAL", "T0TALE", "ToTALE", "HOTALE", "H0TALE"]
    complessives: list[str] = ["COMPLESSIVO", "CONPLESSIVO", "OMPLESSIVO", "ONPLESSIVO", "COMPLESSIV0",
                               "CONPLESSIV0", "COMPLESSIVo", "CoMPLESSIVO", "CoNPLESSIVO", "CONPLESSIVo", "cOMPLESSIVO", "cONPLESSIVO"]
    temp_title: list[str] = []
    for item in res:
        if item.description not in symbols:
            y_title = item.bounding_poly.vertices[0].y
            break
    for item in res:
        if item.bounding_poly.vertices[0].y < y_title + epsilon and item.bounding_poly.vertices[0].y > y_title - epsilon and len(item.description) < 12:
            temp_title.append(item.description)
    temp_title = [find_in_vocab(x) for x in temp_title if x != ""]
    title: str = " ".join(temp_title)
    for item in res:
        if check_similarity(item.description, totales):
            y_tot = item.bounding_poly.vertices[0].y
            continue
        if check_similarity(item.description, complessives):
            y_com = item.bounding_poly.vertices[1].y
            continue
    # Se non trovo il totale o complessivo, non posso neanche calcolarmi dove si trova il prezzo, quindi ritorno None
    if y_tot is None or y_com is None:
        return None
    # Calcolo la posizione del prezzo
    diff: int = (y_tot - y_com) * 2
    y_price: int = y_com - diff
    price: str = None
    for item in res:
        # Trovo il prezzo, che si trova a y_price, ed è una stringa
        # Mi assicuro di non scambiare il prezzo con 'totale' o 'complessivo'
        if not (check_similarity(item.description, totales) or check_similarity(item.description, complessives)):
            if item.bounding_poly.vertices[0].y >= y_price - epsilon and item.bounding_poly.vertices[0].y <= y_price + epsilon:
                price = item.description
    return dict(title=title, price=price)
