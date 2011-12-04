import logging

logger = logging.getLogger('managers.executor')


class Executor(object):
    '''
    Execute commands on host
    '''
    
    def __init__(self, connection, dry_run=False):
        self.host = connection.host
        self.dry_run = dry_run
        self.connection = connection
        
    def query(self, command):
        logger.info("Run `%s' on host `%s'" % (command, self.host))
        output = self.connection.execute(command)
        logger.debug("Command `%s' on host `%s' return:\n%s" % (command, self.host, output))
        return output
    
    def execute(self, command):
        if self.dry_run:
            logger.debug("Dry run `%s' on host `%s'" % (command, self.host))
            return ''
        else:
            return self.query(command)
    
    def put(self, localpath, remotepath):
        if self.dry_run:
            logger.debug("Dry put file `%s' to `%s' on host `%s'" % (localpath, remotepath, self.host))
            return ''
        else:
            return self.connection.put(localpath, remotepath)