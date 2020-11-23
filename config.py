#!/usr/bin/python3
"""
@ModuleName: config.py
@CreateTime: 2020/11/19 11:31
@Author: T.Zhang
@SoftWare: PyCharm
@Description: 配置文件
"""


# api
API_KEY = '2D68F296277144714848126A5B9727A1'
API_MATCH_HISTORY = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
API_MATCH_DETAILS = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1'
API_HEROES = 'http://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1?key=2D68F296277144714848126A5B9727A1&language=zh-cn '
API_ITEMS = 'http://api.steampowered.com/IEconDOTA2_570/GetGameItems/v1?key=2D68F296277144714848126A5B9727A1&language=zh-cn '

# 32位和64位steam id
BYISHIN_32BIT, BYISHIN_64BIT = 148400274, 76561198108666002
LEEROY_32BIT, LEEROY_64BIT = 312137887, 76561198272403615
NEKO_32BIT, NEKO_64BIT = 351692881, 76561198311958609
ORI_32BIT, ORI_64BIT = 283460742, 76561198243726470
ASIIMOV_32BIT, ASIIMOV_64BIT = 181052886, 181052886
SAKANA_32BIT, SAKANA_64BIT = 140996187, 76561198101261915
DIDIDI_32BIT, DIDIDI_64BIT = 120820654, 120820654
NEVEROWNED_32BIT, NEVEROWNED_64BIT = 145265444, 145265444
RABBIT_32BIT, RABBIT_64BIT = 145175090, 76561198105440818

# 日志配置
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s '
DATE_FORMAT = '%Y-%m-%d %H:%M:%S %a'
LOG_FILE = 'union.log'


def get_name(account_32bit):
    names = {
        148400274: '通老板',
        312137887: '老马',
        351692881: '金鱼女王',
        283460742: '萝卜',
        181052886: '小狗',
        140996187: '耀哥',
        120820654: '袁老板',
        145265444: '洪福',
        145175090: '兔子'
    }
    return names.get(account_32bit)


def get_level(deaths):
    level = {
        5: '测试境界',
        10: '初成',
        11: '小成',
        12: '大成',
        13: '小圆满',
        14: '圆满',
        15: '大圆满',
        16: '巅峰',
        17: '极致',
    }
    if deaths <= 17:
        return level.get(deaths)
    else:
        return '化境'
