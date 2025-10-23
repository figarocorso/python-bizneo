import requests


def send_message_to_webhook(webhook, report_text, headers):
    """Send a message to a webhook using the new payload format.

    Args:
        webhook: URL endpoint to POST the message
        report_text: The message body to send
        headers: Dictionary containing routing metadata (e.g., 'channel-id' with Slack user ID)

    Returns:
        Tuple of (success: bool, response_text: str)

    Note:
        The payload now uses the format:
        {
            "recipient": <slack_user_id>,  # extracted from headers['channel-id']
            "body": <report_text>
        }
    """
    # Extract recipient from headers (previously 'channel-id')
    recipient = headers.get("channel-id") if headers else None

    if not recipient:
        return False, "Missing 'channel-id' in headers for recipient"

    payload = {"recipient": recipient, "body": report_text}

    response = requests.post(webhook, json=payload)
    return response.ok, response.text
