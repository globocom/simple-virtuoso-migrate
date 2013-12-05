import unittest
import simple_virtuoso_migrate
import os
import sys
from StringIO import StringIO
from mock import patch, Mock
from tests import create_file, delete_files
from simple_virtuoso_migrate import run


class RunTest(unittest.TestCase):

    def setUp(self):
        config_file = '''
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''
DATABASE_PORT = 'port'
DATABASE_ENDPOINT = 'migration_example'
DATABASE_GRAPH = 'graph'
DATABASE_ONTOLOGY = 'ontology'
ENV1_DATABASE_ENDPOINT = 'migration_example_env1'
DATABASE_MIGRATIONS_DIR = 'example'
DATABASE_ANY_CUSTOM_VARIABLE = 'Some Value'
SOME_ENV_DATABASE_ANY_CUSTOM_VARIABLE = 'Other Value'
DATABASE_OTHER_CUSTOM_VARIABLE = 'Value'
MIGRATION_GRAPH = 'migration_graph_example'
RUN_AFTER = './some_dummy_action.py'
'''
        create_file('sample.conf', config_file)

    def tearDown(self):
        delete_files('sample.conf')

    @patch('codecs.getwriter')
    @patch('sys.stdout', encoding='iso-8859-1')
    def test_it_should_ensure_stdout_is_using_an_utf8_encoding(self,
                                                               stdout_mock,
                                                               codecs_mock):
        new_stdout = Mock()
        codecs_mock.return_value = Mock(**{'return_value': new_stdout})

        reload(simple_virtuoso_migrate.run)

        codecs_mock.assert_called_with('utf-8')
        self.assertEqual(new_stdout, sys.stdout)

    def test_it_should_define_a_version_string(self):
        self.assertIsInstance(
                     simple_virtuoso_migrate.SIMPLE_VIRTUOSO_MIGRATE_VERSION,
                    str)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('simple_virtuoso_migrate.cli.CLI.parse')
    def test_it_should_use_cli_to_parse_arguments(self, parse_mock,
                                                  stdout_mock):
        parse_mock.return_value = (Mock(simple_virtuoso_migrate_version=True),
                                   [])
        try:
            run.run_from_argv()
        except SystemExit:
            pass

        self.assertEqual(1, parse_mock.call_count)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('simple_virtuoso_migrate.cli.CLI.parse')
    def test_it_should_show_help_when_no_args_is_given(self, parse_mock,
                                                       stdout_mock):
        parse_mock.return_value = (Mock(simple_virtuoso_migrate_version=True),
                                   [])
        try:
            run.run_from_argv(None)
        except SystemExit:
            pass

        parse_mock.assert_called_with(["-h"])

    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_print_simple_virtuoso_migrate_version_and_exit(self,
                                                                stdout_mock):
        try:
            run.run_from_argv(["-v"])
        except SystemExit, e:
            self.assertEqual(0, e.code)
        compiled = ('simple-virtuoso-migrate v%s\n\n' %\
                    simple_virtuoso_migrate.SIMPLE_VIRTUOSO_MIGRATE_VERSION)
        self.assertEqual(compiled, stdout_mock.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('simple_virtuoso_migrate.cli.CLI.show_colors')
    def test_it_should_activate_use_of_colors(self, show_colors_mock,
                                              stdout_mock):
        try:
            run.run_from_argv(["--color"])
        except SystemExit:
            pass

        self.assertEqual(1, show_colors_mock.call_count)

    @patch('simple_virtuoso_migrate.cli.CLI.show_colors')
    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_print_message_and_exit_when_user_interrupt_execution(self, stdout_mock, show_colors_mock):
        show_colors_mock.side_effect = KeyboardInterrupt()
        try:
            run.run_from_argv(["--color"])
        except SystemExit, e:
            self.assertEqual(0, e.code)

        self.assertEqual('\nExecution interrupted by user...\n\n', stdout_mock.getvalue())

    @patch('simple_virtuoso_migrate.cli.CLI.show_colors')
    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_print_message_and_exit_when_an_error_happen(self, stdout_mock, show_colors_mock):
        show_colors_mock.side_effect = Exception('occur an error')
        try:
            run.run_from_argv(["--color"])
        except SystemExit, e:
            self.assertEqual(1, e.code)

        self.assertEqual('[ERROR] occur an error\n\n', stdout_mock.getvalue())

    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__',
                  return_value=None)
    @patch.object(simple_virtuoso_migrate.helpers.Utils,
                  'get_variables_from_file',
                  return_value={'DATABASE_HOST':'host', 'DATABASE_USER': 'root', 'DATABASE_PASSWORD':'', 'DATABASE_PORT':'port', 'DATABASE_ENDPOINT':'database', 'DATABASE_MIGRATIONS_DIR':'.', 'DATABASE_GRAPH':'graph', 'DATABASE_ONTOLOGY':'ontology'})
    def test_it_should_read_configuration_file_using_fileconfig_class_and_execute_with_default_configuration(self, get_variables_from_file_mock, main_mock, execute_mock):
        run.run_from_argv(["-c", os.path.abspath('sample.conf')])

        get_variables_from_file_mock.assert_called_with(os.path.abspath('sample.conf'))

        self.assertEqual(1, execute_mock.call_count)
        execute_mock.assert_called_with()

        self.assertEqual(1, main_mock.call_count)
        config_used = main_mock.call_args[0][0]
        self.assertTrue(isinstance(config_used, simple_virtuoso_migrate.config.FileConfig))
        self.assertEqual('root', config_used.get('database_user'))
        self.assertEqual('', config_used.get('database_password'))
        self.assertEqual('database', config_used.get('database_endpoint'))
        self.assertEqual('host', config_used.get('database_host'))
        self.assertEqual('port', config_used.get('database_port'))
        self.assertEqual('graph', config_used.get('database_graph'))
        self.assertEqual('ontology', config_used.get('database_ontology'))
        self.assertEqual(os.path.abspath('.'), config_used.get("database_migrations_dir"))
        self.assertEqual(False, config_used.get('show_sparql'))
        self.assertEqual(False, config_used.get('show_sparql_only'))
        self.assertEqual(1, config_used.get('log_level'))

    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__', return_value=None)
    def test_it_should_get_configuration_exclusively_from_args_if_not_use_configuration_file_using_config_class_and_execute_with_default_configuration(self, main_mock, execute_mock):
        run.run_from_argv(['--db-port', 'port',
                           '--db-host', 'host',
                           '--db-endpoint', 'name',
                           '--db-user', 'user',
                           '--db-password', 'pass',
                           '--db-graph', 'graph',
                           '--db-ontology', 'ontology',
                           '--db-migrations-dir', '../migration:.:/tmp',
                           '--log-dir', '../',
                           '--run-after', 'some_dummy.py',
                           '--file', 'temp_ttl_file.ttl'])

        self.assertEqual(1, execute_mock.call_count)
        execute_mock.assert_called_with()

        self.assertEqual(1, main_mock.call_count)
        config_used = main_mock.call_args[0][0]
        self.assertIsInstance(config_used,
                              simple_virtuoso_migrate.config.Config)
        self.assertEqual('user', config_used.get('database_user'))
        self.assertEqual('pass', config_used.get('database_password'))
        self.assertEqual('name', config_used.get('database_endpoint'))
        self.assertEqual('host', config_used.get('database_host'))
        self.assertEqual('port', config_used.get('database_port'))
        self.assertEqual('graph', config_used.get('database_graph'))
        self.assertEqual('ontology', config_used.get('database_ontology'))
        self.assertEqual(os.path.abspath('../migration'),
                         config_used.get("database_migrations_dir"))
        self.assertEqual(False, config_used.get('show_sparql'))
        self.assertEqual(False, config_used.get('show_sparql_only'))
        self.assertEqual('../', config_used.get('log_dir'))
        self.assertEqual('temp_ttl_file.ttl',
                         config_used.get('file_migration'))
        self.assertEqual(1, config_used.get('log_level'))
        self.assertEqual('some_dummy.py', config_used.get('run_after'))

    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__', return_value=None)
    @patch.object(simple_virtuoso_migrate.helpers.Utils, 'get_variables_from_file', return_value = {'DATABASE_HOST':'host', 'DATABASE_USER': 'root', 'DATABASE_PASSWORD':'', 'DATABASE_NAME':'database', 'DATABASE_MIGRATIONS_DIR':'.'})
    def test_it_should_use_log_level_as_specified(self, import_file_mock, main_mock, execute_mock):
        run.run_from_argv(["-c", os.path.abspath('sample.conf'), '--log-level', 4])
        config_used = main_mock.call_args[0][0]
        self.assertEqual(4, config_used.get('log_level'))

    @patch('simple_virtuoso_migrate.run.getpass',
           return_value='password_asked')
    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__',
                  return_value=None)
    @patch.object(simple_virtuoso_migrate.helpers.Utils,
                  'get_variables_from_file',
                  return_value={'DATABASE_HOST': 'host',
                                'DATABASE_USER': 'root',
                                'DATABASE_PASSWORD': '<<ask_me>>',
                                'DATABASE_ENDPOINT': 'database',
                                'DATABASE_MIGRATIONS_DIR': '.'})
    def test_it_should_ask_for_password_when_configuration_is_as_ask_me(
                                                            self,
                                                            import_file_mock,
                                                            main_mock,
                                                            execute_mock,
                                                            stdout_mock,
                                                            getpass_mock):
        run.run_from_argv(["-c", os.path.abspath('sample.conf')])
        config_used = main_mock.call_args[0][0]
        self.assertEqual('password_asked',
                         config_used.get('database_password'))
        self.assertEqual('\nPlease inform password to connect to virtuoso (DATABASE) "root@host:database"\n',
                         stdout_mock.getvalue())

    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__', return_value=None)
    @patch.object(simple_virtuoso_migrate.helpers.Utils, 'get_variables_from_file', return_value = {'DATABASE_HOST':'host', 'DATABASE_USER': 'root', 'DATABASE_PASSWORD':'<<ask_me>>', 'DATABASE_ENDPOINT':'database', 'DATABASE_MIGRATIONS_DIR':'.'})
    def test_it_should_use_password_from_command_line_when_configuration_is_as_ask_me(self, import_file_mock, main_mock, execute_mock):
        run.run_from_argv(["-c", os.path.abspath('sample.conf'), '--db-password', 'xpto_pass'])
        config_used = main_mock.call_args[0][0]
        self.assertEqual('xpto_pass', config_used.get('database_password'))

    @patch.object(simple_virtuoso_migrate.main.Main, 'execute')
    @patch.object(simple_virtuoso_migrate.main.Main, '__init__', return_value=None)
    @patch.object(simple_virtuoso_migrate.helpers.Utils, 'get_variables_from_file', return_value = {'schema_version':'version', 'DATABASE_HOST':'host', 'DATABASE_USER': 'root', 'DATABASE_PASSWORD':'', 'DATABASE_ENDPOINT':'database', 'DATABASE_MIGRATIONS_DIR':'.'})
    def test_it_should_use_values_from_config_file_in_replacement_for_command_line(self, import_file_mock, main_mock, execute_mock):
        run.run_from_argv(["-c", os.path.abspath('sample.conf')])
        config_used = main_mock.call_args[0][0]
        self.assertEqual('version', config_used.get('schema_version'))

if __name__ == '__main__':
    unittest.main()
