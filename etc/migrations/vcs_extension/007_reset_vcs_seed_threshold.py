from litp.migration import BaseMigration
from litp.migration.operations import AddProperty


class Migration(BaseMigration):
    version = '1.37.1'
    operations = [
        AddProperty('vcs-cluster', 'vcs_seed_threshold', None),
    ]
