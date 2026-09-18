from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> None: ...


class PushProvider(ABC):
    @abstractmethod
    def send_push(self, user_id: str, title: str, body: str, url: str) -> None: ...
