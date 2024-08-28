from litp.migration import BaseMigration
from litp.migration.operations import AddCollection

class Migration(BaseMigration):
    version = '1.10.3'
    operations = [AddCollection('vcs-cluster', 'network_hosts', 'vcs-network-host')]
