from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
import json

channel_layer = get_channel_layer()

def home(request):
  return TemplateResponse(request, 'home.html')


def rotel_rest(request):

  response_message = {}
  json_request=json.loads(request.body)
  ## print('rotel_rest: %s' % json_request) 

  req_type = json_request['type']

  if req_type == 'rotel_sendcommand' or req_type == 'rotel_getvalue':
    
    return_channel = async_to_sync(channel_layer.new_channel)()
    async_to_sync(channel_layer.send)('rotel-channel', { 'type':         req_type
                                                       , 'command':      json_request['command']
                                                       , 'return_chan':  return_channel
                                                       })
    response_message = async_to_sync(channel_layer.receive)(return_channel)

  elif  req_type == 'rotel_setvalue':

    return_channel = async_to_sync(channel_layer.new_channel)()
    async_to_sync(channel_layer.send)('rotel-channel', { 'type':         req_type
                                                       , 'command':      json_request['command']
                                                       , 'value':        json_request['value']
                                                       , 'return_chan':  return_channel
                                                       })
    response_message = async_to_sync(channel_layer.receive)(return_channel)

  return JsonResponse(response_message)



def rotel_sendcommand(request, command):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_sendcommand'
                                                     , 'command':      command
                                                     , 'return_chan':  return_channel
                                                     })

  response_message = async_to_sync(channel_layer.receive)(return_channel)
  return JsonResponse(response_message)



def rotel_getvalue(request, command):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_getvalue'
                                                     , 'command':      command
                                                     , 'return_chan':  return_channel
                                                     })

  response_message = async_to_sync(channel_layer.receive)(return_channel)
  return JsonResponse(response_message)



def rotel_setvalue(request, command, value):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_setvalue'
                                                     , 'command':      command
                                                     , 'value':        value
                                                     , 'return_chan':  return_channel
                                                     })

  response_message = async_to_sync(channel_layer.receive)(return_channel)
  return HttpResponse(json.dumps(response_message), content_type='text/plain')

