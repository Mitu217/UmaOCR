import json
import math
import os
import re

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# 【ウマ娘】全キャラの育成論と難易度一覧 - ゲームウィズ(GameWith)
url_game_with_characters = 'https://gamewith.jp/uma-musume/article/show/253241'
# テーブル/育成ウマ娘詳細一覧 - ウマ娘wiki
url_uma_wiki_characters = 'https://umamusume.wikiru.jp/index.php?cmd=read&page=%A5%C6%A1%BC%A5%D6%A5%EB%2F%B0%E9%C0%AE%A5%A6%A5%DE%CC%BC%BE%DC%BA%D9%B0%EC%CD%F7'

response_game_with_characters = requests.get(url_game_with_characters)
soup_game_with_characters = BeautifulSoup(response_game_with_characters.text, "html.parser")

response_uma_wiki_characters = requests.get(url_uma_wiki_characters)
soup_uma_wiki_characters = BeautifulSoup(response_uma_wiki_characters.text, "html.parser")


def get_characters():
    soup = soup_uma_wiki_characters
    data = []

    for table in soup.select('table.style_table'):
        for tr in table.find_all('tr')[1:]:  # skip header
            tds = tr.find_all('td')
            if len(tds) < 1:
                continue
            text = normalize_name(tds[0].find('a').text)
            if len(text) == 0:
                continue

            nicknames = re.findall("(?<=［).+?(?=］)", text)
            if len(nicknames) == 0:
                continue
            nickname = normalize_nickname(nicknames[0])
            name = normalize_name(re.sub("［.+?］", "", text))

            found = False
            for character in data:
                if character['name'] == name:
                    found = True
                    character['nickname'].append(nickname)
                    break
            if not found:
                data.append({
                    'name': name,
                    'nickname': [nickname],
                })

    return sorted(data, key=lambda x: x['name'])


def normalize_name(name):
    # 衣装違いは除外
    if '新衣装' in name:
        return ''
    if '水着' in name:
        return ''

    return name

def normalize_nickname(nickname):
    if 'エル☆Numero 1' == nickname:
        return 'エル☆Número 1'
    if 'オーセンティック／1928' == nickname:
        return 'オーセンティック/1928'
    if 'ブルー／レイジング' == nickname:
        return 'ブルー/レイジング'

    return nickname

if __name__ == "__main__":
    characters = get_characters()

    with open('../../resources/master_data/characters.json', mode='wt', encoding='utf-8') as file:
        json.dump(characters, file, ensure_ascii=False, indent=2)
