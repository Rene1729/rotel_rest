from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.http    import AsgiHandler

from channels.auth import AuthMiddlewareStack
from rotel_rest.consumers import RotelConsumer

application = ProtocolTypeRouter({

  'channel': ChannelNameRouter({'rotel-channel': RotelConsumer, }),

  'http': AuthMiddlewareStack(
    URLRouter([
  ##    url(r'^rotel/$', WebConsumer),
      url(r'', AsgiHandler),
    ])
  ),

})

