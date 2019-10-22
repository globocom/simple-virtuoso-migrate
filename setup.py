from setuptools import setup, find_packages
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
    tests_require=['coverage==3.7', 'mock==1.0.1', 'nose==1.3.0'],
    install_requires=['GitPython>=0.3 ', 'paramiko==2.0.9', 'rdflib==3.4.0', 'rdfextras==0.4', 'rdflib-sparqlstore==0.2'],

    # generate script automatically
    entry_points = {
        'console_scripts': [
            'virtuoso-migrate = simple_virtuoso_migrate.run:run_from_argv',
        ],
    }
)
