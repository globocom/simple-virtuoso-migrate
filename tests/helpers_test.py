# coding: utf-8
import unittest
import os
import sys
from mock import patch
from tests import create_file, delete_files
from simple_virtuoso_migrate.helpers import Utils

class UtilsTest(unittest.TestCase):

    def setUp(self):
        config_file = '''
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''
DATABASE_NAME = 'migration_example'
ENV1_DATABASE_NAME = 'migration_example_env1'
DATABASE_MIGRATIONS_DIR = 'example'
UTC_TIMESTAMP = True
DATABASE_ANY_CUSTOM_VARIABLE = 'Some Value'
SOME_ENV_DATABASE_ANY_CUSTOM_VARIABLE = 'Other Value'
DATABASE_OTHER_CUSTOM_VARIABLE = 'Value'
'''
        create_file('sample.conf', config_file)
        create_file('sample.py', "import os\n%s" % config_file)

    def tearDown(self):
        delete_files('sample.conf')
        delete_files('sample.py')

    def test_it_should_extract_variables_from_a_config_file(self):
        variables = Utils.get_variables_from_file(os.path.abspath('sample.conf'))
        self.assertEqual('root', variables['DATABASE_USER'])
        self.assertEqual('migration_example_env1', variables['ENV1_DATABASE_NAME'])
        self.assertEqual('migration_example', variables['DATABASE_NAME'])
        self.assertEqual('example', variables['DATABASE_MIGRATIONS_DIR'])
        self.assertEqual(True, variables['UTC_TIMESTAMP'])
        self.assertEqual('localhost', variables['DATABASE_HOST'])
        self.assertEqual('', variables['DATABASE_PASSWORD'])

    def test_it_should_extract_variables_from_a_config_file_with_py_extension(self):
        variables = Utils.get_variables_from_file(os.path.abspath('sample.py'))
        self.assertEqual('root', variables['DATABASE_USER'])
        self.assertEqual('migration_example_env1', variables['ENV1_DATABASE_NAME'])
        self.assertEqual('migration_example', variables['DATABASE_NAME'])
        self.assertEqual('example', variables['DATABASE_MIGRATIONS_DIR'])
        self.assertEqual(True, variables['UTC_TIMESTAMP'])
        self.assertEqual('localhost', variables['DATABASE_HOST'])
        self.assertEqual('', variables['DATABASE_PASSWORD'])

    def test_it_should_not_change_python_path(self):
        original_paths = []
        for path in sys.path:
            original_paths.append(path)

        Utils.get_variables_from_file(os.path.abspath('sample.py'))

        self.assertEqual(original_paths, sys.path)


    def test_it_should_raise_exception_config_file_has_a_sintax_problem(self):
        f = open('sample.py', 'a')
        f.write('\nimport some_not_imported_module\n')
        f.close()
        try:
            Utils.get_variables_from_file(os.path.abspath('sample.py'))
            self.fail("it should not get here")
        except Exception, e:
            self.assertEqual("error interpreting config file 'sample.py': No module named some_not_imported_module", str(e))

    def test_it_should_raise_exception_config_file_not_exists(self):
        try:
            Utils.get_variables_from_file(os.path.abspath('unexistent.conf'))
            self.fail("it should not get here")
        except Exception, e:
            self.assertEqual("%s: file not found" % os.path.abspath('unexistent.conf'), str(e))

    def test_it_should_delete_compiled_module_file(self):
        Utils.get_variables_from_file(os.path.abspath('sample.py'))
        self.assertFalse(os.path.exists(os.path.abspath('sample.pyc')))

    def test_it_should_create_a_temporary_file_with_the_given_content(self):
        filename = None
        try:
            filename = Utils.write_temporary_file('content', 'content_reference')
            self.assertTrue(filename.index('/tmp/') == 0)
            self.assertEqual(open(filename, "r").read(), 'content')
        finally:
            if filename and os.path.exists(filename):
                os.unlink(filename)

    def test_it_should_support_utf8_content_on_temporary_file(self):
        filename = None
        try:
            filename = Utils.write_temporary_file('content çáéíóú'.decode('utf-8'), 'content_reference')
            self.assertEqual(open(filename, "r").read(), 'content çáéíóú')
        finally:
            if filename and os.path.exists(filename):
                os.unlink(filename)

    @patch('simple_virtuoso_migrate.helpers.tempfile.NamedTemporaryFile', side_effect=IOError("some error"))
    def test_it_should_raise_exception_when_an_error_happens_on_writing_temporary_file(self, named_temporary_file_mock):
        try:
            Utils.write_temporary_file('content', 'content_reference')
            self.fail("it should not get here")
        except Exception, e:
            self.assertEqual('could not create temporary file for content_reference -> (some error)', str(e))
