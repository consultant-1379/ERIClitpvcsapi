from litp.migration import BaseMigration
from litp.migration.operations import AddRefCollection


class Migration(BaseMigration):
    version = '1.10.5'
    operations = [AddRefCollection('vcs-clustered-service', 'filesystems',
        'file-system'), ]
