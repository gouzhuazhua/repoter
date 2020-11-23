#!/usr/bin/python3
"""
@ModuleName: war_wolf.py
@CreateTime: 2020/11/18 15:33
@Author: T.Zhang
@SoftWare: PyCharm
@Description:
"""
import logging
import pywinauto.keyboard as kb
import sqlite3
import time
import traceback
from concurrent.futures.process import ProcessPoolExecutor
from functools import wraps
from json import loads
from multiprocessing import Queue, Manager

from apscheduler.schedulers.blocking import BlockingScheduler
from pywinauto import Application
from requests import get

from config import *


app = Application(backend='uia')
app.connect(path=r'D:\Program Files (x86)\Tencent\WeChat\WeChat.exe')


logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=LOG_FILE)


def time_logger():
    def logging_decorator(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            start_time = time.time()
            rs = func(*args, **kwargs)
            end_time = time.time()
            r_time = end_time - start_time
            logging.info("func [%s] take [%s] seconds" % (func.__name__, str(round(r_time, 2))))
            return rs
        return decorator
    return logging_decorator


class WarWolf:

    def __init__(self, account_id_64bit=None, account_id_32bit=None, queue=None):
        self.account_id_64bit = account_id_64bit
        self.account_id_32bit = account_id_32bit
        self.queue = queue
        self.match_id_record = None

        # db
        self.conn = None
        self.cursor = None

    def get_match(self):
        """
        获取最新的一场比赛
        Returns:

        """
        _url = API_MATCH_HISTORY + '?key=%s' % API_KEY + '&account_id=%s' % self.account_id_64bit + '&matches_requested=1'
        try:
            _matches = get(_url)
            matches_dict = loads(_matches.text)
            matches = matches_dict['result']['matches']
            if len(matches) > 0:
                return matches[0]['match_id']
            else:
                logging.warning('get null match')
                return None
        except:
            logging.error(traceback.format_exc())
            return None

    @staticmethod
    def get_match_details(match_id):
        """
        获取比赛详情
        Args:
            match_id:

        Returns:

        """
        try:
            _url = API_MATCH_DETAILS + '?key=%s' % API_KEY + '&match_id=%s' % match_id
            _details = get(_url)
            details_dict = loads(_details.text)
            return details_dict['result']
        except:
            logging.error(traceback.format_exc())
            return None

    def read_result(self, results):
        """
        解析比赛详情
        Args:
            results:

        Returns:

        """
        is_dire = False  # 队伍为夜魇标识
        players = results['players']  # 获取当前比赛所有玩家详情
        for player in players:  # 遍历每个玩家详情
            if player['account_id'] == self.account_id_32bit:  # 以玩家32位steamid确定该玩家是当前子进程玩家
                index = players.index(player)  # 记录该玩家在列表中的index
                # player_slot 为十进制，需要转换为8位二进制
                # 二进制中的最高位标识玩家阵营，1：夜魇/0：天辉
                player_slot_0b = '{:08b}'.format(player['player_slot'])  # 获取玩家详情信息中的player_slot
                if player_slot_0b[0] == '1':  # 如果最高位为1
                    is_dire = True  # 标识该玩家为夜魇阵营
                break

        player_slot_0b_start = '1' if is_dire else '0'  # 根据夜魇标识设置玩家player_slot最高位
        player_deaths = {}  # 玩家32位steamid和死亡数dict
        for player in players:  # 遍历每个玩家详情
            player_slot_0b = '{:08b}'.format(player['player_slot'])  # 获取玩家的player_slot
            if player_slot_0b[0] == player_slot_0b_start:  # 最高位相等，即该玩家与当前子进程玩家属于同一阵营
                player_deaths[player['account_id']] = player['deaths']  # 记录32位steamid和死亡数
        player_deaths = sorted(player_deaths.items(), key=lambda x: x[1], reverse=True)  # 根据死亡数排序，由高到低
        max_death_player_account_id_32bit = player_deaths[0][0]  # 取死亡数最高的玩家的32位steamid
        if max_death_player_account_id_32bit == self.account_id_32bit and player_deaths[0][1] >= 10:  # 满足死亡数最高的玩家为当前子进程玩家且死亡数超过十次
            player = players[index]  # 获取当前子进程玩家的比赛信息
            # 封装上报数据
            report_info = {'hero': self.get_hero_name_by_id(int(player['hero_id'])),
                           'level': player['level'],
                           'kills': player['kills'],
                           'deaths': player['deaths'],
                           'hero_damage': player['hero_damage'],
                           'start_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(results['start_time']))}
            self.report(report_info)  # 解析并推送到queue

    def report(self, report_info):
        """
        发送解析结果至队列（生产者）
        Args:
            report_info:

        Returns:

        """
        name = get_name(self.account_id_32bit)
        level = get_level(report_info['deaths'])
        msg = []
        msg_0 = '【战狼播报】'
        msg_1 = '恭喜【%s】达到【%s】境【%s】!' % (name, report_info['hero'], level)
        msg_2 = '【比赛时间】:%s ' % report_info['start_time']
        msg_3 = '【等级】:%s' % report_info['level']
        msg_4 = '【击杀】:%s' % report_info['kills']
        msg_5 = '【死亡】:%s' % report_info['deaths']
        msg_6 = '【伤害】:%s' % report_info['hero_damage']
        msg.append(msg_0)
        msg.append(msg_1)
        msg.append(msg_2)
        msg.append(msg_3)
        msg.append(msg_4)
        msg.append(msg_5)
        msg.append(msg_6)
        # print(msg)
        self.queue.put(msg)

    def get_hero_name_by_id(self, hero_id):
        """
        根据英雄id获取名称
        Args:
            hero_id:

        Returns:

        """
        self.connect_db()
        cursor = self.cursor.execute(
            'SELECT * FROM hero WHERE hero_id = ?', (hero_id, )
        ).fetchone()
        return cursor[2]

    def connect_db(self):
        """
        连接sqlite3
        Returns:

        """
        try:
            self.conn = sqlite3.connect('union.db')
            self.cursor = self.conn.cursor()
        except:
            print(traceback.format_exc())

    def close_db(self):
        """
        提交并关闭sqlite3
        Returns:

        """
        self.conn.commit()
        self.conn.close()

    @time_logger()
    def main(self):
        """
        进程入口
        Returns:

        """
        match_id = self.get_match()
        if self.match_id_record != match_id:  # 每5分钟获取到的match_id与内存中记录的match_id不一致
            logging.info('发现用户【%s】的新比赛：【%s】' % (get_name(self.account_id_32bit), match_id))
            results = self.get_match_details(match_id)
            self.read_result(results)
            self.match_id_record = match_id
        else:
            pass


def subprocess_event_producer(*args):
    """
    生产者子进程
    Args:
        *args: 64位id，32位id，队列

    Returns:

    """
    ww = WarWolf(args[0], args[1], args[2])  # 实例化战狼对象
    # APScheduler是一个 Python 定时任务框架。
    # 提供了基于日期、固定时间间隔以及 crontab 类型的任务，并且可以持久化任务、并以 daemon 方式运行应用。
    scheduler = BlockingScheduler()
    scheduler.add_job(ww.main, 'interval', seconds=300)  # 5分钟执行一次main方法
    scheduler.start()


def subprocess_event_consumer(queue):
    """
    消费者子进程，该方法尚未成功应用，需考虑其他方法推送至微信群
    Args:
        queue:

    Returns:

    """
    while 1:
        if not queue.empty():
            msg = queue.get()
            for m in msg:
                app['微信']['22194Edit'].type_keys(m)
                kb.send_keys('+{VK_RETURN}')
            kb.send_keys('{VK_RETURN}')
        time.sleep(5)


if __name__ == '__main__':
    q = Manager().Queue()  # 多进程队列
    executor = ProcessPoolExecutor(max_workers=10)  # 进程池
    # 九位玩家分别对应一个子进程
    task_1 = executor.submit(subprocess_event_producer, BYISHIN_64BIT, BYISHIN_32BIT, q)
    task_2 = executor.submit(subprocess_event_producer, LEEROY_64BIT, LEEROY_32BIT, q)
    task_3 = executor.submit(subprocess_event_producer, NEKO_64BIT, NEKO_32BIT, q)
    task_4 = executor.submit(subprocess_event_producer, ORI_64BIT, ORI_32BIT, q)
    task_5 = executor.submit(subprocess_event_producer, ASIIMOV_64BIT, ASIIMOV_32BIT, q)
    task_6 = executor.submit(subprocess_event_producer, SAKANA_64BIT, SAKANA_32BIT, q)
    task_7 = executor.submit(subprocess_event_producer, DIDIDI_64BIT, DIDIDI_32BIT, q)
    task_8 = executor.submit(subprocess_event_producer, NEVEROWNED_64BIT, NEVEROWNED_32BIT, q)
    task_9 = executor.submit(subprocess_event_producer, RABBIT_64BIT, RABBIT_32BIT, q)

    # 上报子进程
    task_10 = executor.submit(subprocess_event_consumer, q)
