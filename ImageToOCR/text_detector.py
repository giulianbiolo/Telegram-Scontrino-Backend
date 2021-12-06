'''Questo file gestisce il riconoscimento di testo in un'immagine.'''

def detect_text(path: str) -> str:
    """Ritorna il testo rilevato nell'immagine."""
    from google.cloud import vision
    import io
    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}
    client = vision.ImageAnnotatorClient(client_options=client_options)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return texts