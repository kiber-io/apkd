from typing import cast

import progressbar
import requests
from bs4 import BeautifulSoup, Tag
from user_agent import generate_user_agent


class ApkPure:
    source_name: str = 'ApkPure'

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
        response = requests.get(f'https://apkpure.com/ru/search?q={pkg}', headers={
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkpure.com/ru/',
        })
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        div_first_apk = soup.find('div', class_='first')
        if div_first_apk is None:
            raise FileNotFoundError(f'Package "{pkg}" not found')
        div_first_apk = cast(Tag, div_first_apk)
        web_pkg = div_first_apk.get('data-dt-app')
        if web_pkg != pkg:
            raise FileNotFoundError(f'Package "{pkg}" not found')
        url_block = div_first_apk.find('a', class_='first-info')
        url_block = cast(Tag, url_block)
        url = url_block.get('href')
        url = cast(str, url)
        app['versions'] = self.list_app_versions(url)

        return app

    def list_app_versions(self, url: str) -> list:
        versions = []
        response = requests.get(f'{url}/versions', headers={
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkpure.com/ru/',
        })
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        for block in soup.find_all('a', class_='ver_download_link'):
            info = {}
            block = cast(Tag, block)
            version_number = block.get('data-dt-version')
            version_code = block.get('data-dt-versioncode')
            file_size = block.get('data-dt-filesize')
            date_block = block.find('span', class_='update-on')
            if date_block is not None:
                date_block_text = date_block.get_text()
                info['update_date'] = date_block_text.strip()
            info['version'] = version_number
            version_code = cast(str, version_code)
            info['version_code'] = int(version_code)
            file_size = cast(str, file_size)
            file_size = int(file_size)
            # file_size_mb = file_size / (1024 * 1024)
            info['file_size'] = file_size
            # info['file_size'] = f'{file_size_mb:.2f}'
            versions.append(info)

        return versions


    # https://d.apkpure.com/b/APK/com.vkontakte.android?versionCode=19238
    def download_app(self, pkg: str, version: dict):
        with requests.get(f'https://d.apkpure.com/b/APK/{pkg}?versionCode={version["version_code"]}', headers={
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkpure.com/ru/',
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
                    bar.update(f.tell())
            bar.finish()
            return filename