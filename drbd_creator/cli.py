import logging
import traceback
import sys
import os
from optparse import OptionParser

from .utils import debug
from .dispatcher import Dispatcher
from .ssh import Connection

# create logger
logger = logging.getLogger('main')

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    
    parser.add_option("-n", "--name", dest='name', 
                      help="resource name (LV)")
    
    parser.add_option("-s", "--size", dest='size', 
                      help="resource size")
    
    parser.add_option("-g", "--group", dest='group', 
                      help="volume group (VG)")
    
    parser.add_option("-t", "--dry-run", 
                      action="store_true", dest="dry_run")
    
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    
    parser.add_option("-c", "--config-template", dest="template",
                      default="template.res")
    
    parser.add_option("-d", "--host", dest="host",
                      action="append", type="string")
    
    parser.add_option("-u", "--user", dest="user", default="root",
                      action="store", type="string")
    
    parser.add_option("-k", "--private-key", dest="private_key", default='',
                      action="store", type="string")
    
    parser.add_option("-r", "--port", dest="port", default=22,
                      action="store", type="int")
    
    (options, _args) = parser.parse_args()
    
    if not options.name:
        parser.error("resource name missing")
    if not options.size:
        parser.error("size missing")
    if not options.group:
        parser.error("volume group missing")
    if not options.host:
        parser.error("host is missing (--host)")
    if len(options.host) < 2:
        parser.error("host count must be greater than 2")
    if not options.user:
        parser.error("user is missing (--user)")
    if not options.port:
        parser.error("port is missing (--port)")
    
    if options.verbose or options.dry_run:
        debug()
        
    primary_host = '192.168.0.171'
    
    logger.info('Connect to %s' % ", ".join(options.host))
    default_params = {'username': options.user, 'password': '', 
                      'private_key': options.private_key or None,
                      'port': options.port}
    hosts_params = map(lambda host: dict(default_params.items() + [('host', host)]), options.host)

    try:
        template = open(os.path.expanduser(options.template)).read()
        
        Dispatcher(name=options.name, 
                size=options.size, 
                group=options.group,
                primary_host=primary_host,
                connections=map(lambda kwargs: Connection(**kwargs), hosts_params),
                template = template,
                dry_run=options.dry_run).process()
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
