import requests
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
        self._update_token()
        return requests.post(
            "http://hak-sms123.gov4c.kz/api/smsgateway/send",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}"
            },
            json={
                "phone_number": phone_number,
                "smsText": message,
            }
        )

    def get_document_order(self, request_id: str, iin: str):
        return requests.get(
            "http://89.218.80.61/vshep-api/con-sync-service",
            params={
                "requestId": request_id,
                "requestIIN": iin,
                "token": settings.EGOV_DOCUMENT_ORDER_TOKEN,
            }
        )
