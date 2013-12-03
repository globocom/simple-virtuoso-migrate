import unittest
from mock import patch, call, Mock
from simple_virtuoso_migrate.main import Main
from simple_virtuoso_migrate.config import Config
from tests import BaseTest, create_file, delete_files


class MainTest(BaseTest):
    def setUp(self):
        super(MainTest, self).setUp()
        self.initial_config = {
            'database_host': 'localhost',
            'database_port': 'port',
            'database_endpoint': 'test',
            'database_user': 'user',
            'database_password': 'password',
            'database_migrations_dir': '.',
            'database_graph': 'graph',
            'database_ontology': 'ontology.ttl',
            'host_user': 'host-user',
            'host_password': 'host-passwd',
            'file_migration': None,
            'migration_graph': 'http://example.com',
            'show_sparql_only': None,
            'virtuoso_dirs_allowed': '/tmp'
        }

        create_file("ontology.ttl", "content")
        create_file("new_triple.ttl")

    def tearDown(self):
        super(MainTest, self).tearDown()
        delete_files("ontology.ttl")
        delete_files("new_triple.ttl")

    def test_it_should_raise_error_if_a_required_config_to_migrate_is_missing(self):
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_host')",
                                     Main,
                                     Config())
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_endpoint')",
                                     Main,
                                     Config({'database_host': ''}))
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_user')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': ''}))
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_password')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': ''}))

        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_migrations_dir')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': '',
                                             'database_password': ''}))
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_port')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': '',
                                             'database_password': '',
                                             'database_migrations_dir': ''}))
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_graph')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': '',
                                             'database_password': '',
                                             'database_migrations_dir': '',
                                             'database_port': ''}))
        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('database_ontology')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': '',
                                             'database_password': '',
                                             'database_migrations_dir': '',
                                             'database_port': '',
                                             'database_graph': ''}))

        self.assertRaisesWithMessage(Exception,
                                     "invalid key ('migration_graph')",
                                     Main,
                                     Config({'database_host': '',
                                             'database_endpoint': '',
                                             'database_user': '',
                                             'database_password': '',
                                             'database_migrations_dir': '',
                                             'database_port': '',
                                             'database_graph': '',
                                             'database_ontology': ''}))


    @patch('sys.version_info', return_value=(2, 5, 2, 'final', 0))
    def test_detect_invalid_python_version(self, mock_sys_version_info):
        self.assertFalse(Main._valid_version())

    @patch('sys.version_info', return_value=(2, 5, 2, 'final', 0))
    def test_exit_if_invalid_python_version(self, mock_sys_version_info):
        self.assertFalse(Main._valid_version())
        self.assertRaises(SystemExit, Main, None)

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate')
    @patch('simple_virtuoso_migrate.main.LOG')
    @patch('simple_virtuoso_migrate.main.CLI')
    def test_it_should_use_the_other_utilities_classes(self, cli_mock, log_mock, simplevirtuosomigrate_mock):
        config = Config(self.initial_config)
        Main(config)
        log_mock.assert_called_with(None)
        simplevirtuosomigrate_mock.assert_called_with(config)

    @patch('simple_virtuoso_migrate.main.LOG')
    def test_it_should_use_log_dir_from_config(self, log_mock):
        self.initial_config.update({'log_dir': '.',
                                    "database_migrations_dir": '.'})
        Main(Config(self.initial_config))
        log_mock.assert_called_with('.')

    @patch('simple_virtuoso_migrate.main.Virtuoso')
    def test_it_should_use_virtuoso_class(self, virtuoso_mock):
        self.initial_config.update({'log_dir': '.',
                                    "database_migrations_dir": '.'})
        config = Config(self.initial_config)
        Main(config)
        virtuoso_mock.assert_called_with(config)

    def test_it_should_raise_error_if_config_is_not_an_instance_of_simple_virtuoso_migrate_config(self):
        self.assertRaisesWithMessage(Exception,
                                     "config must be an instance of simple_virtuoso_migrate.config.Config",
                                     Main,
                                     config={})

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Main._run_after')
    @patch('simple_virtuoso_migrate.main.Main._load_triples')
    def test_it_should_call_run_after_method_after_calling_execute(self, load_triples_mock, run_after_mock, execution_log_mock):
        self.initial_config.update({'load_ttl':'', 'run_after': 'some_script_name'})
        main = Main(Config(self.initial_config))
        main.execute()
        self.assertEqual(execution_log_mock.call_count, 3)
        run_after_mock.assert_called_with('some_script_name')

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Main._load_triples')
    @patch('simple_virtuoso_migrate.main.Main._valid_version')
    def test_should_exec_and_call_run_after_script(self, valid_version_mock, load_triples_mock, execution_log_mock):
        self.initial_config.update({'load_ttl':'', 'run_after': 'tests/plugin/validate_run_after.py'})
        main = Main(Config(self.initial_config))
        main.execute()
        self.assertEqual(valid_version_mock.call_count, 2)

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Main._load_triples')
    def test_should_exec_and_fail_with_invalid_after_script(self, load_triples_mock, execution_log_mock):
        self.initial_config.update({'load_ttl':'', 'run_after': 'tests/plugin/invalid_run_after.py'})
        main = Main(Config(self.initial_config))
        main.execute()
        execution_log_mock.mock_calls[-2].called_with('\nRun after script tests/plugin/invalid_run_after.py does not have run_after() function .\n', 'PINK', 1)

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Virtuoso.execute_change')
    @patch('simple_virtuoso_migrate.main.Virtuoso.get_current_version', return_value=(None, None))
    @patch('simple_virtuoso_migrate.main.Virtuoso._run_isql', return_value=("", ""))
    def test_it_should_add_triples_if_the_database_is_empty_and_the_option_is_activated_by_the_user(self, run_isql_mock, current_version_mock, execute_change_mock, _execution_log_mock):
        self.initial_config.update({'load_ttl':'new_triple.ttl', 'show_sparql_only':None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call("- TTL(s) to upload: ['new_triple.ttl']", 'GREEN', log_level_limit=1),
            call('- Current version is: None', 'GREEN', log_level_limit=1),
            call('- Destination version is: None', 'GREEN', log_level_limit=1),
            call('\nStarting Migration!', log_level_limit=1),
            call('===== executing =====', log_level_limit=1),
            call('', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
#        execute_change_mock.assert_called_with('sparql_up', 'sparql_down', execution_log=_execution_log_mock)

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Virtuoso.execute_change')
    @patch('simple_virtuoso_migrate.main.Virtuoso.get_current_version', return_value=('0.1', 'git'))
    @patch('simple_virtuoso_migrate.main.Virtuoso._run_isql', return_value=("", ""))
    def test_it_should_add_triples_if_the_database_is_not_empty_and_the_option_is_activated_by_the_user(self, run_isql_mock, current_version_mock, execute_change_mock, _execution_log_mock):
        self.initial_config.update({'load_ttl':'new_triple.ttl', 'show_sparql_only':None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call("- TTL(s) to upload: ['new_triple.ttl']", 'GREEN', log_level_limit=1),
            call('- Current version is: 0.1', 'GREEN', log_level_limit=1),
            call('- Destination version is: 0.1', 'GREEN', log_level_limit=1),
            call('\nStarting Migration!', log_level_limit=1),
            call('===== executing =====', log_level_limit=1),
            call('', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
#        execute_change_mock.assert_called_with('sparql_up', 'sparql_down', execution_log=_execution_log_mock)

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Virtuoso.execute_change')
    @patch('simple_virtuoso_migrate.main.Virtuoso.get_current_version', return_value=('0.1', 'git'))
    def test_it_should_not_add_triples_if_show_sparql_only_option_is_activated_by_the_user(self, current_version_mock, execute_change_mock, _execution_log_mock):
        self.initial_config.update({'load_ttl':'new_triple.ttl', 'show_sparql_only':True})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call("- TTL(s) to upload: ['new_triple.ttl']", 'GREEN', log_level_limit=1),
#            call('- Current version is: 0.1', 'GREEN', log_level_limit=1),
#            call('- Destination version is: 0.1', 'GREEN', log_level_limit=1),
#            call("\nWARNING: commands are not being executed ('--show_sparql_only' activated)", 'RED', log_level_limit=1),
#            call('__________ SPARQL statements executed __________', 'YELLOW', log_level_limit=1),
#            call('sparql_up', 'YELLOW', log_level_limit=1),
#            call('_____________________________________________', 'YELLOW', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        self.assertEqual(0, execute_change_mock.call_count)

    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.Main._migrate')
    def test_it_should_migrate_db_if_create_migration_option_is_not_activated_by_user(self, migrate_mock, _execution_log_mock):
        config = Config(self.initial_config)
        main = Main(config)
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        self.assertEqual(1, migrate_mock.call_count)

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate')
    @patch('simple_virtuoso_migrate.main.LOG.debug')
    @patch('simple_virtuoso_migrate.main.CLI')
    def test_it_should_write_the_message_to_log(self, cli_mock, log_mock, simplevirtuosomigrate_mock):
        main = Main(config=Config(self.initial_config))
        main._execution_log('message to log')

        log_mock.assert_called_with('message to log')

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate')
    @patch('simple_virtuoso_migrate.main.LOG')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_write_the_message_to_cli(self, cli_mock, log_mock, simplevirtuosomigrate_mock):
        main = Main(config=Config(self.initial_config))
        main._execution_log('message to log', color='RED', log_level_limit=1)

        cli_mock.assert_called_with('message to log', 'RED')

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate')
    @patch('simple_virtuoso_migrate.main.LOG')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_write_the_message_to_cli_using_default_color(self, cli_mock, log_mock, simplevirtuosomigrate_mock):
        self.initial_config.update({'log_level': 3})
        main = Main(config=Config(self.initial_config))
        main._execution_log('message to log')

        cli_mock.assert_called_with('message to log', 'CYAN')

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Main._get_destination_version', return_value='destination_version')
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':('current_version', 'git'), 'get_sparql.return_value':('sparql_up', 'sparql_down')}))
    def test_it_should_get_current_and_destination_versions_and_execute_migrations(self, virtuoso_mock, _get_destination_version_mock, execute_migrations_mock):
        main = Main(Config(self.initial_config))
        main.execute()
        execute_migrations_mock.assert_called_with('sparql_up', 'sparql_down', 'current_version', 'destination_version')

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate', return_value=Mock(**{'check_if_version_exists.return_value':True}))
    def test_it_should_get_destination_version_when_user_informs_a_specific_version(self, simplevirtuosomigrate_mock):
        self.initial_config.update({"schema_version": "20090214115300"})
        main = Main(Config(self.initial_config))
        self.assertEqual("20090214115300", main._get_destination_version())
        main.virtuoso_migrate.check_if_version_exists.assert_called_with('20090214115300')
        self.assertEqual(1, main.virtuoso_migrate.check_if_version_exists.call_count)

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate', return_value=Mock(**{'latest_version_available.return_value':'latest_version_available'}))
    def test_it_should_get_destination_version_when_user_does_not_inform_a_specific_version(self, simplevirtuosomigrate_mock):
        self.initial_config.update({"schema_version": None})
        main = Main(Config(self.initial_config))
        self.assertEqual("latest_version_available", main._get_destination_version())

    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate', return_value=Mock(**{'check_if_version_exists.return_value':False}))
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':('current_version', 'git')}))
    def test_it_should_raise_exception_when_get_destination_version_and_version_does_not_exist_on_migrations_dir(self, virtuoso_mock, simplevirtuosomigrate_mock):
        self.initial_config.update({"schema_version": "20090214115900"})
        main = Main(Config(self.initial_config))
        self.assertRaisesWithMessage(Exception,
                                     'version not found (20090214115900)',
                                     main.execute)
        main.virtuoso_migrate.check_if_version_exists.assert_called_with('20090214115900')
        self.assertEqual(1, main.virtuoso_migrate.check_if_version_exists.call_count)

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':('current_version', 'git'), 'get_sparql.return_value':('sparql_up', 'sparql_down')}))
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_accept_file_migration_option_instead_a_schema_version(self, cli_mock, _execution_log_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"file_migration":"migration", "schema_version":None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        execute_migrations_mock.assert_called_with('sparql_up', 'sparql_down', 'current_version', 'migration')

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso.get_current_version', return_value=(None, None))
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_not_accept_file_migration_option_for_first_database_migration(self, cli_mock, _execution_log_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"file_migration":"migration"})
        main = Main(Config(self.initial_config))
        try:
            main.execute()
        except SystemExit:
            pass

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('- Current version is: None', 'GREEN', log_level_limit=1),
            call('- Destination version is: migration', 'GREEN', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        cli_mock.assert_called_with("[ERROR] Can't execute migration FROM None TO File (TIP: version it using git --tag and then use -m)\n", 'RED')
        self.assertEqual(0, execute_migrations_mock.call_count)

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso.get_current_version', return_value=('current_file', 'file'))
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_not_accept_file_migration_option_if_current_version_is_already_a_file(self, cli_mock, _execution_log_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"file_migration":"migration"})
        main = Main(Config(self.initial_config))
        try:
            main.execute()
        except SystemExit:
            pass

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('- Current version is: current_file', 'GREEN', log_level_limit=1),
            call('- Destination version is: migration', 'GREEN', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        cli_mock.assert_called_with("[ERROR] Can't execute migration FROM File TO File (TIP: version it using git --tag and then use -m)\n", 'RED')
        self.assertEqual(0, execute_migrations_mock.call_count)

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':('current_version', 'git'), 'get_sparql.return_value':('sparql_up', 'sparql_down')}))
    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate.check_if_version_exists', return_value=True)
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_accept_a_schema_version_option_instead_file_migration(self, cli_mock, _execution_log_mock, simplevirtuosomigrate_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"schema_version": "version",
                                    "file_migration": None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK',
                 log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        execute_migrations_mock.assert_called_with('sparql_up', 'sparql_down',
                                                   'current_version',
                                                   'version')

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':(None, None), 'get_sparql.return_value':('sparql_up', 'sparql_down')}))
    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate.check_if_version_exists', return_value=True)
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_accept_a_schema_version_option_for_first_database_migration(self, cli_mock, _execution_log_mock, simplevirtuosomigrate_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"schema_version": "version",
                                    "file_migration": None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        execute_migrations_mock.assert_called_with('sparql_up', 'sparql_down', None, 'version')

    @patch('simple_virtuoso_migrate.main.Main._execute_migrations')
    @patch('simple_virtuoso_migrate.main.Virtuoso', return_value=Mock(**{'get_current_version.return_value':('current_file', 'file'), 'get_sparql.return_value':('sparql_up', 'sparql_down')}))
    @patch('simple_virtuoso_migrate.main.SimpleVirtuosoMigrate.check_if_version_exists', return_value=True)
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    @patch('simple_virtuoso_migrate.main.CLI.msg')
    def test_it_should_accept_a_schema_version_option_if_current_version_is_a_file(self, cli_mock, _execution_log_mock, simplevirtuosomigrate_mock, virtuoso_mock, execute_migrations_mock):
        self.initial_config.update({"schema_version":"version", "file_migration":None})
        main = Main(Config(self.initial_config))
        main.execute()

        expected_calls = [
            call('\nStarting Virtuoso migration...', 'PINK', log_level_limit=1),
            call('\nDone.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        execute_migrations_mock.assert_called_with('sparql_up', 'sparql_down', 'current_file', 'version')

    @patch('simple_virtuoso_migrate.main.Virtuoso')
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    def test_it_should_use_virtuoso_class_to_get_migration_and_execute_changes(self, _execution_log_mock, virtuoso_mock):
        main = Main(Config(self.initial_config))
        main._execute_migrations("sparql_up line 1\nsparql_up line 2\nsparql_up line 3", "sparql_down line 1\nsparql_down line 2\nsparql_down line 3", "current_version", "destination_version")
        expected_calls = [
            call('- Current version is: current_version', 'GREEN', log_level_limit=1),
            call('- Destination version is: destination_version', 'GREEN', log_level_limit=1),
            call('\nStarting Migration!', log_level_limit=1),
            call('===== executing =====', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        main.virtuoso.execute_change.assert_called_with("sparql_up line 1\nsparql_up line 2\nsparql_up line 3", "sparql_down line 1\nsparql_down line 2\nsparql_down line 3", execution_log=_execution_log_mock)

    @patch('simple_virtuoso_migrate.main.Virtuoso')
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    def test_it_should_log_executed_sparql_if_asked_to_show_sparql(self, _execution_log_mock, virtuoso_mock):
        self.initial_config.update({"show_sparql":True})
        main = Main(Config(self.initial_config))
        main._execute_migrations("sparql_up line 1\nsparql_up line 2\nsparql_up line 3", "sparql_down line 1\nsparql_down line 2\nsparql_down line 3", "current_version", "destination_version")
        expected_calls = [
            call('- Current version is: current_version', 'GREEN', log_level_limit=1),
            call('- Destination version is: destination_version', 'GREEN', log_level_limit=1),
            call('\nStarting Migration!', log_level_limit=1),
            call('===== executing =====', log_level_limit=1),
            call('__________ SPARQL statements executed __________', 'YELLOW', log_level_limit=1),
            call('sparql_up line 1\nsparql_up line 2\nsparql_up line 3', 'YELLOW', log_level_limit=1),
            call('_____________________________________________', 'YELLOW', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)

    @patch('simple_virtuoso_migrate.main.Virtuoso')
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    def test_it_should_not_execute_any_sparql_if_asked_to_show_sparql_only(self, _execution_log_mock, virtuoso_mock):
        self.initial_config.update({"show_sparql_only":True})
        main = Main(Config(self.initial_config))
        main._execute_migrations("sparql_up line 1\nsparql_up line 2\nsparql_up line 3", "sparql_down line 1\nsparql_down line 2\nsparql_down line 3", "current_version", "destination_version")
        expected_calls = [
            call('- Current version is: current_version', 'GREEN', log_level_limit=1),
            call('- Destination version is: destination_version', 'GREEN', log_level_limit=1),
            call("\nWARNING: commands are not being executed ('--show_sparql_only' activated)", 'RED', log_level_limit=1),
            call('__________ SPARQL statements executed __________', 'YELLOW', log_level_limit=1),
            call('sparql_up line 1\nsparql_up line 2\nsparql_up line 3', 'YELLOW', log_level_limit=1),
            call('_____________________________________________', 'YELLOW', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        self.assertEqual(0, main.virtuoso.execute_change.call_count)

    @patch('simple_virtuoso_migrate.main.Virtuoso')
    @patch('simple_virtuoso_migrate.main.Main._execution_log')
    def test_it_should_do_nothing_if_sparql_up_has_two_lines(self, _execution_log_mock, virtuoso_mock):
        main = Main(Config(self.initial_config))
        main._execute_migrations("sparql_up line 1\nsparql_up line 2", "sparql_down line 1\nsparql_down line 2", "current_version", "destination_version")
        expected_calls = [
            call('- Current version is: current_version', 'GREEN', log_level_limit=1),
            call('- Destination version is: destination_version', 'GREEN', log_level_limit=1),
            call('\nStarting Migration!', log_level_limit=1),
            call('\nNothing to do.\n', 'PINK', log_level_limit=1)
        ]
        self.assertEqual(expected_calls, _execution_log_mock.mock_calls)
        self.assertEqual(0, main.virtuoso.execute_change.call_count)

if __name__ == "__main__":
    unittest.main()
