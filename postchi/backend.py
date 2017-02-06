from datetime import datetime
import traceback
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

__author__ = 'Apollo'


def _send_message(to, subject, body, logger_name, **params):
    from django.core.mail.backends.smtp import EmailBackend
    from django.core.mail import EmailMessage
    try:
        if type(to) not in ('list', 'tuple'):
            to = (to, )
        email = EmailMessage(to=to, body=body, subject=subject)
        email.content_subtype = "html"
        EmailBackend(
            host=params['EMAIL_HOST'],
            username=params['EMAIL_HOST_USER'],
            password=params['EMAIL_HOST_PASSWORD'],
            use_ssl=False,
            use_tls=False,
            port=params['EMAIL_PORT']
        ).send_messages([email])
        return "Mail Sent to {}".format(to)
    except Exception as exp:
        if logger_name is not None:
            logging.getLogger(logger_name).error(
                "Error sending mail in postchi : {}\n{}".format(exp, traceback.format_exc()))
        return "Error sending email : {}".format(exp)


class PostchiEmailBackend(BaseEmailBackend):
    """
    Email backend which enqueue emails in a queue
    """

    def __init__(self, *args, **kwargs):
        super(PostchiEmailBackend, self).__init__(*args, **kwargs)
        configs = getattr(settings, "POSTCHI", {})
        send_type = configs.get("send_type", "sync").lower()
        if send_type not in ("sync", "async"):
            raise ImproperlyConfigured("error in POSTCHI_CONFIGURATIONS, send_type could be sync or async")
        self.async = send_type == "async"
        if self.async:
            runner_name = configs.get("easy_job_worker_name", None)
            if runner_name is None:
                raise ImproperlyConfigured(
                    "error in POSTCHI_CONFIGURATIONS, send_type is async but no EASY_JOB_WORKER_NAME has been specifed")
            import easy_job as easy_job
            self.runner = easy_job.get_runner(runner_name)
        self.logger_name = configs.get("logger", None)

    def _log(self, level, message, exception=None, include_traceback=True):
        logging.getLogger(self.logger_name).log(
            level,
            "{} {} \n{}".format(
                message,
                exception or "",
                traceback.format_exc() if include_traceback else ""
            )
        )

    def _get_smtp_connection_parameters(self):
        keys = [x for x in dir(settings) if x.startswith('EMAIL')]
        return {key: getattr(settings, key) for key in keys}

    def _send_message(self, to, subject, body, logger_name=None, **params):
        if self.async:
            self.runner.run(
                "postchi.backend._send_message",
                args=(to, subject, body, logger_name),
                kwargs=params
            )
        else:
            _send_message(to, subject, body, **params)

    def send_messages(self, email_messages):
        before = datetime.now()
        try:
            for email_message in email_messages:
                self._send_message(
                    email_message.to,
                    email_message.subject,
                    email_message.body,
                    self.logger_name,
                    **self._get_smtp_connection_parameters()
                )
                self._log(logging.DEBUG,
                          "Enqueue email : {} -> {} at {}".format(
                              email_message.subject,
                              email_message.to,
                              datetime.now()
                          ))
            after = datetime.now()
            total_time = (after - before).total_seconds()
            self._log(logging.DEBUG, "{} email sent in {} seconds\n===\n".format(len(email_messages), total_time))

        except Exception as exp:
            self._log(logging.ERROR, "error while sending messages  : {}\n{}".format(exp, traceback.format_exc()))
