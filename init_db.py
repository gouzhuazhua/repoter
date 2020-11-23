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


def init_db():
    create_table()
    init_hero_table()
    init_item_table()


if __name__ == '__main__':
    init_db()