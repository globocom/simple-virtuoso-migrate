Simple Virtuoso migrate "quick" documentation
======


Quick start
---

simple-virtuoso-migrate is damn simple. The best way to understand how it works is installing and using it.

You can install it by :

```bash
$ pip install simple-virtuoso-migrate
```

Now, copy the file sitecustomize.py to Python library directory. After installing, for usage tips type:

```bash
$ virtuoso-migrate --help
```

Understanding how it works
---

virtuoso-migrate is a ontology versioning and migration tool inspired on simple-db-migrate.

This tool helps you to manage and track your ontology changes.

The main difference between simple-db-migrate and this tool is that while simple-db-migrate uses multiple migrations files, virtuoso-migrate basically deals with versions (git tags) of one single ttl file. The migrations (i.e.,  actions to be performed) are inferred through the comparison of two versions of the ttl file.

A little explanation about load options:

    -g  <version>   Use this option to evolve your ontology.

Example:

```bash
$ virtuoso-migrate -c /projects/confs/confg.cnf -g 2.0.0
```

```python
def validate_this_paragraph:
    pass
```

Note: Use this option to evolve your ontology. Inform target version of the ontology based on your git tag.
As a result it compares the current version of your local ontology with the current version in the target repository.
If you do not inform a load parameter:

    -i <file_name>  Use this option when you want to load data into your graph.

```bash
$ virtuoso-migrate -c /projects/confs/config.cnf -i /projects/dumps/load.ttl
```

It loads the content of a given file into the database without any verification.

Debugging a migration performed through the migration process:

    --showsparql   Use this option to make Virtuoso-migrate show all the commands that
                   were executed on the database. It increases the output messages

Similarly, you can showing SPARQL queries without executing them:

```bash
$ virtuoso-migrate -c /projects/confs/config.cnf -i /projects/dumps/load.ttl --showsparql
```


    --showsparqlonly  Use this option to make simple-virtuoso-migrate show all the comands but without executing them.
                      It doesn't make any changes.

```bash
$ virtuoso-migrate -c /projects/confs/loads.cnf -i /projects/dumps/loads.ttl --showsparqlonly
```

Note: If no load is specified it will migrate to the last version of your ontology.

Configuration file parameters
-----

One can easily configure file parameters simply by:

    DATABASE_HOST             Virtuoso instance host's name
    DATABASE_USER             Your database login name
    DATABASE_PASSWORD         Your database password.
                              In some cases you will not want to write database passwords in the config files 
                              (e.g. production databases passwords). You can configure the password to be asked 
                              for you in the command line setting up this parameter with "<<ask_me>>".
    DATABASE_PORT             Virtuoso isql's port
    DATABASE_ENDPOINT         Sparql endpoit address . "http://localhost:8890/sparql"
    DATABASE_GRAPH            Graph name
    DATABASE_MIGRATIONS_DIR   Absolute path of the ontology ttl file.
    DATABASE_ONTOLOGY         Ontology ttl file name.


Querying your migrations
-----

Migration history is keeped on the graph <http://migration.example.com/>.

Data properties description:

          owl#versionInfo   Ontology version
          produto           Product name (i.e, graph name)
          origem            <-m / -i >
          commited          When the migration was performed
          endpoint          Sparql endpoint used
          usuario           Username used
          ambiente          Virtuoso instance name

Useful queries:
---

Listing all migrations performed on graph http://example.com/class/ 
during the period between 2012-07-06 and 2012-07-03

```sql
PREFIX mig: <http://example.com/>
SELECT DISTINCT ?source ?endpoint ?user ?env ?when
FROM <http://migration.example.com/>
WHERE {
    ?s  ?p            ?o;
        mig:produto   'http://example.com/class/';
        mig:origen    ?source;
        mig:commited  ?when;
        mig:endpoint  ?endpoint;
        mig:ambiente  ?env;
        mig:usuario   ?user.
        FILTER ( ?when > "2012-06-30T00:00:00"^^xsd:dateTime && 
                 ?when < "2012-07-03T00:00:00"^^xsd:dateTime ).
}  ORDER BY ?when
```

That's it. Enjoy!
