'''Questo file gestisce l'interazione con il server Notion.'''
import json
from pathlib import Path
from notion.block import Block
from notion.client import NotionClient
from notion.collection import CollectionView


def init_client() -> NotionClient:
    '''Inizializza il client Notion.'''
    notion_token: str = None
    path: Path = Path(__file__).parent / 'token.json'
    with path.open("r", encoding="UTF-8") as json_data_file:
        config: dict = json.load(json_data_file)
        notion_token: str = config["notion_token"]
    if notion_token is None:
        print("Errore nella lettura del file di configurazione.")
        return None
    client: NotionClient = NotionClient(token_v2=notion_token)
    return client


def infos_to_notion(infos: dict) -> bool:
    '''Invia le informazioni di uno scontrino al server Notion.'''
    if check_infos_integrity(infos) is False:
        print("Errore di integrità delle informazioni raccolte.")
        return False
    client: NotionClient = init_client()
    if client is None:
        return False
    page: Block = client.get_block(
        "https://www.notion.so/giulianbiolo/011e1a10299e43acb76dddabd4b578e5?v=849a9212e3354b8c8b158361265bf600")
    if page.locked is True:
        page.locked = False
    cv: CollectionView = client.get_collection_view(
        "https://www.notion.so/giulianbiolo/011e1a10299e43acb76dddabd4b578e5?v=69a914defca9426299d15c0b9d4dac9f")
    row = cv.collection.add_row()
    row.Spesa = infos['title']
    if isinstance(infos['price'], float):
        row.Prezzo = infos['price']
    else:
        row.Prezzo = float(infos['price'].replace("€", "").replace(",", "."))
    return True


def check_infos_integrity(infos: dict) -> bool:
    '''Controlla che le informazioni siano valide.'''
    if infos is None:
        return False
    if 'title' not in infos.keys():
        return False
    if 'price' not in infos.keys():
        return False
    if isinstance(infos['title'], str) is False or (isinstance(infos['price'], str) is False and isinstance(infos['price'], float) is False):
        return False
    try:
        float(infos['price'].replace("€", "").replace(",", "."))
    except ValueError:
        return False
    return True
