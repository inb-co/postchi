import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from django.template import Context


__author__ = 'Apollo'
error_logger = logging.getLogger('error')


class BaseMail(object):
    template_name = None
    subject = ""

    def __init__(self, **kwargs):
        self.context = getattr(settings, "EMAIL_COMMON_CONTEXT", dict())
        self.context.update(kwargs)

    def get_subject(self):
        return "".join((getattr(settings, "EMAIL_SUBJECT_PREFIX", ""), self.subject, ))

    def get_template(self):
        return loader.get_template(self.template_name)

    def render(self):
        template = self.get_template()
        return template.render(Context(self.context))

    def send(self, *destinations):
        from_mail = getattr(settings, "EMAIL_HOST_USER")
        mail_body = self.render()
        for destination in destinations:
            try:
                email = EmailMessage(self.get_subject(), mail_body, from_mail, [destination])
                email.content_subtype = "html"
                email.send()
            except Exception as exp:
                error_logger.error("Mail sending failed with error : {}".format(str(exp)))

