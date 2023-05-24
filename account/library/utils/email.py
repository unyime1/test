from typing import List

import requests

from library.utils.parameters import get_ssm_parameters


async def send_email(
    to_address: List[str], subject: str, body: str, name: str
) -> None:
    """Send email"""
    parameters = get_ssm_parameters()
    url = "https://api.zeptomail.com/v1.1/email"
    headers = {"Authorization": parameters["zoho_trans_mail"]}
    payload = {
        "bounce_address": "bounce@bounce.eelclip.com",
        "from": {"address": "noreply@eelclip.com", "name": "eelclip"},
        "to": [
            {"email_address": {"address": email, "name": "Eelclip"}}
            for email in to_address
        ],
        "subject": subject,
        "htmlbody": body,
    }
    res = requests.post(url, headers=headers, json=payload)
    print(res.json())
