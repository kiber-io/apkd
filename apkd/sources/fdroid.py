from typing import cast
from datetime import datetime

from user_agent import generate_user_agent
from bs4 import BeautifulSoup, Tag

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource, Request


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'F-Droid'
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.5',
            'User-Agent': generate_user_agent()
        }

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> App:
        app: App = super().get_app_info(pkg, versions_limit)
        response = Request.get(
            f'https://f-droid.org/en/packages/{pkg}', headers=self.headers)
        if response.status_code == 404:
            raise AppNotFoundError()
        soup = BeautifulSoup(response.text, features='html.parser')
        versions: list[AppVersion] = []
        block: Tag
        for block in soup.find_all('li', class_='package-version'):
            package_version_header = cast(Tag, block.find('div', class_='package-version-header'))
            version_blocks = package_version_header.findChildren('a')
            version_name = version_blocks[0].get('name')
            version_code = version_blocks[1].get('name')
            update_date = ' '.join(cast(str, package_version_header.contents[-1]).strip().split(' ')[-3:])
            update_date = datetime.strptime(update_date, '%b %d, %Y').strftime('%d.%m.%Y')

            package_version_download = cast(Tag, block.find('p', class_='package-version-download'))
            download_block = package_version_download.find_next('a')
            download_block = cast(Tag, download_block)
            download_link = download_block.get('href')
            download_link = cast(str, download_link)

            file_size_block = package_version_download.contents[2]
            file_size_mb = file_size_block.get_text().replace('MiB', '').strip()
            file_size = int(float(file_size_mb) * 1024 * 1024)

            versions.append(AppVersion(version_name, int(version_code), file_size, self, update_date, download_link))
            if self.is_versions_limit(versions):
                break

        app.set_versions(versions)
        return app