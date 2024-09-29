import logging
from typing import Callable, Optional

import cloudscraper
import requests
import requests.adapters


class BaseSource:
    name: str
    headers: dict
    __versions_limit: int = -1

    def get_app_info(self, pkg: str, versions_limit: int = -1) -> 'App':
        self.__versions_limit = versions_limit
        return App(pkg, self)

    def download_app(self, pkg: str, version: 'AppVersion', output_file: Optional[str] = None, on_download_start: Callable[['AppVersion', int], None]|None = None, on_chunk_received: Callable[[int], None]|None = None, on_download_end: Callable[[int], None]|None = None):
        filename = output_file or f'{pkg}_{version.code}.apk'
        def mitm_on_download_start(file_size: int):
            if on_download_start is None:
                return
            on_download_start(version, file_size)
        self.download_file(self.get_download_link(pkg, version), self.headers, filename, version.size, mitm_on_download_start, on_chunk_received, on_download_end)

    def download_file(self, url: str, headers: dict, filename: str, file_size: int, on_download_start: Callable[[int], None]|None = None, on_chunk_received: Callable[[int], None]|None = None, on_download_end: Callable[[int], None]|None = None):
        with Request.get(url, headers=headers, stream=True) as r:
            if 'Content-Length' in r.headers:
                file_size = int(r.headers['Content-Length'])

            if on_download_start is not None:
                on_download_start(file_size)

            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if on_chunk_received is not None:
                        on_chunk_received(f.tell())
                if on_download_end is not None:
                    on_download_end(f.tell())

    def get_download_link(self, pkg: str, version: 'AppVersion') -> str:
        if version.download_link is None:
            raise TypeError(f'Download link missed for version "{version.code}"')

        return version.download_link

    def get_developer_id(self, package_name: str) -> str|None:
        return None

    def find_packages_from_developer(self, developer_id: str) -> set[str]:
        return set()

    def is_versions_limit(self, versions: list):
        return self.__versions_limit != -1 and len(versions) >= self.__versions_limit

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

    def get_version_by_code(self, code: int):
        return next((v for v in self.__versions if v.code == code))


class AppNotFoundError(Exception):
    pass

class DeveloperNotFoundError(Exception):
    pass

class Request:
    @staticmethod
    def get(url, params=None, use_cloudscraper: bool = False, **kwargs):
        session = Request.session()
        if use_cloudscraper:
            session = cloudscraper.create_scraper(sess=session)
            # Request.__set_middleware(session, RequestsMiddlewareCloudscraper())
        return session.request('get', url, params, **kwargs)

    @staticmethod
    def post(url, data=None, json=None, **kwargs):
        session = Request.session()
        return session.request('post', url, data=data, json=json, **kwargs)

    @staticmethod
    def session():
        session = requests.Session()
        Request.__set_middleware(session, RequestsMiddleware())
        return session

    @staticmethod
    def __set_middleware(session: requests.Session, middleware: requests.adapters.HTTPAdapter):
        session.mount('http://', middleware)
        session.mount('https://', middleware)

class RequestsMiddleware(requests.adapters.HTTPAdapter):
    def send(self, request: requests.PreparedRequest, stream: bool = False, timeout: None | float | tuple[float, float] | tuple[float, None] = None, verify: bool | str = True, cert: None | bytes | str | tuple[bytes | str, bytes | str] = None, proxies = None) -> requests.Response:
        response = super().send(request, stream, timeout, verify, cert, proxies)
        log_request(response.request, response)
        return response

class RequestsMiddlewareCloudscraper(cloudscraper.CipherSuiteAdapter):
    def send(self, request: requests.PreparedRequest, stream: bool = False, timeout: None | float | tuple[float, float] | tuple[float, None] = None, verify: bool | str = True, cert: None | bytes | str | tuple[bytes | str, bytes | str] = None, proxies = None) -> requests.Response:
        response = super().send(request, stream, timeout, verify, cert, proxies)
        log_request(response.request, response)
        return response

def log_request(request: requests.PreparedRequest, response: requests.Response):
    get_logger().debug(f'Request: {request.url}, response code: {response.status_code}')

def get_logger():
    return logging.getLogger('apkd')