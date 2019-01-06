import socket
import fcntl
import struct
def get_host_ip():
    myname = socket.getfqdn(socket.gethostname())
    myaa = socket.gethostbyname(myname)
    print myname
    print myaa

def get_local_ip(ifname='enp9s0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
    return socket.inet_ntoa(inet[20:24])




if __name__=='__main__':
    import time

    print u'\u7cbe\u51c6\u5fd7\u613f\u65b0\u7248\u672ccookie\u6d4b\u8bd5'