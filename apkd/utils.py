from typing import Optional

import progressbar
import requests


class BaseSource:
    name: str
    headers: dict

    def get_app_info(self, pkg: str) -> 'App':
        return App(pkg, self)

    def download_app(self, pkg: str, version: 'AppVersion', output_file: Optional[str] = None):
        filename = output_file or f'{pkg}_{version.code}.apk'
        self.download_file(version.download_link, self.headers, filename, version.size)

    def download_file(self, url: str, headers: dict, filename: str, file_size: int):
        with requests.get(url, headers=headers, stream=True) as r:
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


class AppVersion:
    download_link: str
    name: str
    code: int
    update_date: str
    size: int
    source: BaseSource

    def __init__(self, download_link: str, name: str, code: int, size: int, source: BaseSource, update_date: Optional[str] = None) -> None:
        self.update_date = update_date or '--.--.----'
        self.source = source
        self.download_link = download_link
        self.name = name
        self.code = code
        self.size = size


class App:
    __versions: list[AppVersion]
    package: str
    source: BaseSource

    def __init__(self, package: str, source: BaseSource) -> None:
        self.package = package
        self.source = source
        self.__versions = []

    def set_versions(self, versions: list):
        self.__versions = sorted(versions, key=lambda x: x.code, reverse=True)

    def get_versions(self):
        return self.__versions

    def get_version_by_idx(self, idx: int):
        return self.__versions[idx]

    def get_version_by_code(self, code: int):
        return next((v for v in self.__versions if v.code == code))


class AppNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
