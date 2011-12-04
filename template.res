resource %(name)s {
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
  on orb1-vmm1 {
    device    /dev/drbd%(minor)d;
    disk      %(lv_path)s;
    address   192.168.212.2:%(port)d;
    meta-disk internal;
  }
  on orb1-vmm2 {
    device    /dev/drbd%(minor)d;
    disk      %(lv_path)s;
    address   192.168.212.1:%(port)d;
    meta-disk internal;
  }
}