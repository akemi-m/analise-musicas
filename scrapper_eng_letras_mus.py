from httpx import get
from parsel import Selector
from csv import DictWriter

def letra(url: str, traducao: bool = False) -> str:
    if traducao:
        if '#album' in url:
            url_parts = url.split('#', 1)
            url = url_parts[0].rstrip('/') + '/english.html'
            if len(url_parts) > 1:
                url += '#' + url_parts[1]
        else:
            url = url.rstrip('/') + '/english.html'

    response = get(url)
    if response.status_code != 200:
        return 'ERRO AO ACESSAR A PÁGINA'

    s = Selector(response.text)
    verses = s.css('div.lyric-translation span.verse::text').getall()
    cleaned = [v.strip() for v in verses if v.strip()]
    return '\n'.join(cleaned) if cleaned else 'LETRA INDISPONÍVEL'

def faixas(url: str) -> list[tuple[str, str]]:
    response = get(url)
    if response.status_code != 200:
        return []

    s = Selector(response.text)
    musicas = []

    for li in s.css('li.songList-table-row'):
        nome = li.css('div.songList-table-songName span::text').get(default='').strip()
        href = li.css('a.songList-table-playButton::attr(href)').get(default='').strip()

        if nome and href:
            link_completo = f'https://www.letras.mus.br{href}'
            musicas.append((nome, link_completo))

    return musicas

def discos(url: str) -> list[tuple[str, str, str]]:
    response = get(url)
    if response.status_code != 200:
        return []

    s = Selector(response.text)
    resultados = []

    for bloco in s.css('div.songList-header-content'):
        disco_url = bloco.css('h1 a::attr(href)').get(default='').strip()
        disco_nome = bloco.css('h1 a::text').get(default='').strip()
        disco_ano = bloco.css('div.songList-header-info::text').get(default='').strip()

        if disco_url and disco_nome and disco_ano:
            url_completo = f'https://www.letras.mus.br{disco_url}'
            resultados.append((url_completo, disco_nome, disco_ano))

    return resultados

url = 'https://www.letras.mus.br/red-velvet/discografia/'

with open('red_velvet.csv', 'w', encoding='utf-8', newline='') as f:
    writer = DictWriter(f, ['album', 'data', 'musica', 'letra'])
    writer.writeheader()

    for disco_url, disco_nome, disco_ano in discos(url):
        for musica_nome, musica_url in faixas(disco_url):
            row = {
                'album': disco_nome,
                'data': disco_ano,
                'musica': musica_nome,
                'letra': letra(musica_url, traducao=True)
            }
            print(row)
            writer.writerow(row)
