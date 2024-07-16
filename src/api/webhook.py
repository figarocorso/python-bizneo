import requests


def send_message_to_webhook(webhook, report_text, headers):
    response = requests.post(webhook, data=report_text, headers=headers)
    return response.ok, response.text
