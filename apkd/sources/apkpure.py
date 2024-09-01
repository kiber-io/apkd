import datetime
from typing import cast

from bs4 import BeautifulSoup, Tag
from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource, Request


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'ApkPure'
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkpure.com/',
        }

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.get(
            f'https://apkpure.com/search?q={pkg}', use_cloudscraper=True, headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        div_first_apk = soup.find('div', class_='first')
        if div_first_apk is None:
            raise AppNotFoundError()
        div_first_apk = cast(Tag, div_first_apk)
        web_pkg = div_first_apk.get('data-dt-app')
        if web_pkg != pkg:
            raise AppNotFoundError()
        url_block = div_first_apk.find('a', class_='first-info')
        url_block = cast(Tag, url_block)
        url = url_block.get('href')
        url = cast(str, url)

        response = Request.get(f'{url}/versions', use_cloudscraper=True, headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        versions: list[AppVersion] = []
        for block in soup.find_all('a', class_='ver_download_link'):
            block = cast(Tag, block)
            apkid: str = block.attrs['data-dt-apkid']
            if not apkid.startswith('b/APK'):
                continue
            version_name = block.get('data-dt-version')
            version_code = block.get('data-dt-versioncode')
            file_size = block.get('data-dt-filesize')
            date_block = block.find('span', class_='update-on')
            update_date = None
            if date_block is not None:
                date_block_text = date_block.get_text()
                update_date = date_block_text.strip()
                update_date = datetime.datetime.strptime(
                    update_date, '%b %d, %Y').strftime('%d.%m.%Y')

            version_name = cast(str, version_name)
            version_code = int(cast(str, version_code))
            file_size = cast(str, file_size)
            file_size = int(file_size)
            download_link = f'https://d.apkpure.com/b/APK/{pkg}?versionCode={version_code}'

            version: AppVersion = AppVersion(
                version_name, version_code, file_size, self, update_date, download_link)
            versions.append(version)
            if self.is_versions_limit(versions):
                break

        if len(versions) == 0:
            raise AppNotFoundError()

        app.set_versions(versions)

        return app

    def get_developer_id(self, package_name: str) -> str | None:
        response = Request.get(
            f'https://apkpure.com/search?q={package_name}', use_cloudscraper=True, headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        div_first_apk = soup.find('div', class_='first')
        if div_first_apk is None:
            raise AppNotFoundError()
        div_first_apk = cast(Tag, div_first_apk)
        web_pkg = div_first_apk.get('data-dt-app')
        if web_pkg != package_name:
            raise AppNotFoundError()
        url_block = div_first_apk.find('a', class_='first-info')
        url_block = cast(Tag, url_block)
        url = url_block.get('href')
        url = cast(str, url)

        response = Request.get(f'{url}/versions', use_cloudscraper=True, headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        developer_id = None
        ver_dev = soup.find('p', class_='ver_dev')
        if isinstance(ver_dev, Tag):
            ver_dev_a = ver_dev.find('a')
            if isinstance(ver_dev_a, Tag):
                developer_id = ver_dev_a.text.strip()

        return developer_id

    def find_packages_from_developer(self, developer_id: str) -> set[str]:
        packages = set()

        response = Request.get(
            f'https://apkpure.com/developer/{developer_id}', use_cloudscraper=True, headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        for item in soup.find_all('p', class_='search-title'):
            if not isinstance(item, Tag):
                continue
            a_item = item.find('a')
            if isinstance(a_item, Tag):
                packages.add(a_item.attrs['href'].split('/')[-1])

        return packages