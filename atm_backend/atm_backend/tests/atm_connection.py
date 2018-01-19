import xmlrpclib

def ATMConnection(config):
    host = 'localhost'
    port = config['atm']['port']
    atm_rpc = xmlrpclib.ServerProxy('http://' + host + ':' + str(port))
    return atm_rpc
