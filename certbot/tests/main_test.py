"""Tests for certbot.main."""
import shutil
import tempfile
import unittest

import mock

from certbot import cli
from certbot import configuration
from certbot import errors
from certbot.plugins import disco as plugins_disco


class ObtainCertTest(unittest.TestCase):
    """Tests for certbot.main.obtain_cert."""

    def setUp(self):
        self.get_utility_patch = mock.patch(
            'certbot.main.zope.component.getUtility')
        self.mock_get_utility = self.get_utility_patch.start()

    def tearDown(self):
        self.get_utility_patch.stop()

    def _call(self, args):
        plugins = plugins_disco.PluginsRegistry.find_all()
        config = configuration.NamespaceConfig(
            cli.prepare_and_parse_args(plugins, args))

        from certbot import main
        with mock.patch('certbot.main._init_le_client') as mock_init:
            main.obtain_cert(config, plugins)

        return mock_init()  # returns the client

    @mock.patch('certbot.main._auth_from_domains')
    def test_no_reinstall_text_pause(self, mock_auth):
        mock_notification = self.mock_get_utility().notification
        mock_notification.side_effect = self._assert_no_pause
        mock_auth.return_value = (mock.ANY, 'reinstall')
        self._call('certonly --webroot -d example.com -t'.split())

    def _assert_no_pause(self, message, height=42, pause=True):
        # pylint: disable=unused-argument
        self.assertFalse(pause)


class SetupLogFileHandlerTest(unittest.TestCase):
    """Tests for certbot.main.setup_log_file_handler."""

    def setUp(self):
        self.config = mock.Mock(spec_set=['logs_dir'],
                                logs_dir=tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.config.logs_dir)

    def _call(self, *args, **kwargs):
        from certbot.main import setup_log_file_handler
        return setup_log_file_handler(*args, **kwargs)

    @mock.patch('certbot.main.logging.handlers.RotatingFileHandler')
    def test_ioerror(self, mock_handler):
        mock_handler.side_effect = IOError
        self.assertRaises(errors.Error, self._call,
                          self.config, "test.log", "%s")


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
