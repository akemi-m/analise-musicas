from csv import DictWriter
from httpx import get
import dateparser
from parsel import Selector

def letra(url: str) -> str:
    response = get(url)
    s = Selector(response.text)
    
    lyrics_blocks = s.css('div[data-lyrics-container="true"]')
    full_lyrics = []
    
    for block in lyrics_blocks:
        parts = block.xpath('.//text()').getall()
        cleaned = [part.strip() for part in parts if part.strip()]
        full_lyrics.append('\n'.join(cleaned))
    
    return '\n\n'.join(full_lyrics)

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

    for disco_url, disco_nome, disco_data in discos(url):
        if not disco_url:
            continue

        for nome_faixa, url_faixa in faixas(disco_url):
            if not url_faixa:
                continue

            row = {
                'album': disco_nome,
                'data': dateparser.parse(disco_data),
                'musica': nome_faixa,
                'letra': letra(url_faixa)
            }
            print(row)
            writer.writerow(row)
