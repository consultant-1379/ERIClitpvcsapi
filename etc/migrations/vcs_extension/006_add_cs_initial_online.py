from litp.migration import BaseMigration
from litp.migration.operations import AddProperty


class Migration(BaseMigration):
    version = '1.22.2'
    operations = [
        AddProperty('vcs-cluster', 'cs_initial_online', 'on'),
    ]
