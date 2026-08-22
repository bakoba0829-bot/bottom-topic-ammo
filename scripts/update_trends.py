import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone

RSS_URL = "https://trends.google.co.jp/trending/rss?geo=JP"
OUTPUT_FILE = "data/trends.json"

# 重すぎる・配信向きでないもの
BLOCK_WORDS = [
    "死亡", "死去", "殺人", "殺害", "逮捕", "容疑者",
    "死刑", "地震", "津波", "災害", "戦争", "爆発",
    "遺体", "選挙", "政党", "首相", "内閣"
]

# 単体では雑談ネタとして弱すぎる語
WEAK_TITLES = [
    "ニュース", "速報", "結果", "日程", "ライブ",
    "スコア", "順位", "スタメン", "スクイズ"
]

FOOD_WORDS = [
    "ラーメン", "カレー", "寿司", "焼肉", "マック",
    "マクドナルド", "スタバ", "コンビニ", "食品",
    "グルメ", "アイス", "お菓子", "ドリンク"
]

TECH_WORDS = [
    "iPhone", "Android", "スマホ", "Apple", "Google",
    "Switch", "ゲーム", "AI", "ChatGPT", "新型"
]

SCHOOL_WORDS = [
    "学校", "大学", "高校", "中学", "試験",
    "受験", "夏休み", "文化祭", "体育祭", "部活"
]

SEASON_WORDS = [
    "猛暑", "暑", "気温", "エアコン", "夏",
    "冬", "花火", "祭", "連休", "旅行"
]


def contains_any(text, words):
    lower = text.lower()
    return any(word.lower() in lower for word in words)


def is_blocked(title):
    if title in WEAK_TITLES:
        return True

    if len(title.strip()) <= 1:
        return True

    return contains_any(title, BLOCK_WORDS)


def scores(first=5, short=4, expand=5, long=4):
    return {
        "first": first,
        "short": short,
        "expand": expand,
        "long": long
    }


def make_raw_topic(title, number):
    return {
        "id": f"trend-{number}",
        "source": "Google Trends",
        "genre": "トレンド",
        "title": title,
        "opening": f"今『{title}』が検索で伸びてるみたい。これ知ってる？",
        "expansions": [
            "なんで今話題なんだろう？",
            "最近ネットで知ったものある？",
            "流行ってるものってチェックする派？"
        ],
        "related": [
            "SNS",
            "最近の流行",
            "ネット",
            "今日の出来事"
        ],
        "shortReason": "今話題になっているため、冒頭のフックとして使いやすい。",
        "splitPoint": "知っている人と知らない人で反応が分かれやすい。",
        "videoTitle": f"今話題の『{title}』知ってる？",
        "scores": scores(4, 3, 3, 3)
    }


def make_derived_topics(title, number):
    topics = []

    # 食べ物系
    if contains_any(title, FOOD_WORDS):

        topics.append({
            "id": f"derived-{number}-1",
            "source": "トレンド派生",
            "genre": "食べ物",
            "title": "最近食べて当たりだったものある？",
            "opening": "最近食べて『これうまかった！』ってもの何かある？",
            "expansions": [
                "コンビニでリピートしてるものある？",
                "流行ってる食べ物は試す派？",
                "食べ物ならいくらまで出せる？"
            ],
            "related": [
                "コンビニ",
                "外食",
                "新商品",
                "好き嫌い"
            ],
            "trendOrigin": title,
            "shortReason": "誰でも食経験をコメントでき、商品名も自然に出やすい。",
            "splitPoint": "流行を試す派と定番派で意見が分かれる。",
            "videoTitle": "最近食べて本当にうまかったもの教えて",
            "scores": scores(5, 4, 5, 5)
        })

        topics.append({
            "id": f"derived-{number}-2",
            "source": "トレンド派生",
            "genre": "価値観",
            "title": "流行ってる食べ物、すぐ試す？",
            "opening": "SNSでバズってる食べ物って、すぐ買ってみる？",
            "expansions": [
                "行列でも並ぶ？",
                "口コミって信じる？",
                "結局ずっと食べてる定番ある？"
            ],
            "related": [
                "SNS",
                "行列",
                "口コミ",
                "買い物"
            ],
            "trendOrigin": title,
            "shortReason": "流行に乗るかどうかで意見が割れやすい。",
            "splitPoint": "流行を追う派 / 自分の好み優先派。",
            "videoTitle": "バズってる食べ物、すぐ試す派？",
            "scores": scores(5, 5, 5, 4)
        })

        return topics

    # スマホ・新商品・ゲームなど
    if contains_any(title, TECH_WORDS):

        topics.append({
            "id": f"derived-{number}-1",
            "source": "トレンド派生",
            "genre": "日常",
            "title": "スマホって何年で買い替える？",
            "opening": "みんなスマホって何年くらい使ったら買い替える？",
            "expansions": [
                "壊れるまで使う？",
                "新型が出たら欲しくなる？",
                "今までで一番長く使ったスマホ何年？"
            ],
            "related": [
                "スマホ",
                "買い物",
                "新商品",
                "お金"
            ],
            "trendOrigin": title,
            "shortReason": "ほぼ全員が経験を持っていて、一言でも答えられる。",
            "splitPoint": "壊れるまで使う派 / 新型へ買い替える派。",
            "videoTitle": "スマホ何年使ったら買い替える？",
            "scores": scores(5, 5, 5, 5)
        })

        topics.append({
            "id": f"derived-{number}-2",
            "source": "トレンド派生",
            "genre": "価値観",
            "title": "スマホに10万円以上出せる？",
            "opening": "スマホに10万円以上って普通に出せる？高い？",
            "expansions": [
                "一番高かった買い物って何？",
                "分割払いなら気にならない？",
                "性能と値段どっち優先？"
            ],
            "related": [
                "お金",
                "買い物",
                "節約",
                "価値観"
            ],
            "trendOrigin": title,
            "shortReason": "金額を提示するだけで立場が分かれ、短尺動画にしやすい。",
            "splitPoint": "毎日使うなら安い派 / スマホに10万円は高い派。",
            "videoTitle": "スマホに10万円以上、出せる？",
            "scores": scores(5, 5, 5, 4)
        })

        return topics

    # 学校系
    if contains_any(title, SCHOOL_WORDS):

        topics.append({
            "id": f"derived-{number}-1",
            "source": "トレンド派生",
            "genre": "仕事・学校",
            "title": "学生時代に戻るなら何歳？",
            "opening": "学生時代に1回だけ戻れるなら何歳に戻る？",
            "expansions": [
                "小中高ならどこが一番楽しかった？",
                "戻ったらやり直したいことある？",
                "今だから分かる学校生活の良さある？"
            ],
            "related": [
                "学生時代",
                "青春",
                "学校",
                "友達"
            ],
            "trendOrigin": title,
            "shortReason": "経験談が出やすく、年代を問わず参加しやすい。",
            "splitPoint": "戻りたい派 / 絶対戻りたくない派。",
            "videoTitle": "学生時代、戻るなら何歳？",
            "scores": scores(5, 5, 5, 5)
        })

        topics.append({
            "id": f"derived-{number}-2",
            "source": "トレンド派生",
            "genre": "仕事・学校",
            "title": "学校で一番好きだった行事は？",
            "opening": "体育祭・文化祭・修学旅行なら何が一番好きだった？",
            "expansions": [
                "逆に一番嫌だった行事は？",
                "行事ガチ勢だった？",
                "学生の頃の思い出で一番覚えてるの何？"
            ],
            "related": [
                "文化祭",
                "体育祭",
                "修学旅行",
                "学生時代"
            ],
            "trendOrigin": title,
            "shortReason": "一言回答から思い出話へ自然に広げられる。",
            "splitPoint": "行事好き / 行事めんどくさい派。",
            "videoTitle": "学校行事、一番好きだったの何？",
            "scores": scores(5, 4, 5, 5)
        })

        return topics

    # 季節・天候
    if contains_any(title, SEASON_WORDS):

        topics.append({
            "id": f"derived-{number}-1",
            "source": "トレンド派生",
            "genre": "季節",
            "title": "夏と冬、どっちが嫌？",
            "opening": "夏と冬なら、どっちの方が嫌？",
            "expansions": [
                "暑いのと寒いのどっちが耐えられる？",
                "一番好きな季節は？",
                "夏に絶対やることある？"
            ],
            "related": [
                "夏",
                "冬",
                "季節",
                "休日"
            ],
            "trendOrigin": title,
            "shortReason": "誰でも答えられ、真逆の意見が生まれやすい。",
            "splitPoint": "夏派 / 冬派。",
            "videoTitle": "夏と冬、どっちがマシ？",
            "scores": scores(5, 5, 5, 4)
        })

        topics.append({
            "id": f"derived-{number}-2",
            "source": "トレンド派生",
            "genre": "日常",
            "title": "寝る時エアコン何度？",
            "opening": "みんな寝る時エアコン何度にしてる？",
            "expansions": [
                "朝までつけっぱなし？",
                "タイマー使う？",
                "電気代って気にする？"
            ],
            "related": [
                "睡眠",
                "電気代",
                "夏",
                "生活"
            ],
            "trendOrigin": title,
            "shortReason": "数字で回答でき、生活習慣の違いがコメントになりやすい。",
            "splitPoint": "つけっぱなし派 / タイマー派。",
            "videoTitle": "寝る時のエアコン、何度が正解？",
            "scores": scores(5, 5, 5, 4)
        })

        return topics

    # その他のトレンドから作る万能派生
    topics.append({
        "id": f"derived-{number}-1",
        "source": "トレンド派生",
        "genre": "価値観",
        "title": "流行ってるものって気になる？",
        "opening": "みんな『今これ流行ってる』って聞いたら気になっちゃう？",
        "expansions": [
            "流行ってるから始めたものある？",
            "逆に流行ってても興味ないものある？",
            "SNSで流行を知ること多い？"
        ],
        "related": [
            "SNS",
            "流行",
            "趣味",
            "ネット"
        ],
        "trendOrigin": title,
        "shortReason": "流行への向き合い方という普遍的な価値観へ変換している。",
        "splitPoint": "流行に乗る派 / マイペース派。",
        "videoTitle": "流行ってると気になっちゃう？",
        "scores": scores(5, 5, 5, 4)
    })

    return topics


def main():

    request = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "ja-JP,ja;q=0.9"
        }
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    titles = []

    for item in root.findall(".//item"):

        title_element = item.find("title")

        if title_element is None:
            continue

        if not title_element.text:
            continue

        title = title_element.text.strip()

        if is_blocked(title):
            continue

        if title in titles:
            continue

        titles.append(title)

    # 元トレンドは最大8件
    titles = titles[:8]

    topics = []

    for number, title in enumerate(titles, start=1):

        # 元トレンド
        topics.append(
            make_raw_topic(title, number)
        )

        # そこから配信用テーマを作る
        derived = make_derived_topics(
            title,
            number
        )

        topics.extend(derived)

    data = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "topics": topics
    }

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"{len(titles)}件のトレンドから"
        f"{len(topics)}件の話題を作成しました"
    )


if __name__ == "__main__":
    main()
