import json
import math
import os

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# 【ウマ娘】全キャラの育成論と難易度一覧 - ゲームウィズ(GameWith)
url_game_with_characters = 'https://gamewith.jp/uma-musume/article/show/253241'

response_game_with_characters = requests.get(url_game_with_characters)
soup_game_with_characters = BeautifulSoup(response_game_with_characters.text, "html.parser")


def get_characters():
    soup = soup_game_with_characters
    data = []

    for table in soup.select('table'):
        if table.parent.get('class', False) is False:
            continue
        if table.parent['class'][0] == 'umamusume-ikusei-ichiran':
            for tr in table.find_all('tr')[1:]:  # skip header
                tds = tr.find_all('td')
                if len(tds) < 1:
                    continue
                name = normalize_name(tds[0].find('a').text)
                if len(name) == 0:
                    continue
                data.append({
                    'name': name,
                })

    return sorted(data, key=lambda x: x['name'])


def normalize_name(name):
    # 衣装違いは除外
    if '新衣装' in name:
        return ''
    if '水着' in name:
        return ''

    return name

if __name__ == "__main__":
    characters = get_characters()

    with open('../../resources/master_data/characters.json', mode='wt', encoding='utf-8') as file:
        json.dump(characters, file, ensure_ascii=False, indent=2)
