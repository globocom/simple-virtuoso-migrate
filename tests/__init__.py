import glob
import os
import unittest
import codecs
from simple_virtuoso_migrate.config import FileConfig
from StringIO import StringIO
from mock import patch


def create_file(file_name, content=None, encoding='utf-8'):
    f = codecs.open(file_name, 'w', encoding)
    if content:
        f.write(content)
    f.close()
    return file_name

def delete_files(pattern):
    filelist=glob.glob(pattern)
    for _file in filelist:
        os.remove(_file)

def create_config(host='localhost', username='root', password='', endpoint='migration_example', migrations_dir='.'):
    config_file = '''
DATABASE_HOST = '%s'
DATABASE_USER = '%s'
DATABASE_PASSWORD = '%s'
DATABASE_ENDPOINT = '%s'
DATABASE_MIGRATIONS_DIR = '%s'
''' % (host, username, password, endpoint, migrations_dir)
    create_file('test_config_file.conf', config_file)
    return FileConfig('test_config_file.conf')

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.stdout_mock = patch('sys.stdout', new_callable=StringIO)
        self.stdout_mock.start()

    def tearDown(self):
        self.stdout_mock.stop()
        delete_files('*.log')
        delete_files('*test_migration.migration')
        delete_files('migrations/*test_migration.migration')
        if os.path.exists(os.path.abspath('migrations')):
            os.rmdir(os.path.abspath('migrations'))
        if os.path.exists(os.path.abspath('test_config_file.conf')):
            os.remove(os.path.abspath('test_config_file.conf'))

    def assertRaisesWithMessage(self, excClass, excMessage, callableObj, *args, **kwargs):
        raisedMessage = ''
        try:
            callableObj(*args, **kwargs)
        except excClass, e:
            raisedMessage = str(e)
            if excMessage == raisedMessage:
                return

        if hasattr(excClass,'__name__'): excName = excClass.__name__
        else: excName = str(excClass)
        raise self.failureException, "%s not raised with message '%s', the message was '%s'" % (excName, excMessage, raisedMessage)
