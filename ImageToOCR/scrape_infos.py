'''Questo file gestisce lo scraping di informazioni dall'output di Google Cloud Vision.'''
from Levenshtein import ratio as levenshtein_ratio


def check_similarity(word: str, dataset: list) -> bool:
    '''
    Questa funzione calcola un indice di similarità
    tra parola e dataset ritornando True se trova almeno
    una parola nel dataset con similarità > threshold
    nei rispetti del primo argomento 'word'
    '''
    # * Caso base, se word è in dataset non calcolo neanche la similarità
    if word.lower() in dataset or word in dataset:
        return True
    similarity: float = 0
    # * Calcolo il ratio di Levenshtein tra word ed item massimo
    for item in dataset:
        if levenshtein_ratio(word.lower(), item.lower()) > similarity:
            similarity = levenshtein_ratio(word.lower(), item.lower())
        if levenshtein_ratio(word, item) > similarity:
            similarity = levenshtein_ratio(word, item)
    # * Se similarity è maggiore di threshold ritorno True, altrimenti False
    return similarity > 0.85


def scrape_infos(res: str) -> dict:
    '''
    Questa funzione prende in input una stringa
    contenente una risposta di Google Cloud Vision
    e restituisce un dizionario con le informazioni contenute
    res: stringa contenente una risposta di Google Cloud Vision
    '''
    symbols: list = ["*", "-", "/", "\\", "_", ".", ",", ":", ";", "+", "'"]
    totales: list = ["totale", "t0tale", "hotale", "h0tale", "totane", "t0tane", "hotane", "h0tane"]
    numbers_array: list = list()
    pos_numbers_array: list = list()
    epsilon: float = 25.00  # ? Errore di tolleranza

    # ? Taglio la risposta a solo il 90% superiore dello scontrino
    res = [
        item for item in res
        if item.bounding_poly.vertices[0].y < 0.90 * max([
            item.bounding_poly.vertices[0].y for item in res
        ])
    ]
    # ? Trovo la coordinata 'y' della parola 'totale'
    y_totale: float = [
        item.bounding_poly.vertices[0].y
        for item in res
        if check_similarity(item.description, totales)
    ][0]
    # * Trovo il titolo dello scontrino prendendo
    # * le parole più vicine in altezza alla prima parola in lista
    title: str = " ".join([
        item.description for item in res
        if abs(item.bounding_poly.vertices[0].y - [
            # ? Questo è y_title
            item.bounding_poly.vertices[0].y
            for item in res
            if item.description not in symbols
        ][0]) < epsilon
        and len(item.description) < 12 and item.description != ""
    ])
    for item in res:
        # ? Creo l'array numbers_array di numeri validi da res
        nan: bool = False
        if "," in item.description or "." in item.description:
            try:
                float(item.description.replace("€", "").replace(",", "."))
            except ValueError:
                nan = True
                pass
        else:
            nan = True
        if not nan:
            try:
                if len(item.description.split(",")) > 1 and len(item.description.split(",")[1]) > 1:
                    numbers_array.append(
                        item.description.replace("€", "").replace(",", "."))
                    pos_numbers_array.append(
                        abs(item.bounding_poly.vertices[0].y - y_totale))
                    continue
                if len(item.description.split(".")) > 1 and len(item.description.split(".")[1]) > 1:
                    numbers_array.append(
                        item.description.replace("€", "").replace(",", "."))
                    pos_numbers_array.append(
                        abs(item.bounding_poly.vertices[0].y - y_totale))
                    continue
            except ValueError:
                pass

    # * Peso tutti i numeri validi con y_totale ordinandoli per distanza dal totale
    # * Infine scelgo il primo numero valido in lista con occorrenze == max_occorrenze
    # * Facendo così anche se ho 2 valori con stesse occorrenze
    # * preferenzio la più vicina alla scritta "TOTALE"
    # ? Trovo numero massimo di occorrenze in numbers_array
    n_occ_max: int = max([numbers_array.count(item) for item in numbers_array])
    # ? Sorto numbers_array per distanza da y_totale usando pos_numbers_array
    numbers_array = [item for _, item in sorted(
        zip(pos_numbers_array, numbers_array))]
    # ? Prendo il primo numero con almeno n_occ_max - 1 occorrenze
    for item in numbers_array:
        if numbers_array.count(item) == n_occ_max:
            price: str = item.replace("€", "").replace(",", ".")
            break

    return dict(title=title, price=price)
