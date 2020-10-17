from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
import json

channel_layer = get_channel_layer()

def home(request):
  return TemplateResponse(request, 'home.html')


def rotel_sendcommand(request, command):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_sendcommand'
                                                     , 'command':      command
                                                     , 'return_chan':  return_channel
                                                     })

  response_message = async_to_sync(channel_layer.receive)(return_channel)

  # return HttpResponse(json.dumps(response_message), content_type='text/plain')
  return JsonResponse(response_message)


def rotel_getvalue(request, command):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_getvalue'
                                                     , 'command':      command
                                                     , 'return_chan':  return_channel
                                                     })

  response_message = async_to_sync(channel_layer.receive)(return_channel)

  # return HttpResponse(json.dumps(response_message), content_type='text/plain')
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


def rotel_wakeup(request):
  return_channel = async_to_sync(channel_layer.new_channel)()
  async_to_sync(channel_layer.send)('rotel-channel', { 'type':         'rotel_wakeup'
                                                     , 'return_chan':  return_channel
                                                     })

  # return HttpResponse('OK', content_type='text/plain')
  return JsonResponse({'OK'})
