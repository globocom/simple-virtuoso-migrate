from optparse import OptionParser, make_option
import sys


class CLI(object):
    """Parse parameters passed by command line options when
        the user calls virtuoso-migrate. Uses external module optparse"""

    color = {
        "PINK": "",
        "BLUE": "",
        "CYAN": "",
        "GREEN": "",
        "YELLOW": "",
        "RED": "",
        "END": "",
    }

    @staticmethod
    def show_colors():
        CLI.color = {
            "PINK": "\033[35m",
            "BLUE": "\033[34m",
            "CYAN": "\033[36m",
            "GREEN": "\033[32m",
            "YELLOW": "\033[33m",
            "RED": "\033[31m",
            "END": "\033[0m",
        }

    @staticmethod
    def parse(args=None):
        parser = OptionParser(option_list=CLI.options_to_parser())
        parser.add_option("-v", "--version",
                action="store_true",
                dest="simple_virtuoso_migrate_version",
                default=False,
                help="Displays simple-virtuoso-migrate's version and exit.")
        return parser.parse_args(args)

    @classmethod
    def options_to_parser(cls):
        "Inform command-line options to be Parsed"
        return (
        make_option("-c", "--config",
                dest="config_file",
                default=None,
                help="Use a specific config file. If not provided, will search\
                     for 'simple-virtuoso-migrate.conf'\
                     in the current directory."),

        make_option("-l", "--log-level",
                dest="log_level",
                default=1,
                help="Log level: 0-no log; 1-migrations log; 2-statement\
                      execution log (default: %default)"),

        make_option("--log-dir",
                dest="log_dir",
                default=None,
                help="Directory to save the log files of execution"),

        make_option("-g", "--git",
                dest="schema_version",
                default=None,
                help="Git tag version to migrate to. If not provided will\
                      raise an exception."),

        make_option("-f", "--file",
                dest="file_migration",
                default=None,
                help="Create migration from file"),

        #make_option("-i", "--insert",
        #        dest="add_ttl",
        #        default=None,
        #        help="Insert TTL file"),

        make_option("-a", "--add",
                dest="load_ttl",
                default=None,
                help="Load TTL file"),

        make_option("--color",
                action="store_true",
                dest="show_colors",
                default=False,
                help="Output with beautiful colors."),

        make_option("--showsparql",
                action="store_true",
                dest="show_sparql",
                default=False,
                help="Show all SPARQL statements executed."),

        make_option("--showsparqlonly",
                action="store_true",
                dest="show_sparql_only",
                default=False,
                help="Show all SQL statements that would be executed but\
                      DON'T execute them in the virtuoso."),

        make_option("--env", "--environment",
                dest="environment",
                default="",
                help="Use this environment to get specific configurations."),

        make_option("--db-user",
                dest="database_user",
                default=None,
                help="Set the username to connect to database."),

        make_option("--db-password",
                dest="database_password",
                default=None,
                help="Set the password to connect to database."),

        make_option("--host-user",
                dest="host_user",
                default=None,
                help="Set the username to connect to host."),

        make_option("--host-password",
                dest="host_password",
                default=None,
                help="Set the password to connect to host."),

        make_option("--db-host",
                dest="database_host",
                default=None,
                help="Set the host where the database is."),

        make_option("--db-port",
                dest="database_port",
                default=None,
                help="Set the port where the database is."),

        make_option("--db-endpoint",
                dest="database_endpoint",
                default=None,
                help="Set the endpoint address."),

        make_option("--db-graph",
                dest="database_graph",
                default=None,
                help="Set the graph name."),

        make_option("--db-ontology",
                dest="database_ontology",
                default=None,
                help="Set the ontology ttl file name."),

        make_option("--db-migrations-dir",
                dest="database_migrations_dir",
                default=None,
                help="List of directories where migrations are separated by a\
                      colon")
        )

    @classmethod
    def error_and_exit(cls, msg):
        cls.msg("[ERROR] %s\n" % msg, "RED")
        sys.exit(1)

    @classmethod
    def info_and_exit(cls, msg):
        cls.msg("%s\n" % msg, "BLUE")
        sys.exit(0)

    @classmethod
    def msg(cls, msg, color="CYAN"):
        print "%s%s%s" % (cls.color[color], msg, cls.color["END"])
