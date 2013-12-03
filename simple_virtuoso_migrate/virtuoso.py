# -*- coding: utf-8 -*-

from core.exceptions import MigrationException
from git import Git
from helpers import Utils
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
import datetime
import logging
import os
import rdflib
import shutil
import ssh
import subprocess

logging.basicConfig()

ISQL = "isql -U %s -P %s -H %s -S %s"
ISQL_CMD = 'echo "%s" | %s -b %d'
ISQL_CMD_WITH_FILE = '%s -b %d < "%s"'
ISQL_UP = "set echo on;\n\
            DB.DBA.TTLP_MT_LOCAL_FILE('%(ttl)s', '', '%(graph)s');"
ISQL_DOWN = "SPARQL CLEAR GRAPH <%(graph)s>;"
ISQL_SERVER = "select server_root();"


class Virtuoso(object):
    """ Interact with Virtuoso Server"""

    def __init__(self, config):
        self.migration_graph = config.get("migration_graph")
        self.__virtuoso_host = config.get("database_host", '')
        self.__virtuoso_user = config.get("database_user")
        self.__virtuoso_passwd = config.get("database_password")
        self.__host_user = config.get("host_user", None)
        self.__host_passwd = config.get("host_password", None)
        self.__virtuoso_dirs_allowed = config.get("virtuoso_dirs_allowed", None)
        self.__virtuoso_port = config.get("database_port")
        self.__virtuoso_endpoint = config.get("database_endpoint")
        self.__virtuoso_graph = config.get("database_graph")
        self.__virtuoso_ontology = config.get("database_ontology")
        self._migrations_dir = config.get("database_migrations_dir")

        if self.__virtuoso_dirs_allowed:
            self._virtuoso_dir = os.path.realpath(self.__virtuoso_dirs_allowed)
        else:
            self._virtuoso_dir = self._run_isql(ISQL_SERVER)[0].split(
                                                                    '\n\n')[-2]

    def _run_isql(self, cmd, archive=False):
        conn = ISQL % (self.__virtuoso_user,
                       self.__virtuoso_passwd,
                       self.__virtuoso_host,
                       self.__virtuoso_port)
        if archive:
            isql_cmd = ISQL_CMD_WITH_FILE % (conn, max(os.path.getsize(cmd) / 1000, 1), cmd)
        else:
            isql_cmd = ISQL_CMD % (cmd, conn, max(len(cmd) / 1000, 1))
        process = subprocess.Popen(isql_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout_value, stderr_value = process.communicate()
        if stderr_value:
            raise Exception(stderr_value)
        return stdout_value, stderr_value

    def _copy_ttl_to_virtuoso_dir(self, ttl):
        _, fixture_file = os.path.split(ttl)

        if self._is_local() or self.__virtuoso_dirs_allowed:
            origin = os.path.realpath(ttl)
            dest = os.path.realpath(os.path.join(self._virtuoso_dir,
                                                 fixture_file))
            if origin != dest:
                shutil.copyfile(origin, dest)
        else:
            s = ssh.Connection(host=self.__virtuoso_host,
                               username=self.__host_user,
                               password=self.__host_passwd)
            s.put(ttl, os.path.join(self._virtuoso_dir, fixture_file))
            s.close()
        return fixture_file

    def _is_local(self):
        return self.__virtuoso_host.lower() in ["localhost", "127.0.0.1"]

    def _remove_ttl_from_virtuoso_dir(self, ttl):
        ttl_path = os.path.join(self._virtuoso_dir, ttl)
        os.remove(ttl_path)

    def _upload_single_ttl_to_virtuoso(self, fixture):
        fixture = self._copy_ttl_to_virtuoso_dir(fixture)
        file_to_upload = os.path.join(self._virtuoso_dir, fixture)
        isql_up = ISQL_UP % {"ttl": file_to_upload,
                             "graph": self.__virtuoso_graph}
        out, err = self._run_isql(isql_up)

        if self._is_local() or self.__virtuoso_dirs_allowed:
            self._remove_ttl_from_virtuoso_dir(fixture)
        return out, err

    def upload_ttls_to_virtuoso(self, full_path_files):
        response_dict = {}
        for fname in full_path_files:
            response_dict[fname] = self._upload_single_ttl_to_virtuoso(fname)
        return response_dict

    def execute_change(self, sparql_up, sparql_down, execution_log=None):
        """ Final Step. Execute the changes to the Database """

        file_up = None
        file_down = None
        try:
            file_up = Utils.write_temporary_file(("set echo on;\n%s" %
                                                                    sparql_up),
                                                 "file_up")

            #db = self.connect()
            stdout_value, stderr_value = self._run_isql(file_up, True)
            if len(stderr_value) > 0:
                #rollback
                file_down = Utils.write_temporary_file(("set echo on;\n%s" %
                                                                sparql_down),
                                                       "file_down")
                _, stderr_value_rollback = self._run_isql(file_down, True)
                if len(stderr_value_rollback) > 0:
                    raise MigrationException("\nerror executing migration "
                                        "statement: %s\n\nRollback done "
                                        "partially: error executing rollback "
                                        "statement: %s" % (stderr_value,
                                                        stderr_value_rollback))
                else:
                    raise MigrationException("\nerror executing migration "
                                             "statement: %s\n\nRollback done "
                                             "successfully!!!" % stderr_value)

            if execution_log:
                execution_log(stdout_value)
        finally:
            if file_up and os.path.exists(file_up):
                os.unlink(file_up)

            if file_down and os.path.exists(file_down):
                os.unlink(file_down)

    def get_current_version(self):
        """ Get Virtuoso Database Graph Current Version """

        query = """\
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
select distinct ?version ?origen
FROM <%(m_graph)s>
{{
select distinct ?version ?origen ?data
FROM <%(m_graph)s>
where {?s owl:versionInfo ?version;
<%(m_graph)scommited> ?data;
<%(m_graph)sproduto> "%(v_graph)s";
<%(m_graph)sorigen> ?origen.}
ORDER BY desc(?data) LIMIT 1
}}""" % {'m_graph': self.migration_graph, 'v_graph': self.__virtuoso_graph}

        graph = Graph(store="SPARQLStore")
        graph.open(self.__virtuoso_endpoint, create=False)
        graph.store.baseURI = self.__virtuoso_endpoint
        ns = list(graph.namespaces())
        assert len(ns) > 0, ns

        res = graph.query(query)

        graph.close()

        nroResults = len(res)
        if nroResults > 0:
            res.vars = ['version', 'origen']
            versao, origem = iter(res).next()
            versao = None if str(versao) == 'None' else str(versao)
            return  versao, str(origem)
        else:
            return None, None

    def _generate_migration_sparql_commands(self, origin_store,
                                            destination_store):
        diff = (origin_store - destination_store) or []
        checked = set()
        forward_migration = ""
        backward_migration = ""

        for triples in diff:
            subject, predicate, object_ = triples

            query_get_blank_node = """\
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?s WHERE
            {
                """
            if isinstance(subject, rdflib.term.BNode) and (
                                                    not subject in checked):
                checked.add(subject)

                blank_node_as_an_object = ""
                triples_with_blank_node_as_object = diff.subject_predicates(subject)
                for triple_subject, triple_object in triples_with_blank_node_as_object:
                    query_get_blank_node = query_get_blank_node + "%s %s ?s . " % (triple_subject.n3(),
                                                         triple_object.n3())
                    blank_node_as_an_object = blank_node_as_an_object + "%s %s " % (
                                                              triple_subject.n3(),
                                                              triple_object.n3())

                blank_node_as_a_subject = ""
                triples_with_blank_node_as_subject = diff.predicate_objects(subject)
                for pred_obj in triples_with_blank_node_as_subject:
                    query_get_blank_node = query_get_blank_node + "?s %s %s . " % (pred_obj[0].n3(),
                                                         pred_obj[1].n3())
                    blank_node_as_a_subject = blank_node_as_a_subject + "%s %s ; " % (
                                                            pred_obj[0].n3(),
                                                            pred_obj[1].n3())
                query_get_blank_node = query_get_blank_node + "}"

                qres_1 = destination_store.query(query_get_blank_node)

                if len(qres_1) <= 0:
                    forward_migration = forward_migration + \
                        u"\nSPARQL INSERT INTO <%s> { %s[%s] };" % (
                                                            self.__virtuoso_graph,
                                                            blank_node_as_an_object,
                                                            blank_node_as_a_subject)
                    blank_node_as_a_subject = blank_node_as_a_subject[:-2]

                    backward_migration = backward_migration + \
                    (u"\nSPARQL DELETE FROM <%s> { %s ?s. ?s %s } WHERE "
                    "{ %s ?s. ?s %s };") % (self.__virtuoso_graph, blank_node_as_an_object,
                                           blank_node_as_a_subject,
                                           blank_node_as_an_object,
                                           blank_node_as_a_subject)

            if isinstance(subject, rdflib.term.URIRef) and \
                        not isinstance(object_, rdflib.term.BNode):
                forward_migration = forward_migration + \
                                u"\nSPARQL INSERT INTO <%s> {%s %s %s . };"\
                                % (self.__virtuoso_graph, subject.n3(), predicate.n3(),
                                   object_.n3())
                backward_migration = backward_migration + \
                    u"\nSPARQL DELETE FROM <%s> {%s %s %s . };" % (self.__virtuoso_graph,
                                                            subject.n3(),
                                                            predicate.n3(),
                                                            object_.n3())

        return forward_migration, backward_migration

    def get_sparql(self, current_ontology=None, destination_ontology=None,
                         current_version=None, destination_version=None,
                         origen=None, insert=None):
        """ Make sparql statements to be executed """
        query_up = ""
        query_down = ""
        if insert is None:

            current_graph = ConjunctiveGraph()
            destination_graph = ConjunctiveGraph()
            #if insert is None:
            try:
                if current_ontology is not None:
                    current_graph.parse(data=current_ontology, format='turtle')
                destination_graph.parse(data=destination_ontology,
                                        format='turtle')
            except BadSyntax, e:
                e._str = e._str.decode('utf-8')
                raise MigrationException("Error parsing graph %s" % unicode(e))

            forward_migration, backward_migration = (
                            self._generate_migration_sparql_commands(
                                                        destination_graph,
                                                        current_graph))
            query_up += forward_migration
            query_down += backward_migration
            forward_migration, backward_migration = (
                            self._generate_migration_sparql_commands(
                                                        current_graph,
                                                        destination_graph))
            query_down += forward_migration
            query_up += backward_migration

        # Registry schema changes on migration_graph
        now = datetime.datetime.now()
        values = {
            'm_graph': self.migration_graph,
            'v_graph': self.__virtuoso_graph,
            'c_version': current_version,
            'd_version': destination_version,
            'endpoint': self.__virtuoso_endpoint,
            'user': self.__virtuoso_user,
            'host': self.__virtuoso_host,
            'origen': origen,
            'date': str(now.strftime("%Y-%m-%d %H:%M:%S")),
            'insert': insert,
            'query_up': query_up.replace('"', '\\"').replace('\n', '\\n'),
            'query_down': query_down.replace('"', '\\"').replace('\n', '\\n')
        }
        if insert is not None:
            query_up += (u'\nSPARQL INSERT INTO <%(m_graph)s> { '
                    '[] owl:versionInfo "%(c_version)s"; '
                    '<%(m_graph)sendpoint> "%(endpoint)s"; '
                    '<%(m_graph)susuario> "%(user)s"; '
                    '<%(m_graph)sambiente> "%(host)s"; '
                    '<%(m_graph)sproduto> "%(v_graph)s"; '
                    '<%(m_graph)scommited> "%(date)s"^^xsd:dateTime; '
                    '<%(m_graph)sorigen> "%(origen)s"; '
                    '<%(m_graph)sinserted> "%(insert)s".};') % values
            query_down += (u'\nSPARQL DELETE FROM <%(m_graph)s> {?s ?p ?o} '
                    'WHERE {?s owl:versionInfo "%(c_version)s"; '
                    '<%(m_graph)sendpoint> "%(endpoint)s"; '
                    '<%(m_graph)susuario> "%(user)s"; '
                    '<%(m_graph)sambiente> "%(host)s"; '
                    '<%(m_graph)sproduto> "%(v_graph)s"; '
                    '<%(m_graph)scommited> "%(date)s"^^xsd:dateTime; '
                    '<%(m_graph)sorigen> "%(origen)s"; '
                    '<%(m_graph)sinserted> "%(insert)s"; ?p ?o.};') % values
        else:
            query_up += (u'\nSPARQL INSERT INTO <%(m_graph)s> { '
                    '[] owl:versionInfo "%(d_version)s"; '
                    '<%(m_graph)sendpoint> "%(endpoint)s"; '
                    '<%(m_graph)susuario> "%(user)s"; '
                    '<%(m_graph)sambiente> "%(host)s"; '
                    '<%(m_graph)sproduto> "%(v_graph)s"; '
                    '<%(m_graph)scommited> "%(date)s"^^xsd:dateTime; '
                    '<%(m_graph)sorigen> "%(origen)s"; '
                    '<%(m_graph)schanges> "%(query_up)s".};') % values
            query_down += (u'\nSPARQL DELETE FROM <%(m_graph)s> {?s ?p ?o} '
                    'WHERE {?s owl:versionInfo "%(d_version)s"; '
                    '<%(m_graph)sendpoint> "%(endpoint)s"; '
                    '<%(m_graph)susuario> "%(user)s"; '
                    '<%(m_graph)sambiente> "%(host)s"; '
                    '<%(m_graph)sproduto> "%(v_graph)s"; '
                    '<%(m_graph)scommited> "%(date)s"^^xsd:dateTime; '
                    '<%(m_graph)sorigen> "%(origen)s"; '
                    '<%(m_graph)schanges> "%(query_up)s"; ?p ?o.};') % values

        return query_up, query_down

    def get_ontology_by_version(self, version):
        file_name = self._migrations_dir + "/" + self.__virtuoso_ontology
        if not os.path.exists(file_name):
            raise Exception('migration file does not exist (%s)' % file_name)
        return Git(self._migrations_dir).execute(["git",
                                                  "show",
                                                  version + ":" +\
                                                    self.__virtuoso_ontology])

    def get_ontology_from_file(self, filename):
        if not os.path.exists(filename):
            raise Exception('migration file does not exist (%s)' % filename)
        f = open(filename, 'rU')
        content = f.read()
        f.close()
        return content
