from channels.consumer import SyncConsumer
import channels.layers
from asgiref.sync import async_to_sync

##from channels.generic import BaseConsumer
import serial
import time
import json


#------------------------------------------------------------------------------
class RotelConsumer(SyncConsumer):

  commands = {'p-on': b'power_on!'
             ,'p-off': b'power_off!'
             ,'p-tog': b'power_toggle!'
             ,'v-up': b'volume_up!'
             ,'v-dwn': b'volume_down!'
             ,'m-tog': b'mute!' #Mute Toggle
             ,'m-on': b'mute_on!'
             ,'m-off': b'mute_off!'

             ,'rcd': b'rcd!' #Source Rotel CD
             ,'cd': b'cd!'  #Source CD
             ,'c1': b'coax1!' #Source Coax 1
             ,'c2': b'coax2!' #Source Coax 2
             ,'o1': b'opt1!' #Source Optical 1
             ,'o2': b'opt2!' #Source Optical 2
             ,'a1': b'aux1!' #Source Aux 1
             ,'a2': b'aux2!' #Source Aux 2
             ,'tun': b'tuner!' #Source Tuner
             ,'ph': b'phono!' #Source Phono
             ,'usb': b'usb!' #Source Front USB

             ,'t-on': b'tone_on!' #Tone Controls On
             ,'t-off': b'tone_off!' #Tone Controls Off
             ,'b-up': b'bass_up!' #Bass Up
             ,'b-dwn': b'bass_down!' #Bass Down
             ,'b-10': b'bass_-10!' #Set Bass to -10
             ,'b-0': b'bass_000!' #Set Bass to 0
             ,'b+10': b'bass_+10!' #Set Bass to +10
             ,'t-up': b'treble_up!' #Treble Up
             ,'t-dwn': b'treble_down!' #Treble Down
             ,'t-10': b'treble_-10!' #Set Treble to -10
             ,'t-0': b'treble_000!' #Set Treble to 0
             ,'t+10': b'treble_+10!' #Set Treble to +10
             ,'bal-0': b'balance_000!' #Set Balance to 0

             }

  read_commands = { 'disp': b'get_display!'
                  , 'pow': b'get_current_power!'
                  , 'src': b'get_current_source!'
                  , 'tone': b'get_tone!'
                  , 'bass': b'get_bass!'
                  , 'treble': b'get_treble!'
                  , 'bal': b'get_balance!'
                  , 'freq': b'get_current_freq!'
                  , 'play': b'get_play_status!'
                  , 'v-max': b'get_volume_max!'
                  , 'v-min': b'get_volume_min!'
                  , 'vol': b'get_volume!'
                  , 't-max': b'get_tone_max!'
                  }

  set_commands = { 'vol': 'volume_{:02d}!'
                 , 'dim': 'dimmer_{}!'
                 , 'bal-l': 'balance_L{:02d}!'
                 , 'bal-r': 'balance_R{:02d}!'
                 }

  #-----------------------------------------
  def __init__(self, scope):
    super(SyncConsumer, self).__init__(scope)

    self.ser = serial.Serial( port='/dev/serial0'
                            , baudrate = 115200
                            , rtscts = False
                            , dsrdtr = False
                            , xonxoff = False
                            , parity=serial.PARITY_NONE
                            , stopbits=serial.STOPBITS_ONE
                            , bytesize=serial.EIGHTBITS
                            , timeout=0
                            )


  #-----------------------------------------
  def __send_command(self, command):
    print('send serial command: %s' % command )
    self.ser.write(command)
    self.ser.flush()
    time.sleep(0.05)
    
    received = ''
    buff = self.ser.read(10)
    while len(buff) > 0:
      received += buff.decode()
      buff = self.ser.read(10)

    
    print('response: %s' % received)
    return received


  #-----------------------------------------
  def rotel_wakeup(self, message):
    print('In rotel wakeup')

    self.__send_command(b'power_on!')
    self.__send_command(b'display_update_manual!')

    for i in range(7):
      self.__send_command(b'dimmer!')



  #-----------------------------------------
  def rotel_sendcommand(self, message):

    channel_layer = channels.layers.get_channel_layer()
    try:
      command = self.commands[message['command']]
      print('In def rotel_sendcommand command: %s' % command )

      received = self.__send_command(command)
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                , 'value':   received
                                                                })

    except OSError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Error in rotel_sendcommand: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_sendcommand'
                                                                })

  #-----------------------------------------
  def rotel_getvalue(self, message):

    channel_layer = channels.layers.get_channel_layer()
    try:
      command = self.read_commands[message['command']]
      print('In def rotel_getvalue command: %s' % command )

      received = self.__send_command(command)
      channel_layer = channels.layers.get_channel_layer()
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                , 'value':   received
                                                              })
    except OSError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Error in rotel_getvalue: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_getvalue'
                                                                })

  #-----------------------------------------
  def rotel_setvalue(self, message):

    channel_layer = channels.layers.get_channel_layer()
    try:
      command = self.set_commands[message['command']]
      value   = message['value']
      formated_command = command.format(value)

      print('In def rotel_settvalue command:%s, value:%s ->  %s' % (command, value, formated_command))

      received = self.__send_command(formated_command.encode())
      channel_layer = channels.layers.get_channel_layer()
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                , 'value':   received
                                                              })
    except OSError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Error in rotel_setvalue: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_setvalue'
                                                                })


