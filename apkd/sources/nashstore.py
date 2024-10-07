import json
from datetime import datetime

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource, Request
import string
import random


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'NashStore'
        self.headers = {
            'User-Agent': 'Nashstore [com.nashstore][0.0.6][Motorola',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.5',
            'xaccesstoken': 'd323e82b2a3cade95143f1c15d8f1d840a6c62eddf0009138078d7108b4aa40a',
            'nashstore-app': json.dumps({
                'androidId': self.generate_device_id(),
                'apiLevel': 21,
                'baseOs': '',
                'buildId': 'UKQ1.230804.001',
                'carrier': 'MTS',
                'deviceName': 'XT1650-05',
                'fingerprint': 'motorola/griffin_retcn/griffin:6.0.1/MCC24.246-37/42:user/release-keys',
                'fontScale': 1,
                'brand': 'Motorola',
                'deviceId': 'griffin',
                'width': 400,
                'height': 835.3333333333334,
                'scale': 3
            }),
            'Content-Type': 'application/json'
        }

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.post(
            'https://store.nashstore.ru/api/mobile/v1/profile/updates', headers=self.headers, data=json.dumps({
                "apps": {
                    f"{pkg}": {
                        "packageName": f"{pkg}"
                    }
                }
            }))
        json_code = response.json()
        if 'list' not in json_code or len(json_code['list']) != 1:
            raise AppNotFoundError()
        app_json = json_code['list'][0]
        version_code = app_json['release']['version_code']
        version = app_json['release']['version_name']
        update_date = app_json['release']['create_at']
        # nashstore has two date types (wtf?!)
        datetime_date: datetime
        try:
            datetime_date = datetime.strptime(update_date, '%Y-%m-%dT%H:%M:%S%z')
        except ValueError:
            datetime_date = datetime.strptime(update_date, '%Y-%m-%dT%H:%M:%S.%f%z')

        update_date = datetime_date.strftime('%m.%d.%Y')

        download_url = app_json['release']['install_path']
        file_size = app_json['size']

        app.set_versions([AppVersion(version, version_code, file_size, self, update_date, download_url)])
        return app

    def generate_device_id(self) -> str:
        template = [*(string.digits + string.ascii_lowercase)]
        random.shuffle(template)
        return ''.join(template[:16])