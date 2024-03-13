from typing import cast

import progressbar
import requests
from bs4 import BeautifulSoup, Tag
from pypasser import reCaptchaV3
from user_agent import generate_user_agent


class ApkCombo:
    source_name: str = 'ApkCombo'

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
        app['versions'] = self.list_app_versions(f'https://apkcombo.com/ru/downloader/?package={pkg}&ajax=1')

        return app

    def list_app_versions(self, url: str) -> list:
        ua = generate_user_agent()
        response = requests.post('https://apkcombo.com/checkin', data={
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkcombo.com/ru/downloader/',
        })
        checkin = response.text
        versions = []
        recaptcha_token = reCaptchaV3('https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LffOIUUAAAAACDGY5pUGox0yBGBUvRD8aT8c2J0&co=aHR0cHM6Ly9hcGtjb21iby5jb206NDQz&hl=ru&v=QquE1_MNjnFHgZF4HPsEcf_2&size=invisible&cb=kuyn1i99ewi2')
        response = requests.get(url, headers={
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkcombo.com/ru/downloader/',
            'token': recaptcha_token
        })
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        for block in soup.find_all('a', class_='variant'):
            type_apk = block.find('span', class_='type-apk')
            if type_apk is None or type_apk.get_text().strip() != 'APK':
                continue
            info = {}
            download_url = block.get('href')
            version_name_block = block.find('span', class_='vername')
            version_name = version_name_block.get_text().strip().split(' ')[-1]
            version_code = block.find('span', class_='vercode').get_text().strip()[1:-1]
            file_size = block.find('span', class_='spec').get_text().strip().split(' ')[0]
            info['download_url'] = f'{download_url}&{checkin}'
            info['version'] = version_name
            info['version_code'] = int(version_code)
            file_size = int(file_size) * 1024 * 1024
            info['file_size'] = file_size
            info['update_date'] = '?'
            versions.append(info)

        return versions

    def download_app(self, pkg: str, version: dict) -> str:
        with requests.get(version['download_url'], headers={
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkcombo.com/ru/downloader/',
        }, stream=True) as r:
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
                    try:
                        bar.update(f.tell())
                    except ValueError:
                        continue
            bar.finish()
            return filename