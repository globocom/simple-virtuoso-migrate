# coding: utf-8
import unittest
import os
import tempfile
from mock import patch, Mock
from simple_virtuoso_migrate.config import FileConfig
from simple_virtuoso_migrate.core import SimpleVirtuosoMigrate
from tests import create_config, Struct, BaseTest

class SimpleVirtuosoMigrateTest(BaseTest):

    def setUp(self):
        super(SimpleVirtuosoMigrateTest, self).setUp()
        self.config = create_config(migrations_dir='.')

    def test_it_should_use_migrations_dir_from_configuration(self):
        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertEqual(self.config.get("database_migrations_dir"), virtuoso_migrate._migrations_dir)

    @patch('simple_virtuoso_migrate.core.Repo')
    def test_it_should_get_all_migrations_in_dir(self, repo_mock):
        repo_mock.return_value = Mock(**{"tags":[Struct(**{"name":"1"}), Struct(**{"name":"3"}), Struct(**{"name":"2.2"})]})

        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        migrations = virtuoso_migrate.get_all_migrations()
        self.assertNotEqual(None, migrations)
        self.assertEqual(["1", "3", "2.2"], migrations)

    @patch('simple_virtuoso_migrate.core.Repo')
    def test_it_should_not_read_files_again_on_subsequent_calls(self, repo_mock):
        repo_mock.return_value = Mock(**{"tags":[Struct(**{"name":"1"}), Struct(**{"name":"3"}), Struct(**{"name":"2.2"})]})

        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        virtuoso_migrate.get_all_migrations()
        self.assertEqual(1, repo_mock.call_count)

        #make the second call
        virtuoso_migrate.get_all_migrations()
        self.assertEqual(1, repo_mock.call_count)

    def test_it_should_raise_error_if_has_an_invalid_dir_on_migrations_dir(self):
        self.config.update("database_migrations_dir", FileConfig._parse_migrations_dir('invalid_path_it_does_not_exist')[0])
        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertRaisesWithMessage(Exception, "directory not found ('%s')" % os.path.abspath('invalid_path_it_does_not_exist'), virtuoso_migrate.get_all_migrations)

    def test_it_should_raise_error_if_migrations_dir_is_not_a_git_repository(self):
        self.config.update("database_migrations_dir", tempfile.gettempdir())
        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertRaisesWithMessage(Exception, "invalid git repository ('%s')" % tempfile.gettempdir(), virtuoso_migrate.get_all_migrations)

    @patch('simple_virtuoso_migrate.core.Repo')
    def test_it_should_raise_error_if_do_not_have_any_valid_migration(self, repo_mock):
        repo_mock.return_value = Mock(**{"tags":[]})
        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertRaisesWithMessage(Exception, "no migration found", virtuoso_migrate.get_all_migrations)

    @patch('simple_virtuoso_migrate.core.SimpleVirtuosoMigrate.get_all_migrations', return_value=['1', '3', '2.2'])
    def test_it_should_use_get_all_migrations_versions_method_to_check_if_migration_version_exists(self, get_all_migrations_mock):
        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertTrue(virtuoso_migrate.check_if_version_exists('3'))
        self.assertEqual(1, get_all_migrations_mock.call_count)
        self.assertFalse(virtuoso_migrate.check_if_version_exists('4'))

    @patch('simple_virtuoso_migrate.core.Git')
    def test_it_should_get_the_latest_version_available(self, git_mock):
        execute_mock = Mock(**{'return_value':'2.2'})
        git_mock.return_value = Mock(**{'execute':execute_mock})

        virtuoso_migrate = SimpleVirtuosoMigrate(self.config)
        self.assertEqual('2.2', virtuoso_migrate.latest_version_available())

        git_mock.assert_called_with(self.config.get("database_migrations_dir"))
        execute_mock.assert_called_with(["git", "describe","--abbrev=0","--tags"])

if __name__ == '__main__':
    unittest.main()
