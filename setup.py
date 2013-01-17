from setuptools import setup, find_packages
from distutils import config
import simple_virtuoso_migrate


setup(
    name = "simple-virtuoso-migrate",
    version = simple_virtuoso_migrate.SIMPLE_VIRTUOSO_MIGRATE_VERSION,
    packages = find_packages(),
    author = "Percy Rivera",
    author_email = "priverasalas@gmail.com",
    description = "simple-virtuoso-migrate is a Virtuoso database migration tool inspired on simple-db-migrate.",
    license = "Apache License 2.0",
    keywords = "database migration tool virtuoso",
    url = "http://github.com/globocom/simple-virtuoso-migrate/",
    long_description = "simple-virtuoso-migrate is a Virtuoso database migration tool inspired on simple-db-migrate. This tool helps you easily refactor and manage your ontology T-BOX. The main difference is that simple-db-migrate are intended to be used for mysql, ms-sql and oracle projects while simple-virtuoso-migrate makes it possible to have migrations for Virtuoso",
    tests_require=['coverage==3.5.1', 'mock==0.8.0', 'nose==1.1.2'],
    install_requires=['GitPython>=0.3 ', 'paramiko==1.9.0','rdflib==3.2.1', 'rdfextras==0.2', 'rdflib-sparqlstore==0.1'],

    # generate script automatically
    entry_points = {
        'console_scripts': [
            'virtuoso-migrate = simple_virtuoso_migrate.run:run_from_argv',
        ],
    }
)
