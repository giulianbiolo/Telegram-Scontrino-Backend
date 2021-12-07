'''Questo file gestisce il riconoscimento di testo in un'immagine.'''
from google.cloud import vision
import io


def detect_text(path: str, method: str) -> str:
    """Ritorna il testo rilevato nell'immagine."""
    # Inizializzazione del client di vision
    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}
    client = vision.ImageAnnotatorClient(client_options=client_options)
    # Apro l'immagine da riconoscere
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    # La trasformo in un'immagine di vision
    image = vision.Image(content=content)
    # Riconosco il testo
    if 'document' in method:
        response = client.document_text_detection(image=image)
    elif 'default' in method:
        response = client.text_detection(image=image)
    else:
        response = client.text_detection(image=image)
    texts = response.text_annotations

    '''
    # Questo codice è per stampare tutti i testi trovati con le relative coordinate
    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
    '''

    # Handling errori di vision
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return texts