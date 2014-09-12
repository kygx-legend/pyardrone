#!/usr/bin/python

import socket
import struct

REMOTE_IP = '192.168.1.1'
LOCAL_IP = '192.168.1.2'
MULTICAST_IP = '224.1.1.1'

CMD_PORT = 5556
NAV_PORT = 5554
CFG_PORT = 5559
VIDEO_PORT = 5555

cmd_socket = None
nav_socket = None
cfg_socket = None
video_socket = None

cmd_seq = 1

def float2int(f):
  return struct.unpack("=i", struct.pack("=f", f))[0]

def build_command(method, params):
  global cmd_seq

  if not params:
    params = []

  params2 = []
  for param in params:
    if type(param) == float:
      params2.append(str(float2int(param)))
    elif type(param) == int:
      params2.append(str(param))
    else:
      params2.append('\\"' + str(param) + '\\"')

  params_str = ','.join([str(cmd_seq)] + params2)
  cmd_seq += 1

  return 'AT*' + method + '=' + params_str + '\r'

def connect_cmd():
  global cmd_socket

  if cmd_socket is not None:
    return

  cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  cmd_socket.bind((LOCAL_IP, CMD_PORT))
  cmd_socket.connect((REMOTE_IP, CMD_PORT))

def disconnect_cmd():
  global cmd_socket

  if cmd_socket is not None:
    cmd_socket.close()
    cmd_socket = None

def connect_nav():
  global cmd_socket, nav_socket

  if cmd_socket is None:
    connect_cmd()

  cmd_socket.send(build_command('CONFIG', ('general:navdata_demo', '"TRUE"',)))
  
  nav_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  nav_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  nav_socket.bind(('', NAV_PORT))
  group_bin = socket.inet_aton(MULTICAST_IP)
  iface_bin = socket.inet_aton(LOCAL_IP)
  nav_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group_bin + iface_bin)

  while True:
    data, sender = nav_socket.recvfrom(100)
    print "<<<====="
    print str(sender)
    print repr(data)
    print "=====>>>"

def disconnect_nav():
  global nav_socket

  if nav_socket is not None:
    nav_socket.close()
    nav_socket = None

def connect_cfg():
  pass

def connect_video():
  pass

def take_off():
  global cmd_socket

  if cmd_socket is None:
    return

  cmd_socket.send(build_command('REF', (290718208,)))

def landing():
  global cmd_socket

  if cmd_socket is None:
    return

  cmd_socket.send(build_command('REF', (290717696,)))


if __name__ == '__main__':
  print build_command('CONFIG', ('general:navdata_demo', 'TRUE',))
  connect_cmd()

  while True:
    print "CMD: %d" % cmd_seq
    cmd = raw_input()
    if cmd == 'q':
      disconnect_cmd()
      disconnect_nav()
      print 'bye'
      break
    elif cmd == 'n':
      connect_nav()
    elif cmd == 't':
      take_off()
    elif cmd == 'l':
      landing()

