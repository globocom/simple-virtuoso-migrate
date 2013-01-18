import os
from git import Git, Repo, NoSuchPathError, InvalidGitRepositoryError


class SimpleVirtuosoMigrate(object):

    def __init__(self, config):
        self._migrations_dir = config.get("database_migrations_dir")
        self.all_migrations = None

    def get_all_migrations(self):
        if self.all_migrations:
            return self.all_migrations

        migrations = []

        try:
            repo = Repo(self._migrations_dir)
            for git_tag in repo.tags:
                migrations.append(git_tag.name)
        except NoSuchPathError:
            raise Exception("directory not found ('%s')" %
                                                self._migrations_dir)
        except InvalidGitRepositoryError:
            raise Exception("invalid git repository ('%s')" %
                                                 self._migrations_dir)

        if len(migrations) == 0:
            raise Exception("no migration found")

        self.all_migrations = migrations
        return self.all_migrations

    def check_if_version_exists(self, version):
        return version in self.get_all_migrations()

    def latest_version_available(self):
        return Git(self._migrations_dir).execute(["git",
                                                  "describe",
                                                  "--abbrev=0",
                                                  "--tags"])
