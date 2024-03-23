from datetime import datetime
from uuid import uuid4

import requests
from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource

import string
import random


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'Aptoide'
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'user-agent': f'aptoide-9.20.6.1;23127PN0CG(houji);v14;aarch64;0x0;id:{uuid4()};;'
        }

    def get_app_info(self, pkg: str) -> App:
        app: App = super().get_app_info(pkg)
        response = requests.get(f'https://ws75-cache.aptoide.com/api/7/getApp?aab=false&package_name={pkg}', headers=self.headers)
        json_code = response.json()
        if json_code['info']['status'] != 'OK':
            raise AppNotFoundError()
        json_versions = json_code['nodes']['versions']
        versions: list[AppVersion] = []
        for json_version in json_versions['list']:
            version_name = json_version['file']['vername']
            version_code = json_version['file']['vercode']
            file_size = json_version['file']['filesize']
            modified_date = json_version['file']['added']
            update_date = datetime.strptime(modified_date, "%Y-%m-%d %H:%M:%S").strftime('%d.%m.%Y')
            versions.append(AppVersion(version_name, version_code, file_size, self, update_date))

        app.set_versions(versions)
        return app

    def generate_device_id(self) -> str:
        template = [*(string.digits + string.ascii_lowercase)] * 2
        random.shuffle(template)
        return ''.join(template[:64])

    def get_download_link(self, pkg: str, version: AppVersion) -> str:
        response = requests.get(f'https://ws75-cache.aptoide.com/api/7/getApp?aab=false&package_name={pkg}&vercode={version.code}', headers=self.headers)
        json_code = response.json()
        if json_code['info']['status'] != 'OK':
            raise AppNotFoundError()
        download_link = json_code['nodes']['meta']['data']['file']['path']

        return download_link