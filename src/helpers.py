import logging
import smtplib, ssl
import uuid
from dataclasses import dataclass, field

from src import constants
from src.exceptions import ObjectAlreadyExists
from src.management import InstanceManagement

logger = logging.getLogger()


def send_email_data(message: str, recipients: list[str]):
    """Email sender function."""

    # TODO: Implement `aiosmtplib`

    recipients = [recipients] if isinstance(recipients, str) else recipients

    port = constants.EMAIL_PORT
    smtp_server = constants.EMAIL_SERVER
    sender_email = constants.SENDER_EMAIL
    password = constants.EMAIL_PASSWORD

    try:
        logger.info("The message has been sent successfully.")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipients, message)
    except smtplib.SMTPException as e:
        logger.error(f"{e.args} SMTP error")


@dataclass
class BaseModel:
    """Generic model top set id's  for all models"""

    id: str = field(init=False)

    def __post_init__(self):
        self.id = str(uuid.uuid4())
        _child_class = self.__class__

        if hasattr(_child_class, f"_{_child_class.__name__}__management_instance"):
            management_instance: InstanceManagement = getattr(
                _child_class, f"_{_child_class.__name__}__management_instance"
            )
            if hasattr(_child_class, f"_validate_{_child_class.__name__.lower()}"):
                method = getattr(
                    _child_class, f"_validate_{_child_class.__name__.lower()}"
                )
                try:
                    method(self)
                except Exception as e:
                    if isinstance(e, ValueError):
                        raise ObjectAlreadyExists
                    else:
                        raise e
            management_instance.set_instance(self)
