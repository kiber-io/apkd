import json
from datetime import datetime

import progressbar
import requests
from user_agent import generate_user_agent


class RuStore:
    headers: dict
    source_name: str = 'RuStore'

    def __init__(self) -> None:
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.5',
            'deviceId': '9189138868050a43-1462194045',
            'deviceModel': 'samsung SM-S908E',
            'firmwareVer': '11',
            'firmwareLang': 'ru',
            'ruStoreVerCode': '247',
            'deviceType': 'mobile'
        }

    def search_app(self, pkg: str) -> dict:
        return self.get_app_info(pkg)

    def search_apps(self, packages: list) -> dict:
        apps = {}
        for pkg in packages:
            try:
                apps[pkg] = self.search_app(pkg)
            except FileNotFoundError:
                pass

        return apps

    def get_app_info(self, pkg: str) -> dict:
        app = {}
        response = requests.get(
            f'https://backapi.rustore.ru/applicationData/overallInfo/{pkg}', headers=self.headers)
        json_code = response.json()
        if 'code' not in json_code or json_code['code'] != 'OK':
            raise FileNotFoundError(f'Package {pkg} not found')
        version_code = json_code['body']['versionCode']
        version = json_code['body']['versionName'].split('-rustore')[0]
        update_date = json_code['body']['appVerUpdatedAt']
        update_date = datetime.strptime(
            update_date, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m.%d.%Y')

        appId = json_code['body']['appId']
        response = requests.post('https://backapi.rustore.ru/applicationData/v2/download-link', json={
            "appId": appId,
            "firstInstall": True,
            "mobileServices": ["GMS"],
            "supportedAbis": ["x86_64", "x86", "arm64-v8a", "armeabi-v7a", "armeabi"],
            "screenDensity": 240,
            "supportedLocales": ["en_US"],
            "sdkVersion": 30,
            "withoutSplits": True,
            "signatureFingerprint": None,
        }, headers=self.headers)
        json_code = response.json()
        if 'code' not in json_code or json_code['code'] != 'OK':
            raise FileNotFoundError(f'Package {pkg} not found')
        download_url = json_code['body']['downloadUrls'][0]['url']
        file_size = json_code['body']['downloadUrls'][0]['size']

        app['versions'] = [{
            'version': version,
            'version_code': version_code,
            'file_size': file_size,
            'update_date': update_date,
            'download_url': download_url,
        }]

        return app

    def download_app(self, pkg: str, version: dict):
        with requests.get(version['download_url'], headers=self.headers, stream=True) as r:
            file_size = version['file_size']
            filename = f'{pkg}_{version["version_code"]}.apk'
            bar = progressbar.ProgressBar(max_value=file_size, term_width=100, widgets=[
                filename,
                ' ',
                progressbar.Bar(),
                ' ',
                progressbar.widgets.FileTransferSpeed(),
            ])
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(f.tell())
            bar.finish()
            return filename
