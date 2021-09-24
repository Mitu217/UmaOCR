import json
import math
import os

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# 【ウマ娘】固有スキルの効果一覧 - ゲームウィズ(GameWith)
url_game_with_unique_skills = 'https://gamewith.jp/uma-musume/article/show/267935'
# 【ウマ娘】レアスキルの効果一覧 - ゲームウィズ(GameWith)
url_game_with_rare_skills = 'https://gamewith.jp/uma-musume/article/show/267934'
# 【ウマ娘】ノーマルスキルの効果一覧 - ゲームウィズ(GameWith)
url_game_with_normal_skills = 'https://gamewith.jp/uma-musume/article/show/267933'

response_game_with_unique_skills = requests.get(url_game_with_unique_skills)
soup_game_with_unique_skills = BeautifulSoup(response_game_with_unique_skills.text, "html.parser")

response_game_with_rare_skills = requests.get(url_game_with_rare_skills)
soup_game_with_rare_skills = BeautifulSoup(response_game_with_rare_skills.text, "html.parser")

response_game_with_normal_skills = requests.get(url_game_with_normal_skills)
soup_game_with_normal_skills = BeautifulSoup(response_game_with_normal_skills.text, "html.parser")


def get_normal_skills():
    soup = soup_game_with_normal_skills
    data = []

    for table in soup.select('table.sort_element_filter'):
        for tr in table.find_all('tr')[1:]:  # skip header
            tds = tr.find_all('td')
            name = normalize_name(tds[0].find('a').text)

            data.append({
                'type': 'normal',
                'name': name,
                'weight': calc_text_weight(name),
                'desc': '',
                'similar': {
                    'name': get_similar_skill_names(name),
                    'weight': get_similar_skill_weights(name),
                }
            })

    return sorted(data, key=lambda x: x['name'])


def get_rare_skills():
    soup = soup_game_with_rare_skills
    data = []

    for table in soup.select('div.w-instant-database-list table'):
        for tr in table.find_all('tr')[0:]:  # skip header
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            name = normalize_name(tds[0].find('a').text)

            data.append({
                'type': 'rare',
                'name': name,
                'weight': calc_text_weight(name),
                'desc': '',
                'similar': {
                    'name': get_similar_skill_names(name),
                    'weight': get_similar_skill_weights(name),
                }
            })

    return sorted(data, key=lambda x: x['name'])


def get_unique_skills():
    soup = soup_game_with_unique_skills
    data = []

    for table in soup.select('table.sort_element_filter'):
        for tr in table.find_all('tr')[1:]:  # skip header
            tds = tr.find_all('td')
            name = normalize_name(tds[0].find('a').text)
            desc = tds[1].contents[0]

            data.append({
                'type': 'unique',
                'name': name,
                'weight': calc_text_weight(name),
                'desc': '',
                'similar': {
                    'name': get_similar_skill_names(name),
                    'weight': get_similar_skill_weights(name),
                }
            })

    return sorted(data, key=lambda x: x['name'])


def gen_text_image(skill_name):
    font_file = os.path.join('../../resources/fonts/WanpakuRuika-07M.TTF')
    font_size = 24
    font = ImageFont.truetype(font=font_file, size=font_size)

    background_color = (0, 0, 0)
    font_color = (255, 255, 255)
    position = (0, 0)
    image_size = (512, 512)

    im = Image.new(mode='RGB', size=image_size, color=background_color)
    draw = ImageDraw.Draw(im)
    draw.text(xy=position, text=skill_name, font=font, fill=font_color)
    bbox = im.getbbox()
    cropped = im.crop(box=bbox)

    return cropped


def calc_text_weight(text):
    # 英字/記号を含んでいると計算が難しいので例外は別途対応
    if text == '紅焔ギア/LP1211-M':
        return 10

    word_width = 25.3
    text_image = gen_text_image(text)
    return math.ceil(text_image.size[0] / word_width)


def normalize_name(name):
    # 誤表記をコネコネ
    if name == 'LookatCurren':
        name = '#LookatCurren'
    if name == 'G00 1stF∞':
        name = 'G00 1st.F∞;'
    if name == '優等生×バクシン=大勝利ッ':
        name = '優等生✕バクシン＝大勝利ッ'
    if name == 'win Q.E.D':
        name = '∴win Q.E.D.'

    return name


def get_similar_skill_names(skill_name):
    # ocr結果として誤検知されやすい文字列を調整
    similar_names = []

    if '◯' in skill_name:
        similar_names.append(skill_name.replace('◯', ''))

    if '逃げ' in skill_name:
        similar_names.append(skill_name.replace('逃げ', '透け'))
        similar_names.append(skill_name.replace('逃げ', '逃け'))
    if '努力' in skill_name:
        similar_names.append(skill_name.replace('努力', '胡力'))
        similar_names.append(skill_name.replace('努力', '即力'))
        similar_names.append(skill_name.replace('努力', '勢力'))
        similar_names.append(skill_name.replace('努力', '准力'))
        similar_names.append(skill_name.replace('努力', '明力'))
    if '短距離' in skill_name:
        similar_names.append(skill_name.replace('短距離', '細距離'))
        similar_names.append(skill_name.replace('短距離', '紅距離'))
    if '深呼吸' in skill_name:
        similar_names.append(skill_name.replace('深呼吸', '漂陸明'))
        similar_names.append(skill_name.replace('深呼吸', '漂峡明'))
    if '巧者' in skill_name:
        similar_names.append(skill_name.replace('巧者', '巧書'))
        similar_names.append(skill_name.replace('巧者', '世暫'))
    if '一匹狼' in skill_name:
        similar_names.append(skill_name.replace('一匹狼', '一忠独'))
    if 'の風' in skill_name:
        similar_names.append(skill_name.replace('の風', 'の如'))
        similar_names.append(skill_name.replace('の風', 'の鳳'))
    if '一陣' in skill_name:
        similar_names.append(skill_name.replace('一陣', 'ー障'))
    if '豪脚' in skill_name:
        similar_names.append(skill_name.replace('豪脚', '各肢'))
        similar_names.append(skill_name.replace('豪脚', '入陸'))
        similar_names.append(skill_name.replace('豪脚', '京脚'))
    if '末脚' in skill_name:
        similar_names.append(skill_name.replace('末', '未'))
        similar_names.append(skill_name.replace('脚', '肢'))
        similar_names.append(skill_name.replace('脚', '膨'))
    if '積極' in skill_name:
        similar_names.append(skill_name.replace('積極', '策福'))
        similar_names.append(skill_name.replace('積極', '柄租'))
    if '左回り' in skill_name:
        similar_names.append(skill_name.replace('左回り', 'を回り'))
    if '根幹' in skill_name:
        similar_names.append(skill_name.replace('根幹', '相見'))
        similar_names.append(skill_name.replace('根幹', '穫本'))
    if '燃焼' in skill_name:
        similar_names.append(skill_name.replace('燃焼', '移退'))
        similar_names.append(skill_name.replace('燃焼', '燈壇'))
        similar_names.append(skill_name.replace('燃焼', '姫矯'))
        similar_names.append(skill_name.replace('燃焼', '媛妨'))
        if '・速' in skill_name:
            similar_names.append(skill_name.replace('燃焼・速', '移退・通'))
            similar_names.append(skill_name.replace('燃焼・速', '燈壇・通'))
            similar_names.append(skill_name.replace('燃焼・速', '姫矯・通'))
            similar_names.append(skill_name.replace('燃焼・速', '媛妨・通'))
            similar_names.append(skill_name.replace('燃焼・速', '移退・問'))
            similar_names.append(skill_name.replace('燃焼・速', '燈壇・問'))
            similar_names.append(skill_name.replace('燃焼・速', '姫矯・問'))
            similar_names.append(skill_name.replace('燃焼・速', '媛妨・問'))
            similar_names.append(skill_name.replace('燃焼・速', '移退・加'))
            similar_names.append(skill_name.replace('燃焼・速', '燈壇・加'))
            similar_names.append(skill_name.replace('燃焼・速', '姫矯・加'))
            similar_names.append(skill_name.replace('燃焼・速', '媛妨・加'))
            similar_names.append(skill_name.replace('燃焼・速', '移退・連'))
            similar_names.append(skill_name.replace('燃焼・速', '燈壇・連'))
            similar_names.append(skill_name.replace('燃焼・速', '姫矯・連'))
            similar_names.append(skill_name.replace('燃焼・速', '媛妨・連'))
            similar_names.append(skill_name.replace('燃焼・速', '移退・適'))
            similar_names.append(skill_name.replace('燃焼・速', '燈壇・適'))
            similar_names.append(skill_name.replace('燃焼・速', '姫矯・適'))
            similar_names.append(skill_name.replace('燃焼・速', '媛妨・適'))
    if '秋ウマ娘◯' in skill_name:
        similar_names.append(skill_name.replace('秋ウマ娘◯', '入ウマ娘◯'))
        similar_names.append(skill_name.replace('秋ウマ娘◯', '入ウマ娘'))
        similar_names.append(skill_name.replace('秋ウマ娘◯', '邊ウマ娘◯'))
        similar_names.append(skill_name.replace('秋ウマ娘◯', '邊ウマ娘'))
        similar_names.append(skill_name.replace('秋ウマ娘◯', '其ウマ娘◯'))
        similar_names.append(skill_name.replace('秋ウマ娘◯', '其ウマ娘'))
    if '・速' in skill_name:
        similar_names.append(skill_name.replace('・速', '・通'))
        similar_names.append(skill_name.replace('・速', '・問'))
        similar_names.append(skill_name.replace('・速', '・加'))
        similar_names.append(skill_name.replace('・速', '・連'))
        similar_names.append(skill_name.replace('・速', '・適'))
    if '東京' in skill_name:
        similar_names.append(skill_name.replace('東京', '昌京'))
    if '逃亡' in skill_name:
        similar_names.append(skill_name.replace('逃亡', '大亡'))

    return similar_names

def get_similar_skill_weights(skill_name):
    # ocr結果として誤検知されやすい文字列を調整
    similar_weights = []

    if '◯' in skill_name:
        similar_weights.append(len(skill_name.replace('◯', '')))

    # 記号で文字数ブレが激しいケースを吸収
    if '先頭の景色は譲らない…！' == skill_name:
        similar_weights.append(11)
    if 'ブリリアント・レッドエース' == skill_name:
        similar_weights.append(12)
    if 'アングリング×スキーミング' == skill_name:
        similar_weights.append(12)
    if '優等生✕バクシン＝大勝利ッ' == skill_name:
        similar_weights.append(12)
    if '学級委員長＋速さ＝バクシン' == skill_name:
        similar_weights.append(12)
    if 'G00 1st.F∞;' == skill_name:
        similar_weights.append(6)
    if 'ヴィクトリーショット！' == skill_name:
        similar_weights.append(10)

    return similar_weights

if __name__ == "__main__":
    skills = dict()

    skills['normal_skills'] = get_normal_skills()
    skills['rare_skills'] = get_rare_skills()
    skills['unique_skills'] = get_unique_skills()

    with open('../../resources/master_data/skills.json', mode='wt', encoding='utf-8') as file:
        json.dump(skills, file, ensure_ascii=False, indent=2)
