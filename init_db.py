#!/usr/bin/python3
"""
@ModuleName: war_wolf.py
@CreateTime: 2020/11/19 11:10
@Author: T.Zhang
@SoftWare: PyCharm
@Description:
"""
import logging
import os
import sqlite3
from json import loads

from requests import get

LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s '
DATE_FORMAT = '%Y-%m-%d %H:%M:%S %a'
LOG_FILE = os.getcwd() + os.sep + 'union.log'
logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=LOG_FILE)


def create_table():
    conn = sqlite3.connect('union.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE hero
                   (id          INTEGER      PRIMARY KEY  AUTOINCREMENT,
                    hero_id     INT      NOT NULL,
                    hero_name   TEXT     NOT NULL);''')

    cursor.execute('''CREATE TABLE item
                   (id          INTEGER      PRIMARY KEY  AUTOINCREMENT,
                    item_id     INT      NOT NULL,
                    item_name   TEXT     NOT NULL);''')

    cursor.execute('''CREATE TABLE achievements
                   (id            INTEGER      PRIMARY KEY  AUTOINCREMENT,
                    name          TEXT      NOT NULL,
                    target        TEXT      NOT NULL,
                    description   TEXT     NOT NULL);''')

    cursor.execute('''CREATE TABLE player_achievements
                    (id          INTEGER      PRIMARY KEY  AUTOINCREMENT,
                    match_id     TEXT         NOT NULL,
                    account_id   TEXT         NOT NULL,
                    ach_id       TEXT         NOT NULL,
                    create_time  TIMESTAMP default (datetime('now', 'localtime')))''')

    conn.commit()
    logging.info("Table created successfully")
    conn.close()


def init_hero_table():
    _url = 'http://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1?key=2D68F296277144714848126A5B9727A1&language=zh-cn'
    _heroes = get(_url)
    heroes_dict = loads(_heroes.text)
    heroes = heroes_dict['result']['heroes']
    conn = sqlite3.connect('union.db')
    cursor = conn.cursor()
    for hero in heroes:
        hero_id = hero['id']
        hero_name = hero['localized_name']
        cursor.execute(
            'INSERT INTO hero (hero_id, hero_name) VALUES (?, ?)', (hero_id, hero_name)
        )
    conn.commit()
    logging.info('init hero table succeed')
    conn.close()


def init_item_table():
    _url = 'http://api.steampowered.com/IEconDOTA2_570/GetGameItems/v1?key=2D68F296277144714848126A5B9727A1&language=zh-cn'
    _items = get(_url)
    items_dict = loads(_items.text)
    items = items_dict['result']['items']
    conn = sqlite3.connect('union.db')
    cursor = conn.cursor()
    for item in items:
        item_id = item['id']
        item_name = item['localized_name']
        cursor.execute(
            'INSERT INTO item (item_id, item_name) VALUES (?, ?)', (item_id, item_name)
        )
    conn.commit()
    logging.info('init item table succeed')
    conn.close()


def init_achievements():
    conn = sqlite3.connect('union.db')
    cursor = conn.cursor()
    achievements = [{'name': '点到为止', 'target': '0杀', 'description': '轻轻触及战斗的边缘，不必深入，已经让对方明了意图。'},
                    {'name': '修罗', 'target': '20杀', 'description': '六道之一，独立的修罗道，是由人或神转世而成，凶猛好斗的鬼神。'},
                    {'name': '借刀', 'target': '平均击杀伤害低于2000', 'description': '让别人卖命，在关键之时出手，这所谓借刀。'},
                    {'name': '割草', 'target': '800正补', 'description': '众生如草'},
                    {'name': '背刺', 'target': '80反补', 'description': '正面英勇战斗，但却死于毫无防备的一击'},
                    {'name': '浑水', 'target': '经济输出比低于0.6', 'description': '混浊的水中，鱼晕头转向，乘机摸鱼，可以得到意外的好处。'},
                    {'name': '志愿', 'target': '经济输出比高于1.5', 'description': '无私的社区志愿者'}]
    for ach in achievements:
        cursor.execute(
            'INSERT INTO achievements(name, target, description) VALUES (?, ?, ?)', (ach['name'], ach['target'], ach['description'])
        )
    conn.commit()
    logging.info('init achievements table succeed')
    conn.close()


def init_db():
    create_table()
    init_hero_table()
    init_item_table()
    init_achievements()


if __name__ == '__main__':
    init_db()