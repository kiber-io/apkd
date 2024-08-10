from typing import Optional

import progressbar
import requests
import logging

import requests.adapters


class BaseSource:
    name: str
    headers: dict

    def get_app_info(self, pkg: str) -> 'App':
        return App(pkg, self)

    def download_app(self, pkg: str, version: 'AppVersion', output_file: Optional[str] = None):
        filename = output_file or f'{pkg}_{version.code}.apk'
        progress_text = f'{version.source.name}: {pkg} ({version.code}) '
        self.download_file(self.get_download_link(pkg, version), self.headers, filename, version.size, progress_text)

    def download_file(self, url: str, headers: dict, filename: str, file_size: int, progress_text: str):
        with Request.get(url, headers=headers, stream=True) as r:
            bar = progressbar.ProgressBar(max_value=file_size, term_width=100, widgets=[
                progress_text,
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

    def get_download_link(self, pkg: str, version: 'AppVersion') -> str:
        if version.download_link is None:
            raise TypeError(f'Download link missed for version "{version.code}"')

        return version.download_link

class AppVersion:
    download_link: Optional[str] = None
    name: str
    code: int
    update_date: Optional[str] = None
    size: int
    source: BaseSource

    def __init__(self, name: str, code: int, size: int, source: BaseSource, update_date: Optional[str] = None, download_link: Optional[str] = None) -> None:
        if isinstance(update_date, str):
            self.update_date = update_date
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

class Request:
    @staticmethod
    def get(url, params=None, **kwargs):
        session = Request.session()
        return session.request('get', url, params, **kwargs)

    @staticmethod
    def post(url, data=None, json=None, **kwargs):
        session = Request.session()
        return session.request('post', url, data=data, json=json, **kwargs)

    @staticmethod
    def session():
        middleware = RequestsMiddleware()
        session = requests.Session()
        session.mount('http://', middleware)
        session.mount('https://', middleware)
        return session

class RequestsMiddleware(requests.adapters.HTTPAdapter):
    def send(self, request: requests.PreparedRequest, stream: bool = False, timeout: None | float | tuple[float, float] | tuple[float, None] = None, verify: bool | str = True, cert: None | bytes | str | tuple[bytes | str, bytes | str] = None, proxies = None) -> requests.Response:
        response = super().send(request, stream, timeout, verify, cert, proxies)
        return response