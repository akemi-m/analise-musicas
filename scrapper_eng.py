from csv import DictWriter
from httpx import get
import dateparser
from parsel import Selector

def letra(url: str, traducao: bool = False) -> str:
    response = get(url)
    s = Selector(response.text)
    
    if traducao:
        links = s.css('a')
        for link in links:
            texto = link.css('::text').get(default='').strip().lower()
            if texto == 'english':
                traduzido_href = link.attrib.get('href')
                if traduzido_href:
                    response = get(traduzido_href)
                    s = Selector(response.text)
                    break

    lyrics_blocks = s.css('div[data-lyrics-container="true"]')
    full_lyrics = []

    for block in lyrics_blocks:
        parts = block.xpath('.//text()').getall()
        cleaned = [part.strip() for part in parts if part.strip()]
        full_lyrics.append('\n'.join(cleaned))

    return '\n\n'.join(full_lyrics) if full_lyrics else 'TRADUÇÃO INDISPONÍVEL'

def faixas(url: str) -> list[tuple[str, str]]:
    response = get(url)
    s = Selector(response.text)

    musicas = s.css('div.chart_row-content')

    return [
        (
            musica.css('h3.chart_row-content-title::text').get(default='').strip(),
            musica.css('a::attr(href)').get(default='')
        )
        for musica in musicas
    ]

def discos(url: str) -> list[tuple[str | None, ...]]:
    response = get(url)
    s = Selector(response.text)

    discos = s.css('li.ListItem__Container-sc-4f1bc3d5-0')

    resultado = []

    for disco in discos:
        disco_url = disco.css('a::attr(href)').get(default=None)
        disco_nome = disco.css('h3.ListItem__Title-sc-4f1bc3d5-4::text').get(default=None)
        disco_ano = disco.css('div.ListItem__Info-sc-4f1bc3d5-5::text').get(default=None)

        resultado.append((disco_url, disco_nome, disco_ano))

    return resultado

url = 'https://genius.com/artists/Red-velvet/albums'

with open('red_velvet.csv', 'w', encoding='utf-8', newline='') as f:
    writer = DictWriter(f, ['album', 'data', 'musica', 'letra'])
    writer.writeheader()

    for disco in discos(url):
        if not disco[0]:
            continue
        for faixa in faixas(disco[0]):
            if not faixa[1]:
                continue
            row = {
                'album': disco[1],
                'data': dateparser.parse(disco[2]),
                'musica': faixa[0],
                'letra': letra(faixa[1], traducao=True)
            }
            print(row)
            writer.writerow(row)
