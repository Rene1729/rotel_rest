from channels.consumer import SyncConsumer
import channels.layers
from asgiref.sync import async_to_sync

##from channels.generic import BaseConsumer
import serial
import time
import json
import re

#------------------------------------------------------------------------------
class RotelConsumer(SyncConsumer):

  # Structure of commands list:
  #     {rest command: [text to device,   RE for checking response from device ]
  commands = {'p-on':  [b'power_on!',     r'.*']
             ,'p-off': [b'power_off!',    r'.*']
             ,'p-tog': [b'power_toggle!', r'.*']
             ,'v-up':  [b'volume_up!',    r'volume=\d{1,2}!']
             ,'v-dwn': [b'volume_down!',  r'volume=\d{1,2}!']
             ,'m-tog': [b'mute!',         r'mute=(on|off)!'] #Mute Toggle
             ,'m-on':  [b'mute_on!',      r'mute=on!']
             ,'m-off': [b'mute_off!',     r'mute=off!']

             ,'rcd':   [b'rcd!',   r'source=analog_cd!'] #Source Rotel CD
             ,'cd':    [b'cd!',    r'source=analog_cd!']  #Source CD
             ,'coax1': [b'coax1!', r'source=coax1!'] #Source Coax 1
             ,'coax2': [b'coax2!', r'source=coax2!'] #Source Coax 2
             ,'opt1':  [b'opt1!',  r'source=opt1!'] #Source Optical 1
             ,'opt2':  [b'opt2!',  r'source=opt2!'] #Source Optical 2
             ,'aux1':  [b'aux1!',  r'source=aux1!'] #Source Aux 1
             ,'aux2':  [b'aux2!',  r'source=aux2!'] #Source Aux 2
             ,'tuner': [b'tuner!', r'source=tuner!'] #Source Tuner
             ,'phono': [b'phono!', r'source=phono!'] #Source Phono
             ,'usb':   [b'usb!',   r'source=usb!'] #Source Front USB

             ,'t-on':  [b'tone_on!',     r'tone_on!'] #Tone Controls On
             ,'t-off': [b'tone_off!',    r'tone_off!'] #Tone Controls Off
             ,'b-up':  [b'bass_up!',     r'bass=(+|-)\d{2}!'] #Bass Up
             ,'b-dwn': [b'bass_down!',   r'bass=(+|-)\d{2}!'] #Bass Down
             ,'b-10':  [b'bass_-10!',    r'bass=-10!'] #Set Bass to -10
             ,'b-0':   [b'bass_000!',    r'bass=000!'] #Set Bass to 0
             ,'b+10':  [b'bass_+10!',    r'base=+10!'] #Set Bass to +10
             ,'t-up':  [b'treble_up!',   r'treble=(+|-)\d{2}!'] #Treble Up
             ,'t-dwn': [b'treble_down!', r'treble=(+|-)\d{2}!'] #Treble Down
             ,'t-10':  [b'treble_-10!',  r'treble=-10!'] #Set Treble to -10
             ,'t-0':   [b'treble_000!',  r'treble=000!'] #Set Treble to 0
             ,'t+10':  [b'treble_+10!',  r'treble=+10!'] #Set Treble to +10
             ,'bal-0': [b'balance_000!', r'balance=000!'] #Set Balance to 0
             }

  read_commands = { 'disp':   [b'get_display!',        r'display=\d{3},(?P<value>.+)']
                  , 'pow':    [b'get_current_power!',  r'power=(?P<value>\w+)!']
                  , 'src':    [b'get_current_source!', r'source=(?P<value>\w+)!']
                  , 'tone':   [b'get_tone!',           r'tone=(?P<value>\w+)!']
                  , 'bass':   [b'get_bass!',           r'bass=(?P<value>\w+)!']
                  , 'treble': [b'get_treble!',         r'treble=(?P<value>\w+)!']
                  , 'bal':    [b'get_balance!',        r'balance=(?P<value>\w+)!']
                  , 'freq':   [b'get_current_freq!',   r'freq=(?P<value>\w+)!']
                  , 'play':   [b'get_play_status!',    r'play_status=(?P<value>\w+)!']
                  , 'v-max':  [b'get_volume_max!',     r'volume_max=(?P<value>\w+)!']
                  , 'v-min':  [b'get_volume_min!',     r'volume_min=(?P<value>\w+)!']
                  , 'vol':    [b'get_volume!',         r'volume=(?P<value>\w+)!']
                  , 't-max':  [b'get_tone_max!',       r'tone_max=(?P<value>\w+)!']
                  }

  set_commands = { 'vol':   ['volume_{:02d}!',   r'volume=\d{2}!']
                 , 'dim':   ['dimmer_{}!',       r'dimmer=\d!']
                 , 'bal-l': ['balance_L{:02d}!', r'balance=L\d{2}!']
                 , 'bal-r': ['balance_R{:02d}!', r'balance=R\d{2}!']
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
    time.sleep(0.5)

    for i in range(7):
      self.__send_command(b'dimmer!')



  #-----------------------------------------
  def rotel_sendcommand(self, message):

    channel_layer = channels.layers.get_channel_layer()

    try:
      if message['command'] == 'wakeup':
        self.rotel_wakeup('')
        response_value = 'OK'

      else: 
        command = self.commands[message['command']][0]
        re_check = self.commands[message['command']][1]
        print('In def rotel_sendcommand command: %s check: %s' % (command, re_check, ))

        received = self.__send_command(command)
        response_value = 'OK' if (re.search(re_check, received) != None) else 'ERR'

      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                , 'value':   response_value
                                                                })

    except KeyError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'KeyError in rotel_sendcommand: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_sendcommand'
                                                                })

  #-----------------------------------------
  def rotel_getvalue(self, message):

    channel_layer = channels.layers.get_channel_layer()
    try:
      command  = self.read_commands[message['command']][0]
      re_check = self.read_commands[message['command']][1]
      print('In def rotel_getvalue command: %s' % command )

      received = self.__send_command(command)

      re_obj = re.search(re_check, received)
      if re_obj != None:

        received_value = re_obj.group('value')

        async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                  , 'value':   received_value
                                                                })
      else:
        async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                  , 'value':   None
                                                                })

    except KeyError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'KeyError in rotel_getvalue: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_getvalue'
                                                                })

  #-----------------------------------------
  def rotel_setvalue(self, message):

    channel_layer = channels.layers.get_channel_layer()
    try:
      command  = self.set_commands[message['command']][0]
      re_check = self.set_commands[message['command']][1]

      value    = message['value']
      formated_command = command.format(value)

      print('In def rotel_settvalue command:%s, value:%s ->  %s' % (command, value, formated_command))

      received = self.__send_command(formated_command.encode())
      response_value = 'OK' if (re.search(re_check, received) != None) else 'ERR'

      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'response'
                                                                , 'value':   response_value
                                                              })
    except KeyError as err:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'KeyError in rotel_setvalue: {}'.format(err)
                                                                })
    except:
      async_to_sync(channel_layer.send)(message['return_chan'], { 'type':    'error'
                                                                , 'value':   'Unhandled exception in rotel_setvalue'
                                                                })


