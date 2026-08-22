import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone

RSS_URL = "https://trends.google.co.jp/trending/rss?geo=JP"
OUTPUT_FILE = "data/trends.json"

BLOCK_WORDS = [
    "死亡",
    "死去",
    "殺人",
    "殺害",
    "逮捕",
    "容疑者",
    "死刑",
    "事故",
    "地震",
    "津波",
    "台風被害",
    "災害",
    "戦争",
    "爆発",
    "遺体",
    "選挙",
    "政党",
    "首相",
    "内閣",
]

def is_blocked(text):
    return any(word in text for word in BLOCK_WORDS)

def make_topic(title):
    if any(word in title for word in ["新型", "発売", "新商品", "新作"]):
        return {
            "opening": f"『{title}』が今話題みたい。新しい物ってすぐ試す派？",
            "expansions": [
                "新商品ってすぐ買う？",
                "最近買ってよかった物ある？",
                "何円くらいから買うか悩む？"
            ],
            "related": ["買い物", "新商品", "お金", "趣味"],
            "genre": "日常"
        }

    if any(word in title for word in [
        "ラーメン", "カレー", "寿司", "焼肉", "マック",
        "マクドナルド", "スタバ", "コンビニ", "食品", "グルメ"
    ]):
        return {
            "opening": f"『{title}』が話題らしいけど、みんなこれ好き？",
            "expansions": [
                "最後に食べたのいつ？",
                "似た系統なら何が一番好き？",
                "外食でつい頼んじゃう物ある？"
            ],
            "related": ["食べ物", "外食", "コンビニ", "好き嫌い"],
            "genre": "食べ物"
        }

    if any(word in title for word in [
        "学校", "大学", "高校", "中学", "試験", "受験",
        "夏休み", "冬休み", "文化祭", "体育祭"
    ]):
        return {
            "opening": f"『{title}』が話題だけど、みんな学生時代どうだった？",
            "expansions": [
                "学生時代に戻りたい？",
                "学校行事で一番好きだったの何？",
                "今思うと変だった校則ある？"
            ],
            "related": ["学生時代", "学校", "先生", "部活"],
            "genre": "仕事・学校"
        }

    return {
        "opening": f"今『{title}』が検索で急上昇してるみたい。みんなこれ知ってる？",
        "expansions": [
            "これ初めて聞いた？",
            "なんで今話題なんだろう？",
            "流行ってるものってチェックする派？",
            "最近ネットで知ったものある？"
        ],
        "related": ["SNS", "流行", "ネット", "日常"],
        "genre": "今日の話題"
    }

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

    trends = []

    for item in root.findall(".//item"):
        title_element = item.find("title")

        if title_element is None or not title_element.text:
            continue

        title = title_element.text.strip()

        if is_blocked(title):
            continue

        topic = make_topic(title)

        trends.append({
            "id": f"trend-{len(trends) + 1}",
            "source": "Google Trends",
            "trend_title": title,
            "title": title,
            "genre": topic["genre"],
            "opening": topic["opening"],
            "expansions": topic["expansions"],
            "related": topic["related"],
            "scores": {
                "first": 4,
                "short": 4,
                "expand": 4,
                "long": 3
            }
        })

        if len(trends) >= 15:
            break

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "topics": trends
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{len(trends)} 件のトレンドを保存しました")
    print(f"保存先: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
