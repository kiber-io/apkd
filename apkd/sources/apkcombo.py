
from bs4 import BeautifulSoup, Tag
from user_agent import generate_user_agent

from apkd.libs.pypasser import reCaptchaV3
from apkd.utils import (App, AppNotFoundError, AppVersion, BaseSource, Request,
                        get_logger)


class Source(BaseSource):
    headers: dict
    checkin: str

    def __init__(self):
        super().__init__()
        self.name = 'ApkCombo'
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkcombo.com/ru/downloader/',
        }
        response = Request.post(
            'https://apkcombo.com/checkin', headers=self.headers)
        self.checkin = response.text

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        self.headers['token'] = reCaptchaV3(
            'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LffOIUUAAAAACDGY5pUGox0yBGBUvRD8aT8c2J0&co=aHR0cHM6Ly9hcGtjb21iby5jb206NDQz&hl=ru&v=QquE1_MNjnFHgZF4HPsEcf_2&size=invisible&cb=kuyn1i99ewi2')
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.get(
            f'https://apkcombo.com/ru/downloader/?package={pkg}&ajax=1', headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        versions: list[AppVersion] = []
        for block in soup.find_all('a', class_='variant'):
            type_apk = None
            type_apk_block = block.find('span', class_='type-apk')
            if type_apk_block is not None:
                type_apk = type_apk_block.get_text().strip()
            if type_apk != 'APK':
                get_logger().warning(f'ApkCombo: {pkg} is not of the APK type')
                continue
            download_url = block.get('href')
            version_name_block = block.find('span', class_='vername')
            version_name = version_name_block.get_text().strip().split(' ')[-1]
            version_code = block.find(
                'span', class_='vercode').get_text().strip()[1:-1]
            file_size = block.find(
                'span', class_='spec').get_text().strip().split(' ')[0]
            file_size = int(float(file_size)) * 1024 * 1024
            version = AppVersion(version_name, int(
                version_code), file_size, self, download_link=f'{download_url}&{self.checkin}')
            versions.append(version)
            if self.is_versions_limit(versions):
                break

        if len(versions) == 0:
            raise AppNotFoundError()

        app.set_versions(versions)

        return app

    def get_developer_id(self, package_name: str) -> str | None:
        response = Request.get(
            f'https://apkcombo.com/ru/downloader/?package={package_name}&ajax=1', headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        developer_id = None
        author = soup.find('div', class_='author')
        if isinstance(author, Tag):
            a_link = author.find('a', class_='is-link')
            if isinstance(a_link, Tag):
                developer_id = a_link.text.strip()

        return developer_id

    def find_packages_from_developer(self, developer_id: str) -> set[str]:
        packages = set()

        response = Request.get(
            f'https://apkcombo.com/developer/{developer_id}', headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        for item in soup.find_all('a', class_='l_item'):
            if not isinstance(item, Tag):
                continue
            link = item.attrs['href']
            if link.endswith('/'):
                link = link[:-1]
            package = link.split('/')[-1]
            packages.add(package)

        return packages