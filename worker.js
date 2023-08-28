addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

addEventListener('scheduled', event => {
  console.log("Cron job started!");
  event.waitUntil(main());
})

var configUrl = '';
var rawConfig = {}

function divmod(dividend, divisor) {
  const quotient = Math.floor(dividend / divisor);
  const remainder = dividend % divisor;
  return [quotient, remainder];
}


async function startSign(config) {
  var output = '';
  const token = config['x-rpc-combo_token'];
  const clientType = config['x-rpc-client_type'] || '2';
  const android = config['x-rpc-sys_version'] || "13";
  const deviceid = config['x-rpc-device_id'];
  const devicename = config['x-rpc-device_name'] || "Xiaomi 2304FPN6DG";
  const devicemodel = config['x-rpc-device_model'] || "2304FPN6DG";
  const appid = config['x-rpc-app_id'] || "1953439974";
  const bbsid = token.split('oi=')[1].split(';')[0];

  const NotificationURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup&is_sort=true';
  const WalletURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/wallet/wallet/get';
  const AnnouncementURL = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/gamer/api/getAnnouncementInfo';

  try {
    const verInfoResponse = await fetch('https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource?key=eYd89JmJ&launcher_id=18', {headers: {}});
    const verInfo = await verInfoResponse.json();
    var version = verInfo.data.game.latest.version;
    console.log(`从官方API获取到云·原神最新版本号：${version}`);
  } catch (error) {
    console.log('无法从官方 API 获取版本号信息!');
    const version = config.version || config['x-rpc-app_version'];
    if (!version) {
      console.error("获取失败！程序无法运行");
      return '无法获取云 · 原神具体版本';
    }
  }

  const headers = {
    'x-rpc-combo_token': token,
    'x-rpc-client_type': clientType,
    'x-rpc-app_version': version,
    'x-rpc-sys_version': android, 
    'x-rpc-channel': 'mihoyo',
    'x-rpc-device_id': deviceid,
    'x-rpc-device_name': devicename,
    'x-rpc-device_model': devicemodel,
    'x-rpc-app_id': appid,
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

  const WalletInfoResponse = await fetch(WalletURL, {headers: headers});
  const WalletInfo = await WalletInfoResponse.json();
  if (!WalletInfo.data) {
    return `当前登录已过期，请重新登陆！返回为：${WalletInfo}`;
  }
  const f_time = divmod(parseInt(WalletInfo['data']['free_time']['free_time']), 60)
  output += `ID: ${bbsid} ,免费时长 ${f_time[0]} 小时 ${f_time[1]} 分钟,畅玩卡： ${WalletInfo['data']['play_card']['short_msg']},米云币： ${WalletInfo['data']['coin']['coin_num']} 枚\n`;
  await fetch(AnnouncementURL, {headers: headers})
  const CheckSignedResponse = await fetch(NotificationURL, {headers: headers});
  const CheckSigned = await CheckSignedResponse.json();
  var status = [0, 0, 0];

  if (!CheckSigned['data']['list'].length) {
    status = [1, 1, 0];
  } else if (CheckSigned['data']['list'][0]['msg']['func_type'] === 1) {
    status = [1, 0, 0];
  } else if (CheckSigned['data']['list'][0]['msg']['over_num'] > 0) {
    status = [1, 0, 1];
  } else {
    status = [0, 0, 0];
  }

  if (status[0]) {
    if (status[1]) {
      output += 'The account has already signed!';
    } else if (status[2]) {
      output += 'The account has already up to the max minutes';
    } else {
      output += 'Sign success!';
    }
  } else {
    return 'Sign failed!';
  } 
  console.log(output);
  return output;
}

async function handleRequest(request) {
  if (!rawConfig) {
    if (configUrl) {
      try {
        const rawConfigResponse = await fetch(configUrl);
        rawConfig = await rawConfigResponse.json();
      } catch (error) {
        return new Response('Error while getting the headers', {status: 500})
      }
    }
  }
  if (request.method === 'POST' && request['Content-Type'] === 'application/json') {
    rawConfig = await request.json();
    return;
  }
  return await main();
}

async function main() {
  let res = '';
  try {
    if (Array.isArray(rawConfig)) {
      for (const c of rawConfig) {
        res += String(await startSign(c));
      }
    } else if (typeof rawConfig === 'object') {
      res = String(await startSign(rawConfig));
    } else {
      return new Response(`Whrong headers`, { status: 500 });
    }
  } catch (error) {
    console.error(error);
  }
  return new Response(`Complete\nResult: ${res}`)
}

