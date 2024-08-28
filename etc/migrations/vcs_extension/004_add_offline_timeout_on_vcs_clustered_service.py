from litp.migration import BaseMigration
from litp.migration.operations import AddProperty


class Migration(BaseMigration):
    version = '1.15.4'
    operations = [
        AddProperty('vcs-clustered-service', 'offline_timeout', '300'),
    ]
