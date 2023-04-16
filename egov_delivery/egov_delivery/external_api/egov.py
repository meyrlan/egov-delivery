import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from django.conf import settings


class Client:
    def __init__(
        self,
        token=None,
        username=settings.EGOV_API_USERNAME,
        password=settings.EGOV_API_PASSWORD,
        client_id=settings.EGOV_API_CLIENT_ID,
        grant_type=settings.EGOV_API_GRANT_TYPE,
    ) -> None:
        self._token = token
        self._username = username
        self._password = password
        self._client_id = client_id
        self._grant_type = grant_type
        self._headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _update_token(self):
        response = requests.post(
            "http://hakaton-idp.gov4c.kz/auth/realms/con-web/protocol/openid-connect/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "username": self._username,
                "password": self._password,
                "client_id": self._client_id,
                "grant_type": self._grant_type,
            }
        )
        response_json = response.json()
        self._token = response_json.get("access_token")

    def get_user_by_iin(self, iin: str):
        self._update_token()
        return requests.get(
            f"http://hakaton-fl.gov4c.kz/api/persons/{iin}/",
            headers={
                "Authorization": f"Bearer {self._token}"
            }
        )

    def get_phone_number_by_iin(self, iin: str):
        self._update_token()
        return requests.get(
            f"http://hakaton.gov4c.kz/api/bmg/check/{iin}/",
            headers={
                "Authorization": f"Bearer {self._token}"
            }
        )

    def send_message_by_phone_number(self, phone_number: str, message: str):
        if phone_number[0] == '+':
            phone_number = phone_number[1:]
        self._update_token()
        response = requests.post(
            "http://hak-sms123.gov4c.kz/api/smsgateway/send",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}"
            },
            json={
                "phone": phone_number,
                "smsText": message,
            }
        )
        print(response.status_code)
        print(response.text)
        return response

    def get_document_order(self, request_id: str, iin: str):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        try:
            response = http.get(
                "http://89.218.80.61/vshep-api/con-sync-service",
                params={
                    "requestId": request_id,
                    "requestIIN": iin,
                    "token": settings.EGOV_DOCUMENT_ORDER_TOKEN,
                },
                timeout=1
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f"Error: {err}")
            raise
        return response
