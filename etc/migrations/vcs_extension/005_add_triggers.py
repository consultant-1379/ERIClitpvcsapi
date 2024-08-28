from litp.migration import BaseMigration
from litp.migration.operations import AddCollection


class Migration(BaseMigration):
    version = '1.17.2'
    operations = [AddCollection('vcs-clustered-service', 'triggers',
                                'vcs-trigger')]
