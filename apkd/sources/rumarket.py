from datetime import datetime
from uuid import uuid4

import requests
from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'RuMarket'
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.5',
            'Accept-Charset': 'UTF-8',
            'Authorization': 'Bearer',
            'rumarket-api': 'Bearer',
            'User-Agent': f'RuMarket(3.5.6);sdk_gphone64_x86_64 Google;34;{uuid4()};'
        }

    def get_app_info(self, pkg: str) -> App:
        app: App = super().get_app_info(pkg)
        response = requests.get(
            f'https://store-api.ruplay.market/api/v1/app/getApp/{pkg}', headers=self.headers)
        if response.status_code == 404:
            raise AppNotFoundError()
        json_code = response.json()
        version_code = json_code['data']['latestApk']['versionCode']
        version_name = json_code['data']['latestApk']['versionName']
        update_date = json_code['data']['updatedAt']
        update_date = datetime.strptime(
            update_date, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m.%d.%Y')
        download_url = f'https://store.ruplay.market/app/{pkg}'
        file_size = json_code['data']['latestApk']['size']

        app.set_versions(
            [AppVersion(version_name, version_code, file_size, self, update_date, download_url)])
        return app