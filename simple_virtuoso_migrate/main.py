import os
import sys
from cli import CLI
from log import LOG
from core import SimpleVirtuosoMigrate
from virtuoso import Virtuoso
from config import Config


class Main(object):
    """ Call all execution modules """

    def __init__(self, config):

        if not Main._valid_version():
            print "You need to upgrade your Python version from %s to 2.7.x" % sys.version
            sys.exit(0)

        Main._check_configuration(config)
        self.config = config
        self.virtuoso = Virtuoso(config)
        self.virtuoso_migrate = SimpleVirtuosoMigrate(config)
        self.log = LOG(self.config.get("log_dir", None))

    @staticmethod
    def _valid_version():
        return sys.version_info[0] == 2 and sys.version_info[1] >= 7

    def execute(self):
        """ evaluate what action to take from command line options """

        self._execution_log("\nStarting Virtuoso migration...",
                            "PINK",
                            log_level_limit=1)

        if self.config.get("load_ttl", None) is not None:
            operation_result = self._load_triples()

        else:
            operation_result = self._migrate()

        run_after_script = self.config.get('RUN_AFTER', None)
        if run_after_script:
            self._execution_log("\nExecuting run_after script %s.\n" % run_after_script,
                                "PINK",
                                log_level_limit=1)
            self._run_after(run_after_script, operation_result)

        self._execution_log("\nDone.\n", "PINK", log_level_limit=1)

    def _load_triples(self):
        """ Called if the -a option is passed in the command line """

        current_version, origen = self.virtuoso.get_current_version()

        files_to_load = self.config.get("load_ttl")
        basepath = os.path.dirname(files_to_load)
        if os.path.isdir(files_to_load):
            files = []
            for i in os.listdir(files_to_load):
                files.append(os.path.join(basepath, i))
        else:
            files = [files_to_load]

        files = [i for i in files if i.endswith('.ttl')]

        self._execution_log("- TTL(s) to upload: %r" % files,
                            "GREEN",
                            log_level_limit=1)

        out_list = []
        ok_list = []
        err_list = []
        operation_result = {
            'operation': 'load',
            'ok_list': ok_list,
            'out_list': out_list,
            'err_list': err_list
        }

        if not self.config.get("show_sparql_only", False):
            response_dict = self.virtuoso.upload_ttls_to_virtuoso(files)
            for filename, (out, err) in response_dict.items():
                if err:
                    err_list.append("File %s with err %s" % (filename, err))
                else:
                    out_list.append(out)
                    ok_list.append(filename)
            if err_list:
                self._execution_log("ERRORS %r" % err_list,
                                    "RED",
                                    log_level_limit=1)

            if origen is None:
                origen = "insert"

            if ok_list:
                sparql_up, sparql_down = self.virtuoso.get_sparql(None,
                                                                  None,
                                                                  current_version,
                                                                  None,
                                                                  origen,
                                                                  ok_list)
                self._execute_migrations(sparql_up,
                                         sparql_down,
                                         current_version,
                                         current_version,
                                         out_list)
                operation_result['current_version'] = current_version
                operation_result['sparql_up'] = sparql_up
                operation_result['sparql_down'] = sparql_down

            else:
                self._execution_log("\n".join(out_list), log_level_limit=1)

        return operation_result

    def _migrate(self):
        """ Execute migrations based on git tags """
        source = 'git'
        current_ontology = None
        current_version, origen = self.virtuoso.get_current_version()
        # Making the first migration to the database
        if current_version is None:
            if self.config.get("file_migration", None) is not None:
                self._execution_log(("- Current version is: %s" %
                                                        current_version),
                                    "GREEN",
                                    log_level_limit=1)
                self._execution_log(("- Destination version is: %s" %
                                        self.config.get("file_migration")),
                                    "GREEN",
                                    log_level_limit=1)
                CLI.error_and_exit("Can't execute migration FROM None TO File "
                                   "(TIP: version it using git --tag and then "
                                   "use -m)")
        else:
            if origen == "file":
                if self.config.get("file_migration", None) is not None:
                    self._execution_log(("- Current version is: %s" %
                                                            current_version),
                                        "GREEN",
                                        log_level_limit=1)
                    self._execution_log(("- Destination version is: %s" %
                                            self.config.get("file_migration")),
                                        "GREEN",
                                        log_level_limit=1)
                    CLI.error_and_exit("Can't execute migration FROM File TO "
                                       "File (TIP: version it using git --tag "
                                       "and then use -m)")

            current_ontology = self.virtuoso.get_ontology_by_version(current_version)

        if self.config.get("file_migration", None) is not None:
            source = 'file'
            destination_version = self.config.get("file_migration")
            destination_ontology = self.virtuoso.get_ontology_from_file(
                                                        destination_version)
        else:
            destination_version = self._get_destination_version()
            destination_ontology = self.virtuoso.get_ontology_by_version(
                                                        destination_version)

        sparql_up, sparql_down = self.virtuoso.get_sparql(current_ontology,
                                                          destination_ontology,
                                                          current_version,
                                                          destination_version,
                                                          source)

        self._execute_migrations(sparql_up,
                                 sparql_down,
                                 current_version,
                                 destination_version)

        return {'operation': 'migration',
                'sparql_up': sparql_up,
                'sparql_down': sparql_down,
                'current_version': current_version,
                'destination_version': destination_version}

    def _get_destination_version(self):
        """ get destination version """

        destination_version = self.config.get("schema_version", None)
        if destination_version is None:
            destination_version = (
                            self.virtuoso_migrate.latest_version_available())
        if destination_version is not None and\
            not self.virtuoso_migrate.check_if_version_exists(
                                                        destination_version):
            raise Exception("version not found (%s)" % destination_version)
        return destination_version

    def _execute_migrations(self, sparql_up, sparql_down, current_version,
                                            destination_version,
                                            out_list=None):
        self._execution_log("- Current version is: %s" % current_version,
                            "GREEN",
                            log_level_limit=1)
        self._execution_log(("- Destination version is: %s" %
                                                destination_version),
                            "GREEN",
                            log_level_limit=1)

        if self.config.get("show_sparql_only"):
            self._execution_log("\nWARNING: commands are not being executed "
                                "('--show_sparql_only' activated)",
                                "RED",
                                log_level_limit=1)
        else:
            self._execution_log("\nStarting Migration!", log_level_limit=1)

        if len(sparql_up.splitlines()) == 2 and \
                                        self.config.get("load_ttl", None) is None:
            self._execution_log("\nNothing to do.\n", "PINK",
                                log_level_limit=1)
            return

        if not self.config.get("show_sparql_only", False):
            self._execution_log("===== executing =====", log_level_limit=1)

            if out_list:
                self._execution_log("\n".join(out_list), log_level_limit=1)

            self.virtuoso.execute_change(sparql_up, sparql_down,
                                         execution_log=self._execution_log)

        if self.config.get("show_sparql", False) or self.config.get(
                                                            "show_sparql_only",
                                                            False):
            self._execution_log(
                            "__________ SPARQL statements executed __________",
                            "YELLOW", log_level_limit=1)
            self._execution_log(sparql_up, "YELLOW", log_level_limit=1)
            self._execution_log(
                            "_____________________________________________",
                            "YELLOW", log_level_limit=1)

    def _execution_log(self, msg, color="CYAN", log_level_limit=2):
        if self.config.get("log_level", 1) >= log_level_limit:
            CLI.msg(msg, color)
        self.log.debug(msg)

    def _run_after(self, script_name, operation_result):
        module = open(script_name, "r").read()
        sandbox = {}
        exec(module, sandbox)
        try:
            run_after_func = sandbox['run_after']
            run_after_func(self, operation_result)
        except KeyError:
            self._execution_log("\nRun after script %s does not have run_after() function .\n" % script_name,
                                "PINK", log_level_limit=1)

    @staticmethod
    def _check_configuration(config):
        if not isinstance(config, Config):
            raise Exception("config must be an instance of "
                            "simple_virtuoso_migrate.config.Config")

        required_configs = ['database_host',
                            'database_endpoint',
                            'database_user',
                            'database_password',
                            'database_migrations_dir',
                            'database_port',
                            'database_graph',
                            'database_ontology',
                            'migration_graph']

        for key in required_configs:
            #check if config has the key, if do not have will raise exception
            config.get(key)
