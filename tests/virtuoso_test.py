# -*- coding: utf-8 -*-
import unittest
import datetime
import os
import re

from mock import patch, Mock, call, MagicMock
from rdflib.graph import ConjunctiveGraph

from simple_virtuoso_migrate.config import Config
from simple_virtuoso_migrate.main import Virtuoso
from simple_virtuoso_migrate.core.exceptions import MigrationException
from tests import create_file, delete_files, BaseTest


class VirtuosoTest(BaseTest):

    def setUp(self):
        super(VirtuosoTest, self).setUp()
        self.config = Config()
        self.config.put("database_migrations_dir", ".")
        self.config.put("database_ontology", "test.ttl")
        self.config.put("database_graph", "test")
        self.config.put("database_host", "localhost")
        self.config.put("database_user", "user")
        self.config.put("database_password", "password")
        self.config.put("database_port", 9999)
        self.config.put("database_endpoint", "endpoint")
        self.config.put("host_user", "host-user")
        self.config.put("host_password", "host-passwd")
        self.config.put("virtuoso_dirs_allowed", "/tmp")
        self.config.put("migration_graph", "http://example.com/")
        create_file("test.ttl", "")

        self.data_ttl_content = """
@prefix : <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<http://example.com/John> rdf:type <http://example.com/Person>.
"""

        create_file("data.ttl", self.data_ttl_content)

        self.structure_01_ttl_content = """
@prefix : <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:Actor rdf:type owl:Class .
:SoapOpera rdf:type owl:Class .
"""

        create_file("structure_01.ttl", self.structure_01_ttl_content)

        self.structure_02_ttl_content = """
@prefix : <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:Actor rdf:type owl:Class .
:SoapOpera rdf:type owl:Class .
:RoleOnSoapOpera rdf:type owl:Class .

:role rdf:type owl:Class ;
                rdfs:subClassOf [
                    rdf:type owl:Restriction ;
                    owl:onProperty :play_a_role ;
                    owl:onClass :RoleOnSoapOpera ;
                    owl:minQualifiedCardinality "1"^^xsd:nonNegativeInteger ;
                    owl:maxQualifiedCardinality "1"^^xsd:nonNegativeInteger
                ] .
"""

        create_file("structure_02.ttl", self.structure_02_ttl_content)

        self.structure_03_ttl_content = """
@prefix : <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:Actor rdf:type owl:Class .
:SoapOpera rdf:type owl:Class .
:RoleOnSoapOpera rdf:type owl:Class .

:role rdf:type owl:Class ;
                rdfs:subClassOf [
                    rdf:type owl:Restriction ;
                    owl:onProperty :play_a_role ;
                    owl:onClass :RoleOnSoapOpera ;
                    owl:minQualifiedCardinality "1111"^^xsd:nonNegativeInteger 
                ] ,
                [
                    rdf:type owl:Restriction ;
                    owl:onProperty :play_a_role ;
                    owl:onClass :RoleOnSoapOpera ;
                    owl:maxQualifiedCardinality "3333"^^xsd:nonNegativeInteger
                ] .
"""

        create_file("structure_03.ttl", self.structure_03_ttl_content)

        self.structure_04_ttl_content = """
@prefix : <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:Actor rdf:type owl:Class .
:SoapOpera rdf:type owl:Class .
:RoleOnSoapOpera rdf:type owl:Class .

:role rdf:type owl:Class ;
                rdfs:subClassOf [
                    rdf:type owl:Restriction ;
                    owl:onProperty :play_a_role ;
                    owl:onClass :RoleOnSoapOpera ;
                    owl:minQualifiedCardinality "1"^^xsd:nonNegativeInteger
                ] .
"""

        create_file("structure_04.ttl", self.structure_02_ttl_content)

    def tearDown(self):
        super(VirtuosoTest, self).tearDown()
        delete_files("*.ttl")

#    @patch('subprocess.Popen', return_value=Mock(**{"communicate.return_value": ("out", "err")}))
#    def test_it_should_use_popen_to_run_a_command(self, popen_mock):
#        Virtuoso(self.config).command_call("echo 1")
#        popen_mock.assert_called_with('echo 1', shell=True, stderr=-1, stdout=-1)

#    def test_it_should_return_stdout_and_stderr(self):
#        stdout, _ = Virtuoso(self.config).command_call("echo 'out'")
#        _, stderr = Virtuoso(self.config).command_call("python -V")
#
#        self.assertEqual('out\n', stdout)
#        self.assertEqual('python', stderr.split(' ')[0].lower())

    @patch('subprocess.Popen.communicate', return_value=("", ""))
    @patch('subprocess.Popen.__init__', return_value=None)
    def test_it_should_use_isql_executable_to_send_commands_to_virtuoso(self, popen_mock, communicate_mock):
        virtuoso = Virtuoso(self.config)
        virtuoso._run_isql("command")
        popen_mock.assert_called_with('echo "command" | isql -U user -P password -H localhost -S 9999 -b 1', shell=True, stderr=-1, stdout=-1)

    @patch('subprocess.Popen.communicate', return_value=("", ""))
    @patch('subprocess.Popen.__init__', return_value=None)
    def test_it_should_set_the_command_buffer_size_on_isql_calls_to_support_large_commands(self, popen_mock, communicate_mock):
        virtuoso = Virtuoso(self.config)
        cmd = "0123456789" * 250000
        virtuoso._run_isql(cmd)
        popen_mock.assert_called_with('echo "%s" | isql -U user -P password -H localhost -S 9999 -b 2500' % cmd, shell=True, stderr=-1, stdout=-1)

    @patch('subprocess.Popen.communicate', return_value=("", ""))
    @patch('subprocess.Popen.__init__', return_value=None)
    def test_it_should_use_file_size_as_the_command_buffer_size_on_isql_calls(self, popen_mock, communicate_mock):
        virtuoso = Virtuoso(self.config)
        create_file("big_file.ttl", "0123456789" * 480000)
        virtuoso._run_isql("big_file.ttl", True)
        popen_mock.assert_called_with('isql -U user -P password -H localhost -S 9999 -b 4800 < "big_file.ttl"', shell=True, stderr=-1, stdout=-1)

#    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso.command_call',
#           return_value=('', 'some error'))
#    def test_it_should_raise_error_if_isql_status_return_error(self, command_call_mock):
#        virtuoso = Virtuoso(self.config)
#        self.assertRaisesWithMessage(Exception, 'could not connect to virtuoso: some error', virtuoso.connect)

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file', return_value='filename.ttl')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql', return_value=('', ''))
    def test_it_should_write_a_file_with_sparql_up_when_executing_change(self, run_isql_mock, write_temporary_file_mock):
        virtuoso = Virtuoso(self.config)
        virtuoso.execute_change("sparql_up", "sparql_down")
        write_temporary_file_mock.assert_called_with("set echo on;\nsparql_up", "file_up")
        run_isql_mock.assert_called_with('filename.ttl', True)

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file', return_value='filename.ttl')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql', return_value=('', ''))
    def test_it_should_delete_the_temporary_file_with_sparql_up_when_executing_change(self, run_isql_mock, write_temporary_file_mock):
        create_file('filename.ttl', 'content')

        virtuoso = Virtuoso(self.config)
        virtuoso.execute_change("sparql_up", "sparql_down")
        self.assertFalse(os.path.exists('filename.ttl'))

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file', return_value='filename.ttl')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql', side_effect=Exception("some error"))
    def test_it_should_delete_the_temporary_file_with_sparql_up_when_executing_change_raise_an_error(self, run_isql_mock, write_temporary_file_mock):
        create_file('filename.ttl', 'content')

        virtuoso = Virtuoso(self.config)
        self.assertRaisesWithMessage(Exception, 'some error', virtuoso.execute_change, "sparql_up", "sparql_down")
        self.assertFalse(os.path.exists('filename.ttl'))

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql')
    def test_it_should_write_a_file_with_sparql_down_when_executing_change_raise_an_error(self, run_isql_mock, write_temporary_file_mock):
        run_isql_mock.side_effect = command_call_side_effect
        write_temporary_file_mock.side_effect = temp_file_side_effect

        virtuoso = Virtuoso(self.config)
        self.assertRaisesWithMessage(MigrationException, '\nerror executing migration statement: err\n\nRollback done successfully!!!', virtuoso.execute_change, "sparql_up", "sparql_down")
        expected_calls = [
            call("set echo on;\nsparql_up", "file_up"),
            call("set echo on;\nsparql_down", "file_down")
        ]
        self.assertEqual(expected_calls, write_temporary_file_mock.mock_calls)

        expected_calls = [
            call('filename_up.ttl', True),
            call('filename_down.ttl', True)
        ]
        self.assertEqual(expected_calls, run_isql_mock.mock_calls)

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql')
    def test_it_should_delete_the_temporary_file_with_sparql_down_when_executing_change(self, run_isql_mock, write_temporary_file_mock):
        create_file('filename_down.ttl', 'content')
        run_isql_mock.side_effect = command_call_side_effect
        write_temporary_file_mock.side_effect = temp_file_side_effect

        virtuoso = Virtuoso(self.config)
        self.assertRaisesWithMessage(MigrationException, '\nerror executing migration statement: err\n\nRollback done successfully!!!', virtuoso.execute_change, "sparql_up", "sparql_down")
        self.assertFalse(os.path.exists('filename_down.ttl'))

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql')
    def test_it_should_raise_a_specific_message_when_rollback_fails_when_executing_change(self, run_isql_mock, write_temporary_file_mock):
        def command_call_side_effect(*args):
            if (args[0].find("_up") > 0) or (args[0].find("_down") > 0):
                return ("", "err")
            return ("out", "")

        run_isql_mock.side_effect = command_call_side_effect
        write_temporary_file_mock.side_effect = temp_file_side_effect

        virtuoso = Virtuoso(self.config)
        self.assertRaisesWithMessage(MigrationException, '\nerror executing migration statement: err\n\nRollback done partially: error executing rollback statement: err', virtuoso.execute_change, "sparql_up", "sparql_down")

    @patch('simple_virtuoso_migrate.virtuoso.Utils.write_temporary_file', return_value='filename.ttl')
    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso._run_isql', return_value=('output', ''))
    def test_it_should_log_stdout_when_executing_change(self, run_isql_mock, write_temporary_file_mock):
        execution_log = Mock()
        virtuoso = Virtuoso(self.config)
        virtuoso.execute_change("sparql_up", "sparql_down", execution_log)
        execution_log.assert_called_with("output")

    @patch('simple_virtuoso_migrate.virtuoso.Graph.query')
    @patch('simple_virtuoso_migrate.virtuoso.Graph.namespaces', return_value=['ns0'])
    def test_it_should_get_current_version_none_when_database_is_empty(self, graph_mock, graph_query_mock):
        result_mock = MagicMock()
        result_mock.__iter__.return_value = []
        result_mock.__len__.return_value = 0
        graph_query_mock.return_value = result_mock
        current, source = Virtuoso(self.config).get_current_version()

        graph_query_mock.assert_called_with('prefix owl: <http://www.w3.org/2002/07/owl#>\nprefix xsd: <http://www.w3.org/2001/XMLSchema#>\nselect distinct ?version ?origen\nFROM <http://example.com/>\n{{\nselect distinct ?version ?origen ?data\nFROM <http://example.com/>\nwhere {?s owl:versionInfo ?version;\n<http://example.com/commited> ?data;\n<http://example.com/produto> "test";\n<http://example.com/origen> ?origen.}\nORDER BY desc(?data) LIMIT 1\n}}')

        self.assertIsNone(current)
        self.assertIsNone(source)

    @patch('simple_virtuoso_migrate.virtuoso.Graph.query')
    @patch('simple_virtuoso_migrate.virtuoso.Graph.namespaces', return_value=['ns0'])
    def test_it_should_get_current_version_when_database_is_not_empty(self, graph_mock, graph_query_mock):
        result_mock = MagicMock()
        result_mock.__iter__.return_value = [('2', 'git'), ('1', 'file')]
        result_mock.__len__.return_value = 2
        graph_query_mock.return_value = result_mock

        current, source = Virtuoso(self.config).get_current_version()

        self.assertEqual(['version', 'origen'], result_mock.vars)
        self.assertEqual('2', current)
        self.assertEqual('git', source)

    def test_it_should_get_sparql_statments_from_given_ontology(self):

        query_up, query_down = Virtuoso(self.config).get_sparql(destination_ontology=self.data_ttl_content, insert="data.ttl")

        self.assertEqual('\nSPARQL INSERT INTO <http://example.com/> { [] owl:versionInfo "None"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "None"; <http://example.com/inserted> "data.ttl".};' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query_up)
        self.assertEqual('\nSPARQL DELETE FROM <http://example.com/> {?s ?p ?o} WHERE {?s owl:versionInfo "None"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "None"; <http://example.com/inserted> "data.ttl"; ?p ?o.};'  % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query_down)

    # def test_generate_migration_sparql_commands_dealing_with_blank_nodes(self):
    #     self.stdout_mock.stop()

    #     from rdflib.graph import ConjunctiveGraph

    #     ttl_before = self.structure_02_ttl_content
    #     graph_before = ConjunctiveGraph()
    #     graph_before.parse(data=ttl_before, format='turtle')

    #     ttl_after = self.structure_03_ttl_content
    #     graph_after = ConjunctiveGraph()
    #     graph_after.parse(data=ttl_after, format='turtle')

    #     virtuoso_ = Virtuoso(self.config)
        
    #     query_up, query_down = virtuoso_._generate_migration_sparql_commands(origin_store=graph_before, destination_store=graph_after)
    #     query_up2, query_down2 = virtuoso_._generate_migration_sparql_commands(origin_store=graph_after, destination_store=graph_before)
    #     import pdb; pdb.set_trace()
    #     query_down


    def test_generate_migration_sparql_commands_when_only_a_triple_of_an_existing_blank_node_is_deleted(self):
        ttl_before = self.structure_02_ttl_content
        graph_before = ConjunctiveGraph()
        graph_before.parse(data=ttl_before, format='turtle')

        ttl_after = self.structure_04_ttl_content
        graph_after = ConjunctiveGraph()
        graph_after.parse(data=ttl_after, format='turtle')

        virtuoso_ = Virtuoso(self.config)
        
        query_up, query_down = virtuoso_._generate_migration_sparql_commands(origin_store=graph_after, destination_store=graph_before)
        expected_query_up = u'\nSPARQL INSERT INTO <test> { <http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf> [<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> ; <http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger> ; <http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera> ; <http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role> ; ] };'
        expected_query_down  = u'\nSPARQL DELETE FROM <test> { <http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf>  ?s. ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> ; <http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger> ; <http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera> ; <http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>  } WHERE { <http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf>  ?s. ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction> ; <http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger> ; <http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera> ; <http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>  };'
        self.assertEqual(query_up, expected_query_up)
        self.assertEqual(query_down, expected_query_down)

    def test_it_should_get_sparql_statments_when_forward_migration(self):

        query_up, query_down = Virtuoso(self.config).get_sparql(current_ontology=self.structure_01_ttl_content, destination_ontology=self.structure_02_ttl_content, origen='file', destination_version='02')

        expected_lines_up = ["SPARQL INSERT INTO <test> {<http://example.com/RoleOnSoapOpera> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                             "SPARQL INSERT INTO <test> {<http://example.com/role> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                            ]

        expected_log_migration_up = """SPARQL INSERT INTO <http://example.com/> { [] owl:versionInfo "02"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "file"; <http://example.com/changes> "\\n<log>".};""" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        expected_lines_down = ["SPARQL DELETE FROM <test> {<http://example.com/role> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                             "SPARQL DELETE FROM <test> {<http://example.com/RoleOnSoapOpera> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                            ]

        expected_log_migration_down = """SPARQL DELETE FROM <http://example.com/> {?s ?p ?o} WHERE {?s owl:versionInfo "02"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "file"; <http://example.com/changes> "\\n<log>"; ?p ?o.};""" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines_up = query_up.strip(' \t\n\r').splitlines()
        self.assertEqual(4, len(lines_up))
        [self.assertTrue(l in lines_up) for l in expected_lines_up]
        self.assertEqual(lines_up[-1], expected_log_migration_up.replace('<log>', "\n".join(lines_up[0:-1]).replace('"','\\"').replace('\n', '\\n')))

        matchObj = re.search(r"SPARQL INSERT INTO <test> { <http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf> \[(.*)\] };", query_up,  re.MULTILINE)
        sub_classes = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(1))]
        [self.assertTrue(c in sub_classes) for c in [
            '<http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#maxQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera>',
            '<http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>',
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>'
            ]]

        lines_down = query_down.strip(' \t\n\r').splitlines()
        self.assertEqual(4, len(lines_down))
        [self.assertTrue(l in lines_down) for l in expected_lines_down]
        self.assertEqual(lines_down[-1], expected_log_migration_down.replace('<log>', "\n".join(lines_up[0:-1]).replace('"','\\"').replace('\n', '\\n')))

        matchObj = re.search(r"SPARQL DELETE FROM <test> {(.*)} WHERE {(.*)};", query_down,  re.MULTILINE)
        sub_classes_01 = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(1))]
        sub_classes_02 = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(2))]
        [self.assertTrue((c in sub_classes_01) and (c in sub_classes_02)) for c in [
            '<http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf>',
            '<http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#maxQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera>',
            '<http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>',
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>'
            ]]


    def test_it_should_get_sparql_statments_when_backward_migration(self):

        query_up, query_down = Virtuoso(self.config).get_sparql(current_ontology=self.structure_02_ttl_content, destination_ontology=self.structure_01_ttl_content, origen='file', destination_version='01')


        expected_lines_up = ["SPARQL DELETE FROM <test> {<http://example.com/role> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                             "SPARQL DELETE FROM <test> {<http://example.com/RoleOnSoapOpera> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                            ]

        expected_log_migration_up = """SPARQL INSERT INTO <http://example.com/> { [] owl:versionInfo "01"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "file"; <http://example.com/changes> "\\n<log>".};""" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        expected_lines_down = ["SPARQL INSERT INTO <test> {<http://example.com/RoleOnSoapOpera> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                             "SPARQL INSERT INTO <test> {<http://example.com/role> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . };",
                            ]

        expected_log_migration_down = """SPARQL DELETE FROM <http://example.com/> {?s ?p ?o} WHERE {?s owl:versionInfo "01"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "file"; <http://example.com/changes> "\\n<log>"; ?p ?o.};""" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        """SPARQL INSERT INTO <http://example.com/> { [] owl:versionInfo "01"; <http://example.com/endpoint> "endpoint"; <http://example.com/usuario> "user"; <http://example.com/ambiente> "localhost"; <http://example.com/produto> "test"; <http://example.com/commited> "%s"^^xsd:dateTime; <http://example.com/origen> "file"; <http://example.com/changes> "\\n<log>".};""" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines_up = query_up.strip(' \t\n\r').splitlines()
        self.assertEqual(4, len(lines_up))
        [self.assertTrue(l in lines_up) for l in expected_lines_up]
        self.assertEqual(lines_up[-1], expected_log_migration_up.replace('<log>', "\n".join(lines_up[0:-1]).replace('"','\\"').replace('\n', '\\n')))

        matchObj = re.search(r"SPARQL DELETE FROM <test> {(.*)} WHERE {(.*)};", query_up,  re.MULTILINE)
        sub_classes_01 = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(1))]
        sub_classes_02 = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(2))]
        [self.assertTrue((c in sub_classes_01) and (c in sub_classes_02)) for c in [
            '<http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf>',
            '<http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#maxQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera>',
            '<http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>',
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>'
            ]]


        lines_down = query_down.strip(' \t\n\r').splitlines()
        self.assertEqual(4, len(lines_down))
        [self.assertTrue(l in lines_down) for l in expected_lines_down]
        self.assertEqual(lines_down[-1], expected_log_migration_down.replace('<log>', "\n".join(lines_up[0:-1]).replace('"','\\"').replace('\n', '\\n')))

        matchObj = re.search(r"SPARQL INSERT INTO <test> { <http://example.com/role> <http://www.w3.org/2000/01/rdf-schema#subClassOf> \[(.*)\] };", query_down,  re.MULTILINE)
        sub_classes = [c.strip(' \t\n\r') for c in re.split(r" ; | \?s\. \?s ", matchObj.group(1))]
        [self.assertTrue(c in sub_classes) for c in [
            '<http://www.w3.org/2002/07/owl#minQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#maxQualifiedCardinality> "1"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>',
            '<http://www.w3.org/2002/07/owl#onClass> <http://example.com/RoleOnSoapOpera>',
            '<http://www.w3.org/2002/07/owl#onProperty> <http://example.com/play_a_role>',
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Restriction>'
            ]]

#    @patch('simple_virtuoso_migrate.virtuoso.Virtuoso.get_sparql')
#    def test_it_should_get_statments_to_execute_when_comparing_the_given_file_with_the_current_version(self, get_sparql_mock):
#        Virtuoso(self.config).get_statements("data.ttl", current_version='01', origen='file')
#        get_sparql_mock.assert_called_with(None, self.data_ttl_content, '01', None, 'file', 'data.ttl')

#    def test_it_should_raise_exception_when_getting_statments_of_an_unexistent_ttl_file(self):
#        self.assertRaisesWithMessage(Exception, 'migration file does not exist (current_file.ttl)', Virtuoso(self.config).get_statements, "current_file.ttl", current_version='01', origen='file')

    def test_it_should_raise_exception_if_specified_ontology_does_not_exists_on_migrations_dir(self):
        self.config.update('database_ontology', 'ontology.ttl')
        self.config.update('database_migrations_dir', '.')
        self.assertRaisesWithMessage(Exception, 'migration file does not exist (./ontology.ttl)', Virtuoso(self.config).get_ontology_by_version, '01')

    @patch('simple_virtuoso_migrate.virtuoso.Git')
    def test_it_should_return_git_content(self, git_mock):
        execute_mock = Mock(**{'return_value':'content'})
        git_mock.return_value = Mock(**{'execute':execute_mock})

        content = Virtuoso(self.config).get_ontology_by_version('version')
        self.assertEqual('content', content)
        git_mock.assert_called_with('.')
        execute_mock.assert_called_with(['git', 'show', 'version:test.ttl'])

    def test_it_should_print_error_message_with_correct_encoding(self):
        graph = """
        :is_part_of rdf:type owl:ObjectProperty ;
                     rdfs:label "É parte de outro objeto" ;
                     rdfs:domain absent:Prefix ;
                     rdfs:range absent:Prefix .
        """

        expected_message = 'Error parsing graph at line 2 of <>:\nBad syntax (Prefix ":" not bound) at ^ in:\n"\n        ^:is_part_of rdf:type owl:ObjectProperty ;\n                  ..."'
        self.assertRaisesWithMessage(Exception, expected_message, Virtuoso(self.config).get_sparql, current_ontology=None, destination_ontology=graph)


def export_git_file_side_effect(version):
    return "content_%s" % version


def temp_file_side_effect(content, reference):
    if reference == "file_down":
        return "filename_down.ttl"
    return "filename_up.ttl"


def command_call_side_effect(*args):
    if args[0].find("_up") > 0:
        return ("", "err")
    return ("out", "")

if __name__ == "__main__":
    unittest.main()
