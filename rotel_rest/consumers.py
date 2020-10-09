from channels.consumer import SyncConsumer
# from django.http import HttpResponse

##from channels.generic import BaseConsumer
import serial
import time
import json

class RotelConsumer(SyncConsumer):

#  method_mapping = {"rotel.get_value": "get_value",
#                    "rotel.set_value": "set_value",
#                    "rotel.wakeup": "wakeup",
#                   }

  ser = serial.Serial( port='/dev/serial0'
                     , baudrate = 115200
                     , rtscts = False
                     , dsrdtr = False
                     , xonxoff = False
                     , parity=serial.PARITY_NONE
                     , stopbits=serial.STOPBITS_ONE
                     , bytesize=serial.EIGHTBITS
                     , timeout=0
                     )
  
  def rotel_wakeup(self, message, **kwargs):
    self.ser.write(b'power_on!')
    self.ser.write(b'display_update_manual!')

    counter=10

    while counter>0:
      self.ser.write(b'dimmer!')
      self.ser.flush()
      time.sleep(0.05)
  
      buff = self.ser.read(10)
      while len(buff) > 0:
        buff = self.ser.read(10)

      counter -= 1


      
  def rotel_getValue(self, command):
    self.ser.write(command)
    
    received = ''
    buff = self.ser.read(10)
    while len(buff) > 0:
      received += buff.decode()
      buff = self.ser.read(10)

    data = {}
    data['command'] = command
    data['data'] = received

    return data



  def rotel_setValue(self, message, **kwargs):
    pass



  def http_request(self, message, **kwargs):

    asgiResponse = { 'type':    'http.response.start',
                     'status':  200,
                     'headers': [[b'content_type',b'text/plain']],
                   }
    self.send(asgiResponse)

    data = self.rotel_getValue(b'dimmer!')

    asgiResponse = { 'type': 'http.response.body',
                     'body': json.dumps(data).encode(),
                     'more_body': False,
                   }
    self.send(asgiResponse)



  def http_disconnect(self, message, **kwargs):
    pass
