import sys
from optparse import OptionParser
from psphere import client, managedobjects

p = OptionParser()

p.add_option('--vcenter',
    dest='vcenter',
    default='Required',
    help='Address of vcenter')

p.add_option('-u', '--username',
    dest='vusername',
    default='Required',
    help='Required: Username to login to vcenter')

p.add_option('-p', '--password',
    dest='vpassword',
    default='Required',
    help='Required: Password to login to vcenter')

p.add_option('-v', '--verbose',
    dest='verbose',
    default=False,
    action='store_true',
    help='Print debug messages')

(options, args) = p.parse_args()

def validate_args(options):
    if (options.vpassword or options.vusername) == 'Required':
        raise Exception("Required fields missing")

class vEnvironment(object):

    def __init__(self, vcenter=None, username=None, password=None, verbose=False):
        self.vcenter = vcenter
        self.username = username
        self.password = password
        self.verbose = verbose
        self.hosts = 0
        self.clusters = 0
        self.sockets = 0
        self.vms = 0
        self.ram = 0
        self.link = client.Client(self.vcenter, self.username, self.password)

    def verbose_msg(self, msg):
        if self.verbose:
            print "%s" % msg

    def getHostCount(self):
        self.verbose_msg("Collecting number of hosts")
        self.hosts = managedobjects.HostSystem.all(self.link)
        return len(self.hosts)

    def getClusterCount(self):
        self.verbose_msg("Collecting number of clusters")
        self.clusters = managedobjects.ComputeResource.all(self.link)
        return len(self.clusters)

    def getSocketCount(self):
        self.verbose_msg("Collecting number of sockets in cluster")
        if not self.hosts:
            self.hosts = self.getHostCount()
        for host in self.hosts:
            self.sockets += host.summary.hardware.numCpuPkgs

        return self.sockets

    def getVMCount(self):
        self.verbose_msg("Collecting number of vms")
        self.vms = managedobjects.VirtualMachine.all(self.link)
        return len(self.vms)

    def getTotalRamProvisioned(self):
        self.verbose_msg("Collecting total amount of provisioned ram in GB")
        if not self.hosts:
            self.hosts = self.getHostCount()
        for host in self.hosts:
            for vm in host.vm:
                self.ram += vm.summary.config.memorySizeMB
        return (self.ram / 1024)

if __name__ == '__main__':
    validate_args(options)

    venv = vEnvironment(options.vcenter, options.vusername, options.vpassword,
                    options.verbose)

    print "Number of hosts: %s" % venv.getHostCount()
    print "\tNumber of sockets: %s" % venv.getSocketCount()
    print "Number of clusters: %s" % venv.getClusterCount()
    print "Number of VMs: %s" % venv.getVMCount()
    print "Total RAM provisioned: %s" % venv.getTotalRamProvisioned()