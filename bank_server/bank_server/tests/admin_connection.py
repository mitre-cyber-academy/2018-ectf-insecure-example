import xmlrpclib

def AdminConnection(config):
    host = 'localhost'
    port = config['admin']['port']
    admin_rpc = xmlrpclib.ServerProxy('http://' + host + ':' + str(port))
    return admin_rpc
