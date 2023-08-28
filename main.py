import requests
import json
import os
import sys
import re
from loguru import logger


env_config_name = "ys_config"
env_config = os.environ.get(env_config_name)
if not env_config:
    logger.error(f"没有检测到名为 {env_config_name} 的环境变量，请新建名为 {env_config_name} 的环境变量")
    sys.exit(1)
raw_config = json.loads(env_config)


def start_sign(config):
    token = config.get('x-rpc-combo_token')
    client_type = config.get('x-rpc-client_type') or 2
    try:
        ver_info = requests.get('https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource?key=eYd89JmJ&launcher_id=18', timeout=60).text
        version = json.loads(ver_info)['data']['game']['latest']['version']
        logger.info(f'从官方API获取到云·原神最新版本号：{version}')
    except:
        logger.warning('无法从官方 API获取版本号信息!')
        version = config.get('version') or config.get('x-rpc-app_version')
        if not version:
            logger.error("获取失败！程序无法运行")
            sys.exit(1)
    android = config.get('x-rpc-sys_version') or "13"
    deviceid = config.get('x-rpc-device_id')
    devicename = config.get('x-rpc-device_name') or "Xiaomi 2304FPN6DG"
    devicemodel = config.get('x-rpc-device_model') or "2304FPN6DG"
    appid = config.get('x-rpc-app_id') or "1953439974"
    bbsid = token.split('oi=')[1].split(';')[0]

    NotificationURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup&is_sort=true'
    WalletURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/wallet/wallet/get'
    AnnouncementURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/getAnnouncementInfo'
    headers = {
        'x-rpc-combo_token': token,
        'x-rpc-client_type': str(client_type),
        'x-rpc-app_version': str(version),
        'x-rpc-sys_version': str(android), 
        'x-rpc-channel': 'mihoyo',
        'x-rpc-device_id': deviceid,
        'x-rpc-device_name': devicename,
        'x-rpc-device_model': devicemodel,
        'x-rpc-app_id': str(appid),
        'x-rpc-vendor_id': "1",
        'x-rpc-cg_game_biz': "hk4e_cn",
        'x-rpc-op_biz': "clgm_cn",
        'x-rpc-language': "zh-cn",
        'Referer': 'https://app.mihoyo.com',
        'Host': 'api-cloudgame.mihoyo.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.10.0'
    }
    for k, v in headers.items():
        headers[k] = str(v)
    if config == '':
        logger.error(
            f"请在环境变量页面中新建名为config的环境变量，并将你的配置填入后再运行！")
        sys.exit(1)
    else:
        if token == '' or android == 0 or deviceid == '' or devicemodel == '' or appid == 0:
            logger.error(f'请确认您的配置文件配置正确再运行本程序！')
            sys.exit(1)
    wallet = requests.get(WalletURL, headers=headers, timeout=60)
    if json.loads(wallet.text) == {"data": None,"message":"登录已失效，请重新登录","retcode":-100}: 
        logger.error(f'当前登录已过期，请重新登陆！返回为：{wallet.text}')
        sys.exit(1)
    else:
        f_time = divmod(int(json.loads(wallet.text)['data']['free_time']['free_time']), 60)
        logger.info(
            f"ID: {bbsid} ,免费时长 {f_time[0]} 小时 {f_time[1]} 分钟,畅玩卡： {json.loads(wallet.text)['data']['play_card']['short_msg']},米云币： {json.loads(wallet.text)['data']['coin']['coin_num']} 枚")
        announcement = requests.get(AnnouncementURL, headers=headers, timeout=60)
        logger.info(f'获取到公告列表：{json.loads(announcement.text)["data"]}')
        res = requests.get(NotificationURL, headers=headers, timeout=60)
        success,Signed = False,False
        try:
            if list(json.loads(res.text)['data']['list']) == []:
                success = True
                Signed = True
                Over = False
            elif json.loads(json.loads(res.text)['data']['list'][0]['msg']) == {"num": 15, "over_num": 0, "type": 2, "msg": "每日登录奖励", "func_type": 1}:
                success = True
                Signed = False
                Over = False
            elif json.loads(json.loads(res.text)['data']['list'][0]['msg'])['over_num'] > 0:
                success = True
                Signed = False
                Over = True
            else:
                success = False
        except IndexError:
            success = False
        if success:
            if Signed:
                logger.warning("今天似乎已经签到过了")
                # logger.info(f'完整返回体为：{res.text}')
            elif not Signed and Over:
                logger.warning("当前免费时长已经达到上限！")
                # logger.info(f'完整返回体为：{res.text}')
            else:
                logger.success('签到成功')
                # logger.info(f'完整返回体为：{res.text}')
        else:
            logger.error(
                f"签到失败！请带着本次运行的所有log内容到 https://github.com/ElainaMoe/MHYY-AutoCheckin/issues 发起issue解决（或者自行解决）。签到出错，返回信息如下：{res.text}")
if __name__ == '__main__':
    if isinstance(raw_config, list):
        for c in raw_config:
            start_sign(c)
    elif isinstance(raw_config, dict):
        start_sign(raw_config)
    else:
        logger.error(f"错误的 {env_config_name} 配置文件！")
