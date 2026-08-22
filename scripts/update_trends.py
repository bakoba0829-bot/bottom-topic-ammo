import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
from datetime import datetime, timezone

RSS_URL = "https://trends.google.co.jp/trending/rss?geo=JP"
OUTPUT_FILE = "data/trends.json"

# 配信で扱いづらい話題をある程度除外
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
    """
    トレンド語を、そのままニュース見出しとして出すのではなく
    雑談の入口として使いやすい形にする。
    完全無料版なのでAIではなくルールベース。
    """

    # 車・新商品っぽいワード
    if any(word in title for word in ["新型", "発売", "新商品", "新作"]):
        return {
            "opening": f"『{title}』が今話題みたい。新しい物ってすぐ試す派？",
            "expansions": [
                "新商品ってすぐ買う？",
                "最近買ってよかった物ある？",
                "何円くらいから買うか悩む？",
            ],
            "related": ["買い物", "新商品", "お金", "趣味"],
            "genre": "日常",
        }

    # 食べ物系
    if any(word in title for word in [
        "ラーメン", "カレー", "寿司", "焼肉", "マック",
        "マクドナルド", "スタバ", "コンビニ", "食品", "グルメ"
    ]):
        return {
            "opening": f"『{title}』が話題らしいけど、みんなこれ好き？",
            "expansions": [
                "最後に食べたのいつ？",
                "似た系統なら何が一番好き？",
                "外食でつい頼んじゃう物ある？",
            ],
            "related": ["食べ物", "外食", "コンビニ", "好き嫌い"],
            "genre": "食べ物",
        }

    # 学校・試験系
    if any(word in title for word in [
        "学校", "大学", "高校", "中学", "試験", "受験",
        "夏休み", "冬休み", "文化祭", "体育祭"
    ]):
        return {
            "opening": f"『{title}』が話題だけど、みんな学生時代どうだった？",
            "expansions": [
                "学生時代に戻りたい？",
                "学校行事で一番好きだったの何？",
                "今思うと変だった校則ある？",
            ],
            "related": ["学生時代", "学校", "先生", "部活"],
            "genre": "仕事・学校",
        }

    # 芸能・人物名っぽいもの
    if re.fullmatch(r"[ぁ-んァ-ヶ一-龠
