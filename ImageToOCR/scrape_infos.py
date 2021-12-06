'''Questo file gestisce lo scraping di informazioni dall'output di Google Cloud Vision'''

def scrape_infos(res: str) -> dict:
    '''
    Questa funzione prende in input una stringa
    contenente una risposta di Google Cloud Vision
    e restituisce un dizionario con le informazioni contenute
    '''
    y_tot = None
    y_com = None
    epsilon = 25
    title = None
    price_error = None
    iva_error = None
    symbols = ["*", "-", "/", "\\", "_", ".", ",", ":", ";", "+", "'"]
    totales = ["TOTALE", "TOTANE", "OTALE", "TOTAL", "T0TALE", "ToTALE"]
    complessives = ["COMPLESSIVO", "CONPLESSIVO", "OMPLESSIVO", "ONPLESSIVO", "COMPLESSIV0", "CONPLESSIV0", "COMPLESSIVo", "CoMPLESSIVO", "CoNPLESSIVO", "CONPLESSIVo", "cOMPLESSIVO", "cONPLESSIVO"]
    ivas = ["IVA", "INA", "iVA", "ivA", "IvA", "iNA"]
    for i in range(1, len(res)):
        if res[i].description not in symbols:
            title = res[i].description
            break
    for i in range(0, len(res)):
        for x in totales:
            if x in res[i].description:
                y_tot = res[i].bounding_poly.vertices[0].y
                break
        for x in complessives:
            if x in res[i].description:
                y_com = res[i].bounding_poly.vertices[1].y
                break
        for x in ivas:
            if x in res[i].description:
                y_iva = res[i].bounding_poly.vertices[1].y
                break
    if y_tot is None or y_com is None:
        return None
    diff = (y_tot - y_com) * 2
    y_price = y_com - diff
    y_iva_num = y_iva - diff
    price = None
    iva = None
    for i in range(0, len(res)):
        tr = False
        # Find the price, which is a string containing a number and it's vertex is located at y_price
        for x in totales:
            if x in res[i].description:
                tr = True
        for x in complessives:
            if x in res[i].description:
                tr = True
        for x in ivas:
            if x in res[i].description:
                tr = True
        if "di" in res[i].description or "cui" in res[i].description:
            tr = True
        if tr is False:
            if res[i].bounding_poly.vertices[0].y >= y_price - epsilon and res[i].bounding_poly.vertices[0].y <= y_price + epsilon:
                price = res[i].description
                price_error = res[i].bounding_poly.vertices[0].y - y_price
            if res[i].bounding_poly.vertices[0].y >= y_iva_num - epsilon and res[i].bounding_poly.vertices[0].y <= y_iva_num + epsilon:
                iva = res[i].description
                iva_error = res[i].bounding_poly.vertices[0].y - y_iva_num
    '''
    print("Y_TOT: ", y_tot)
    print("Y_COM: ", y_com)
    print("DIFF: ", diff)
    print("Y_PRICE: ", y_price)
    print("Y_IVA: ", y_iva)
    print("Y_IVA_NUM: ", y_iva_num)
    print("PRICE_ ERROR: ", price_error)
    print("IVA_ ERROR: ", iva_error)
    '''

    return dict(title=title, price=price, iva=iva)