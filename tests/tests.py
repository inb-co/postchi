from unittest import mock


# Create your tests here.
from django.core.exceptions import ImproperlyConfigured
from django.test.testcases import TestCase


# noinspection PyCallByClass,PyTypeChecker
class PostchiBackendTestCase(TestCase):
    @mock.patch("django.core.mail.backends.smtp.EmailBackend")
    @mock.patch("django.core.mail.EmailMessage")
    @mock.patch("logging.getLogger")
    def test_send_mail_function(self, logger, emailMessage, emailBackend):
        # Arrange
        from postchi.backend import _send_message as target
        email = emailMessage.return_value = mock.MagicMock()
        content_subtype = type(email).content_subtype = mock.PropertyMock()
        backend_instance = emailBackend.return_value = mock.MagicMock()
        params = {
            "EMAIL_HOST": "host",
            "EMAIL_HOST_USER": "user@email.com",
            "EMAIL_HOST_PASSWORD": "password",
            "EMAIL_PORT": "1234",
        }
        # Act
        target("to@mail.com", "subject", "body", "logger_name", **params)

        # Assert
        emailMessage.assert_called_once_with(body="body", subject="subject", to=("to@mail.com",))
        emailBackend.assert_called_once_with(host="host", password="password", port="1234", use_ssl=mock.ANY,
                                             use_tls=mock.ANY, username="user@email.com")
        backend_instance.send_messages.assert_called_once_with([mock.ANY])
        content_subtype.assert_called_once_with('html')

    # @mock.patch("")
    def test_backend_init_method_with_no_config(self, ):
        from postchi.backend import PostchiEmailBackend
        # Arrange
        with self.settings(POSTCHI={}):
            # Act
            instance = PostchiEmailBackend()

            # Assert
            self.assertEqual(instance.async, False)  # postchi send_type is sync by default

    @mock.patch("easy_job.get_runner")
    def test_backend_init_method_async_mode(self, get_runner):
        from postchi.backend import PostchiEmailBackend
        # Arrange
        configs = {
            'send_type': 'async',
            'easy_job_worker_name': 'postchi',
            'logger': 'mail_log'
        }
        with self.settings(POSTCHI=configs):
            # Act
            instance = PostchiEmailBackend()

            # Assert
            self.assertEqual(instance.async, True)  # postchi send_type is sync by default
            self.assertEqual(instance.logger_name, 'mail_log')
            get_runner.assert_called_once_with("postchi")

    @mock.patch("easy_job.get_runner")
    def test_backend_init_method_async_mode_without_worker_name(self, get_runner):
        from postchi.backend import PostchiEmailBackend
        # Arrange
        configs = {
            'send_type': 'async',
            # 'poseidon_worker_name': 'postchi',
            'logger': 'mail_log'
        }
        with self.settings(POSTCHI=configs):
            # Act and Assert
            with self.assertRaises(ImproperlyConfigured):
                instance = PostchiEmailBackend()

    def test_backend_send_messages(self):
        from postchi.backend import PostchiEmailBackend
        # Arrange
        instance = mock.MagicMock()
        # Act
        PostchiEmailBackend.send_messages(instance, [mock.MagicMock()])
        # Assert
        instance._send_message.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY, mock.ANY)
        instance._log.assert_has_calls([mock.call(10, mock.ANY), mock.call(10, mock.ANY)])  # 10=logging.DEBUG
