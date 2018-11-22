from nameserver import NameServer
from dataserver import DataServer

numReplicate = 3

def main():
    global numReplicate
    ns = NameServer(numReplicate)
    ds1 = DataServer("node1")
    ds2 = DataServer("node2")
    ds3 = DataServer("node3")
    ds4 = DataServer("node4")
    
    ns.add(ds1)
    ns.add(ds2)
    ns.add(ds3)
    ns.add(ds4)

    ds1.start()
    ds2.start()
    ds3.start()
    ds4.start()

    # print("===")
    ns.operator()
    '''
    print("?????")
    ds1.join()
    ds2.join()
    ds3.join()
    ds4.join()
    '''

    return 0

if __name__ == '__main__':
    main()
