import unittest

from drbd_creator.parsers import DrbdConfigParser, LvmConfigParser


DRBD_CONFIG = """
global {
    minor-count 128;
}
common {
    protocol               C;
    disk {
        fencing          resource-only;
    }
    handlers {
        fence-peer       /usr/lib/drbd/crm-fence-peer.sh;
        after-resync-target /usr/lib/drbd/crm-unfence-peer.sh;
    }
}
resource msk1-g-cm1 {
  net {
    allow-two-primaries;
    max-buffers 8000;
    max-epoch-size 8000;
    sndbuf-size 0;
  }
  syncer {
    rate 66M;
  }
  disk {
    no-disk-barrier;
    no-disk-flushes;
  }
  on msk1-vmm1 {
    device    /dev/drbd2;
    disk      /dev/vg2-big/msk1-g-cm1;
    address   192.168.0.2:55002;
    meta-disk internal;
  }
  on msk1-vmm2 {
    device    /dev/drbd2;
    disk      /dev/vg2-big/msk1-g-cm1;
    address   192.168.0.1:55002;
    meta-disk internal;
  }
}
"""


LVM_LIST = """
  LV          VG      
  config      vg0-sys 
  drbd-config vg0-sys 
  home        vg0-sys 
  images      vg0-sys 
  root        vg0-sys 
  var         vg0-sys 
  msk1-g-ad1  vg1-fast
  msk1-g-cm1  vg2-big 
  msk1-g-dev1 vg2-big 
  msk1-g-egw1 vg2-big 
  msk1-g-igw1 vg2-big 
  msk1-g-igw2 vg2-big 
"""


class TestLvmConfig(unittest.TestCase):
    
    def setUp(self):
        self.config = LvmConfigParser.create(LVM_LIST)
    
    def test_parser(self):
        self.assertTrue(self.config)


class TestDrbdConfig(unittest.TestCase):
    
    def setUp(self):
        self.config = DrbdConfigParser.create(DRBD_CONFIG)
    
    def test_parser(self):
        self.assertTrue(self.config)
        self.assertTrue(self.config['msk1-g-cm1'].params)
        self.assertTrue(self.config['msk1-g-cm1'].hosts)


if __name__ == '__main__':
    unittest.main()