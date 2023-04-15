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

    def get_phone_by_iin(self, iin: str):
        self._update_token()
        return requests.get(
            f"http://hakaton.gov4c.kz/api/bmg/check/{iin}/",
            headers={
                "Authorization": f"Bearer {self._token}"
            }
        )

    def send_message_by_phone(self, phone: str, smsText: str):
        self._update_token()
        return requests.post(
            "http://hakaton-sms.gov4c.kz/api/smsgateway/send",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}"
            },
            data={
                "phone": phone,
                "smsText": smsText
            }
        )
