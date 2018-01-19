import xmlrpclib

def BankConnection(config):
    host = 'localhost'
    port = config['bank']['port']
    bank_rpc = xmlrpclib.ServerProxy('http://' + host + ':' + str(port))
    return bank_rpc
