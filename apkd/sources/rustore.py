from datetime import datetime

from user_agent import generate_user_agent

from apkd.utils import (App, AppNotFoundError, AppVersion, BaseSource,
                        DeveloperNotFoundError, Request)


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'RuStore'
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

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.get(
            f'https://backapi.rustore.ru/applicationData/overallInfo/{pkg}', headers=self.headers)
        json_code = response.json()
        if 'code' not in json_code or json_code['code'] != 'OK':
            raise AppNotFoundError()
        version_code = json_code['body']['versionCode']
        version = json_code['body']['versionName'].split('-rustore')[0]
        update_date = json_code['body']['appVerUpdatedAt']
        update_date = datetime.strptime(
            update_date, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m.%d.%Y')

        app_id = json_code['body']['appId']
        response = Request.post('https://backapi.rustore.ru/applicationData/v2/download-link', json={
            "appId": app_id,
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

        app.set_versions(
            [AppVersion(version, version_code, file_size, self, update_date, download_url)])
        return app

    def get_developer_id(self, package_name: str) -> str|None:
        response = Request.get(
            f'https://backapi.rustore.ru/applicationData/overallInfo/{package_name}', headers=self.headers)
        json_code = response.json()
        if 'code' not in json_code or json_code['code'] != 'OK':
            raise AppNotFoundError()
        developer_id = json_code['body']['publicCompanyId']

        return developer_id

    def find_packages_from_developer(self, developer_id: str) -> set[str]:
        packages = set()

        response = Request.get(
            f'https://backapi.rustore.ru/applicationData/devs/{developer_id}/apps?limit=999999', headers=self.headers)
        json_code = response.json()
        if 'code' not in json_code or json_code['code'] != 'OK':
            raise DeveloperNotFoundError()
        for app in json_code['body']['elements']:
            packages.add(app['packageName'])

        return packages