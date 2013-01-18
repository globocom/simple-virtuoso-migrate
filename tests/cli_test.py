from StringIO import StringIO
from mock import patch
from simple_virtuoso_migrate.cli import CLI
import unittest

class CLITest(unittest.TestCase):

    def setUp(self):
        self.color = CLI.color

    def tearDown(self):
        CLI.color = self.color

    def test_it_should_define_colors_values_as_empty_strings_by_default(self):
        self.assertEqual("", CLI.color["PINK"])
        self.assertEqual("", CLI.color["BLUE"])
        self.assertEqual("", CLI.color["CYAN"])
        self.assertEqual("", CLI.color["GREEN"])
        self.assertEqual("", CLI.color["YELLOW"])
        self.assertEqual("", CLI.color["RED"])
        self.assertEqual("", CLI.color["END"])

    def test_it_should_define_colors_values_when_asked_to_show_collors(self):
        CLI.show_colors()
        self.assertEqual("\033[35m", CLI.color["PINK"])
        self.assertEqual("\033[34m", CLI.color["BLUE"])
        self.assertEqual("\033[36m", CLI.color["CYAN"])
        self.assertEqual("\033[32m", CLI.color["GREEN"])
        self.assertEqual("\033[33m", CLI.color["YELLOW"])
        self.assertEqual("\033[31m", CLI.color["RED"])
        self.assertEqual("\033[0m", CLI.color["END"])

    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_exit_with_help_options(self, stdout_mock):
        try:
            CLI.parse(["-h"])
        except SystemExit, e:
            self.assertEqual(0, e.code)
            self.assertTrue(stdout_mock.getvalue().find("Displays simple-virtuoso-migrate's version and exit") > 0)

        stdout_mock.buf = ''
        try:
            CLI.parse(["--help"])
        except SystemExit, e:
            self.assertEqual(0, e.code)
            self.assertTrue(stdout_mock.getvalue().find("Displays simple-virtuoso-migrate's version and exit") > 0)

    def test_it_should_not_has_a_default_value_for_configuration_file(self):
        self.assertEqual(None, CLI.parse([])[0].config_file)

    def test_it_should_accept_configuration_file_options(self):
        self.assertEqual("file.conf", CLI.parse(["-c", "file.conf"])[0].config_file)
        self.assertEqual("file.conf", CLI.parse(["--config", "file.conf"])[0].config_file)

    def test_it_should_has_a_default_value_for_log_level(self):
        self.assertEqual(1, CLI.parse([])[0].log_level)

    def test_it_should_accept_log_level_options(self):
        self.assertEqual("log_level_value", CLI.parse(["-l", "log_level_value"])[0].log_level)
        self.assertEqual("log_level_value", CLI.parse(["--log-level", "log_level_value"])[0].log_level)

    def test_it_should_not_has_a_default_value_for_log_dir(self):
        self.assertEqual(None, CLI.parse([])[0].log_dir)

    def test_it_should_accept_log_dir_options(self):
        self.assertEqual("log_dir_value", CLI.parse(["--log-dir", "log_dir_value"])[0].log_dir)

    def test_it_should_not_has_a_default_value_for_schema_version(self):
        self.assertEqual(None, CLI.parse([])[0].schema_version)

    def test_it_should_accept_schema_version_options(self):
        self.assertEqual("schema_version_value", CLI.parse(["-g", "schema_version_value"])[0].schema_version)
        self.assertEqual("schema_version_value", CLI.parse(["--git", "schema_version_value"])[0].schema_version)

    def test_it_should_not_has_a_default_value_for_file_migration(self):
        self.assertEqual(None, CLI.parse([])[0].file_migration)

    def test_it_should_accept_file_migration_options(self):
        self.assertEqual("file_migration_value", CLI.parse(["-f", "file_migration_value"])[0].file_migration)
        self.assertEqual("file_migration_value", CLI.parse(["--file", "file_migration_value"])[0].file_migration)

    def test_it_should_not_has_a_default_value_for_add_ttl(self):
        self.assertEqual(None, CLI.parse([])[0].add_ttl)

    def test_it_should_accept_add_ttl_options(self):
        self.assertEqual("add_ttl_value", CLI.parse(["-i", "add_ttl_value"])[0].add_ttl)
        self.assertEqual("add_ttl_value", CLI.parse(["--insert", "add_ttl_value"])[0].add_ttl)

    def test_it_should_has_a_default_value_for_simple_virtuoso_migrate_version(self):
        self.assertEqual(False, CLI.parse([])[0].simple_virtuoso_migrate_version)

    def test_it_should_accept_simple_virtuoso_migrate_version_options(self):
        self.assertEqual(True, CLI.parse(["-v"])[0].simple_virtuoso_migrate_version)
        self.assertEqual(True, CLI.parse(["--version"])[0].simple_virtuoso_migrate_version)

    def test_it_should_has_a_default_value_for_show_colors(self):
        self.assertEqual(False, CLI.parse([])[0].show_colors)

    def test_it_should_accept_show_colors_options(self):
        self.assertEqual(True, CLI.parse(["--color"])[0].show_colors)

    def test_it_should_has_a_default_value_for_show_sparql(self):
        self.assertEqual(False, CLI.parse([])[0].show_sparql)

    def test_it_should_accept_show_sparql_options(self):
        self.assertEqual(True, CLI.parse(["--showsparql"])[0].show_sparql)

    def test_it_should_has_a_default_value_for_show_sparql_only(self):
        self.assertEqual(False, CLI.parse([])[0].show_sparql_only)

    def test_it_should_accept_show_sparql_only_options(self):
        self.assertEqual(True, CLI.parse(["--showsparqlonly"])[0].show_sparql_only)

    def test_it_should_has_a_default_value_for_environment(self):
        self.assertEqual("", CLI.parse([])[0].environment)

    def test_it_should_accept_environment_options(self):
        self.assertEqual("environment_value", CLI.parse(["--env", "environment_value"])[0].environment)
        self.assertEqual("environment_value", CLI.parse(["--environment", "environment_value"])[0].environment)

    def test_it_should_not_has_a_default_value_for_database_user(self):
        self.assertEqual(None, CLI.parse([])[0].database_user)

    def test_it_should_accept_database_user_options(self):
        self.assertEqual("user_value", CLI.parse(["--db-user", "user_value"])[0].database_user)

    def test_it_should_not_has_a_default_value_for_database_password(self):
        self.assertEqual(None, CLI.parse([])[0].database_password)

    def test_it_should_accept_database_password_options(self):
        self.assertEqual("password_value", CLI.parse(["--db-password", "password_value"])[0].database_password)

    def test_it_should_not_has_a_default_value_for_database_host(self):
        self.assertEqual(None, CLI.parse([])[0].database_host)

    def test_it_should_accept_database_host_options(self):
        self.assertEqual("host_value", CLI.parse(["--db-host", "host_value"])[0].database_host)

    def test_it_should_not_has_a_default_value_for_database_port(self):
        self.assertEqual(None, CLI.parse([])[0].database_port)

    def test_it_should_accept_database_port_options(self):
        self.assertEqual("port_value", CLI.parse(["--db-port", "port_value"])[0].database_port)

    def test_it_should_not_has_a_default_value_for_database_endpoint(self):
        self.assertEqual(None, CLI.parse([])[0].database_endpoint)

    def test_it_should_accept_database_endpoint_options(self):
        self.assertEqual("endpoint_value", CLI.parse(["--db-endpoint", "endpoint_value"])[0].database_endpoint)

    def test_it_should_not_has_a_default_value_for_database_graph(self):
        self.assertEqual(None, CLI.parse([])[0].database_graph)

    def test_it_should_accept_database_graph_options(self):
        self.assertEqual("graph_value", CLI.parse(["--db-graph", "graph_value"])[0].database_graph)

    def test_it_should_not_has_a_default_value_for_database_ontology(self):
        self.assertEqual(None, CLI.parse([])[0].database_ontology)

    def test_it_should_accept_database_ontology_options(self):
        self.assertEqual("ontology_value", CLI.parse(["--db-ontology", "ontology_value"])[0].database_ontology)

    def test_it_should_not_has_a_default_value_for_migrations_dir(self):
        self.assertEqual(None, CLI.parse([])[0].database_migrations_dir)

    def test_it_should_accept_migrations_dir_options(self):
        self.assertEqual(".:../:/tmp", CLI.parse(["--db-migrations-dir", ".:../:/tmp"])[0].database_migrations_dir)

    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_call_print_statment_with_the_given_message(self, stdout_mock):
        CLI.msg("message to print")
        self.assertEqual("message to print\n", stdout_mock.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_call_print_statment_with_the_given_message_and_color_codes_when_colors_are_on(self, stdout_mock):
        CLI.show_colors()
        CLI.msg("message to print")
        self.assertEqual("\x1b[36mmessage to print\x1b[0m\n", stdout_mock.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_it_should_use_color_code_to_the_specified_color(self, stdout_mock):
        CLI.show_colors()
        CLI.msg("message to print", "RED")
        self.assertEqual("\x1b[31mmessage to print\x1b[0m\n", stdout_mock.getvalue())

    @patch('simple_virtuoso_migrate.cli.CLI.msg')
    def test_it_should_show_error_message_and_exit(self, msg_mock):
        try:
            CLI.error_and_exit("error test message, dont mind about it :)")
            self.fail("it should not get here")
        except:
            pass
        msg_mock.assert_called_with("[ERROR] error test message, dont mind about it :)\n", "RED")

    @patch('simple_virtuoso_migrate.cli.CLI.msg')
    def test_it_should_show_info_message_and_exit(self, msg_mock):
        try:
            CLI.info_and_exit("info test message, dont mind about it :)")
            self.fail("it should not get here")
        except:
            pass
        msg_mock.assert_called_with("info test message, dont mind about it :)\n", "BLUE")

if __name__ == "__main__":
    unittest.main()
