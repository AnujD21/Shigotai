import smtplib

from app.notifications.smtp_provider import SMTPEmailProvider


class _FakeSMTP:
    instances: list["_FakeSMTP"] = []

    def __init__(self, host, port, timeout):
        self.login_args = None
        self.sent = []
        _FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.sent.append(message)


def test_gmail_app_password_spaces_are_removed(monkeypatch):
    _FakeSMTP.instances.clear()
    monkeypatch.setattr(smtplib, "SMTP", _FakeSMTP)
    provider = SMTPEmailProvider("smtp.gmail.com", 587, "me@gmail.com", "abcd efgh ijkl mnop", "me@gmail.com")

    provider.send_email("user@example.com", "Hello", "<p>Hi</p>", "Hi")

    [server] = _FakeSMTP.instances
    assert server.login_args == ("me@gmail.com", "abcdefghijklmnop")
    assert server.sent[0]["To"] == "user@example.com"


def test_smtp_failure_does_not_raise(monkeypatch):
    class _Broken(_FakeSMTP):
        def login(self, username, password):
            raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(smtplib, "SMTP", _Broken)
    provider = SMTPEmailProvider("smtp.gmail.com", 587, "me@gmail.com", "wrong", "me@gmail.com")

    provider.send_email("user@example.com", "Hello", "<p>Hi</p>", "Hi")  # logged, not raised
