from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http    import AsgiHandler

from channels.auth import AuthMiddlewareStack
from rotel_rest.consumers import RotelConsumer

application = ProtocolTypeRouter({

  "http": AuthMiddlewareStack(
    URLRouter([
      url(r"^rotel/$", RotelConsumer),
      url(r"", AsgiHandler),
    ])
  ),

})

