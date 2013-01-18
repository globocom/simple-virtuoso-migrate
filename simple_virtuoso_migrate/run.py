from cli import CLI
from config import FileConfig, Config
from getpass import getpass
from main import Main
from version import SIMPLE_VIRTUOSO_MIGRATE_VERSION
import codecs
import sys

# fixing print in non-utf8 terminals
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)


def run_from_argv(args=sys.argv[1:]):
    if not args:
        args = ["-h"]
    (options, _) = CLI.parse(args)
    run(options.__dict__)


def run(options):
    """ Initial Module. Treat Parameters and call Main Module for execution """
    try:
        if options.get('simple_virtuoso_migrate_version'):
            msg = ('simple-virtuoso-migrate v%s' %
                                            SIMPLE_VIRTUOSO_MIGRATE_VERSION)
            CLI.info_and_exit(msg)

        if options.get('show_colors'):
            CLI.show_colors()

        # Create config
        if options.get('config_file'):
            config = FileConfig(options.get('config_file'),
                                options.get('environment'))
        else:
            config = Config()

        config.update('schema_version', options.get('schema_version'))
        config.update('show_sparql', options.get('show_sparql'))
        config.update('show_sparql_only', options.get('show_sparql_only'))
        config.update('file_migration', options.get('file_migration'))
        #config.update('add_ttl', options.get('add_ttl'))
        config.update('load_ttl', options.get('load_ttl'))
        config.update('log_dir', options.get('log_dir'))
        config.update('database_user', options.get('database_user'))
        config.update('database_password', options.get('database_password'))
        config.update('host_user', options.get('host_user'))
        config.update('host_password', options.get('host_password'))
        config.update('virtuoso_dirs_allowed',
                      options.get('virtuoso_dirs_allowed'))
        config.update('database_host', options.get('database_host'))
        config.update('database_port', options.get('database_port'))
        config.update('database_endpoint', options.get('database_endpoint'))
        config.update('database_graph', options.get('database_graph'))
        config.update('database_ontology', options.get('database_ontology'))
        if options.get('database_migrations_dir'):
            config.update("database_migrations_dir",
                          Config._parse_migrations_dir(
                                            options.get(
                                                'database_migrations_dir')))

        config.update("database_migrations_dir",
                      config.get("database_migrations_dir")[0])
        config.update('log_level', int(options.get('log_level')))

        # Ask the password for user if configured
        if config.get('database_password') == '<<ask_me>>':
            CLI.msg('\nPlease inform password to connect to\
                virtuoso (DATABASE) "%s@%s"' % (config.get('database_user'),
                                                config.get('database_host')))
            passwd = getpass()
            config.update('database_password', passwd)

        is_local = config.get('database_host', '').lower() in ["localhost",
                                                               "127.0.0.1"]
        #import pdb; pdb.set_trace()
        if config.get('load_ttl') and\
                config.get('virtuoso_dirs_allowed') is None and\
                not is_local:
            if config.get('host_password') == '<<ask_me>>':
                CLI.msg('\nPlease inform password to connect to\
                virtuoso (HOST) "%s@%s"' % (config.get('host_user'),
                                            config.get('database_host')))
                passwd = getpass()
                config.update('host_password', passwd)
        # If CLI was correctly parsed, execute db-virtuoso.
        Main(config).execute()
    except KeyboardInterrupt:
        CLI.info_and_exit("\nExecution interrupted by user...")
    except Exception, e:
        CLI.error_and_exit(unicode(e))

if __name__ == '__main__':
    "Begin of execution"

    run_from_argv()
