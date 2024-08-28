from litp.migration import BaseMigration
from litp.migration.operations import AddCollection


class Migration(BaseMigration):
    version = '1.10.2'
    operations = [AddCollection('vcs-clustered-service', 'ipaddresses',
                                'vip')]
