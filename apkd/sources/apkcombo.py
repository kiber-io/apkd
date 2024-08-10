
from bs4 import BeautifulSoup
from apkd.libs.pypasser import reCaptchaV3
from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource, Request


class Source(BaseSource):
    headers: dict

    def __init__(self):
        super().__init__()
        self.name = 'ApkCombo'
        recaptcha_token = reCaptchaV3(
            'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LffOIUUAAAAACDGY5pUGox0yBGBUvRD8aT8c2J0&co=aHR0cHM6Ly9hcGtjb21iby5jb206NDQz&hl=ru&v=QquE1_MNjnFHgZF4HPsEcf_2&size=invisible&cb=kuyn1i99ewi2')
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'Referer': 'https://apkcombo.com/ru/downloader/',
            'token': recaptcha_token
        }

    def get_app_info(self, pkg: str) -> App:
        app: App = super().get_app_info(pkg)
        response = Request.post(
            'https://apkcombo.com/checkin', headers=self.headers)
        checkin = response.text
        response = Request.get(
            f'https://apkcombo.com/ru/downloader/?package={pkg}&ajax=1', headers=self.headers)
        html_code = response.text
        soup = BeautifulSoup(html_code, features='html.parser')
        versions: list[AppVersion] = []
        for block in soup.find_all('a', class_='variant'):
            type_apk = block.find('span', class_='type-apk')
            if type_apk is None or type_apk.get_text().strip() != 'APK':
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
                version_code), file_size, self, download_link=f'{download_url}&{checkin}')
            versions.append(version)

        if len(versions) == 0:
            raise AppNotFoundError()

        app.set_versions(versions)

        return app