import boto3

from config import TESTING


def get_ssm_parameters():
    """Get ssm parameters."""

    if TESTING:
        return {
            "zoho_trans_mail": "",
            "app_secret_key": "secret",
            "pixabay_api_key": "",
            "sentry_accounts": "",
            "sentry_main": "",
            "unsplash_access_key": "",
            "unsplash_secret_key": "",
            "zoho_trans_mail": "",
        }

    ssm = boto3.client("ssm")
    parameters = ssm.get_parameters(
        Names=[
            "zoho_trans_mail",
            "app_secret_key",
            "pixabay_api_key",
            "sentry_accounts",
            "sentry_main",
            "unsplash_access_key",
            "unsplash_secret_key",
            "zoho_trans_mail",
        ],
        WithDecryption=True,
    )

    data = {}
    for item in parameters.get("Parameters"):
        data.update({item.get("Name"): item.get("Value")})
    return data
