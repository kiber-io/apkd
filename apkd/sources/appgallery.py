from datetime import datetime
from uuid import uuid4

from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource, Request

import string
import random
from urllib.parse import urlencode
import time
import json


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'AppGallery'
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'network-out': 'NWK(time/20240319173023017)',
            'net-msg-id': str(uuid4()),
            'network-vendor': 'NWK',
            'network-in': 'NWK(time/20240319173023016)',
            'sysUserAgent': 'Mozilla/5.0 (Linux; Android 14; 23127PN0CG Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.106 Mobile Safari/537.36',
        }

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.post('https://store-drru.hispace.dbankcloud.ru/hwmarket/api/clientApi', headers=self.headers, data=urlencode({
            'callWay': '2',
            'clientPackage': 'com.huawei.appmarket',
            'code': '0200',
            'deviceId': self.generate_device_id(),
            'deviceIdType': 9,
            'method': 'client.agdSecurityVerification',
            'net': 1,
            'pkgName': pkg,
            'sign': 'u90035905i0121062000001007u003500a0000000500200000010000000010000070230b0100011000000@46CC28CBB85C45259311A01057E9CB41',
            'ts': round(time.time()),
            'uriParams': json.dumps({
                'callType': 'default',
                'cdcParams': json.dumps({
                    'accessID': '',
                    'channelId': '',
                    'detailType': '',
                    'extraParam': '',
                    'id': pkg,
                    'initParam': '',
                    's': ''
                }),
                'downloadParams': '',
                'installType': ''
            }),
            'ver': '1.1'
        }))
        json_code = response.json()
        if 'titleType' not in json_code or json_code['titleType'] is None:
            raise AppNotFoundError()
        data = None
        for layout_data in json_code['layoutData']:
            if data is not None:
                break
            # apps direct from appgallery has appid from 10 characters - "C" + 9 digits
            # apps from third-party services has appid from 19 characters - "C" + 18 digits
            for data_list in layout_data['dataList']:
                if 'appid' in data_list and len(data_list['appid']) == 10 and 'package' in data_list and data_list['package'] == pkg:
                    data = data_list
                    break

        if data is None:
            raise AppNotFoundError()
        version_name = data['versionName']
        version_code = int(data['versionCode'])
        file_size = data['fullSize']
        download_url = data['downurl']

        app.set_versions(
            [AppVersion(version_name, version_code, file_size, self, download_link=download_url)])
        return app

    def generate_device_id(self) -> str:
        template = [*(string.digits + string.ascii_lowercase)] * 2
        random.shuffle(template)
        return ''.join(template[:64])