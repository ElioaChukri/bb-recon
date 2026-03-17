import logging
import os

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

BASE_TELEGRAM_URL = "https://api.telegram.org"

logger = logging.getLogger(__name__)

send_retry = retry(
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.RequestException)),
)


class TelegramBot:
    """
    Thin wrapper around the telegram bot API. Currently only allows sending a message
    """

    def __init__(self, token: str | None = None, chat_id: str | None = None):
        """
        :param token: telegram bot token. Defaults to OS variable TELEGRAM_BOT_TOKEN if unset
        :param chat_id: telegram chat id. Defaults to OS variable TELEGRAM_CHAT_ID if unset
        """

        self._token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    @send_retry
    def send_message(self, message: str) -> None:
        """
        Send a message to telegram bot
        :param message: message to send
        :return: None
        """
        url = f"{BASE_TELEGRAM_URL}/bot{self._token}/sendMessage"

        try:
            logger.debug("Sending message to telegram bot: %s", message)
            response = requests.get(url, params={"chat_id": self._chat_id, "text": message})
            if not response.ok:
                logger.warning("Telegram API error: %s %s", response.status_code, response.text)
        except requests.exceptions.RequestException as e:
            logger.debug("Failed to send message to telegram bot: %s", e)

            # We have to raise to allow tenacity to retry
            raise
        except Exception as e:
            logger.debug("Failed to send message to telegram bot: %s", e)
