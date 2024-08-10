from typing import Dict, Union

import requests

from apkd.utils import Request

from ..pypasser.exceptions import ConnectionError


class Session():
    def __init__(self, base_url: str, base_headers: dict, timeout: Union[int, float]):
        self.base_url = base_url
        self.req_session = Request.session()
        self.req_session.headers = base_headers
        self.timeout = timeout

    def send_request(self, endpoint: str, data: Union[str, Dict]|None = None, params: str|None = None) -> requests.Response:
        try:
            if data:
                response = self.req_session.post(self.base_url.format(endpoint), data=data, params=params, timeout=self.timeout)
            else:
                response = self.req_session.get(self.base_url.format(endpoint), params=params, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise ConnectionError()

        return response