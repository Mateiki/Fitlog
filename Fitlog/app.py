from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

# monkey.patch_all() é crucial para o gevent funcionar corretamente
monkey.patch_all()

from bottle import app
import beaker.middleware
import controllers.rotas

# Configurações da sessão
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,
    'session.data_dir': './session_data',
    'session.auto': True
}

# Cria a aplicação com o middleware de sessão
application = beaker.middleware.SessionMiddleware(app(), session_opts)

# Inicia o servidor GeventWebSocket
if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), application, handler_class=WebSocketHandler)
    print("Servidor WebSocket iniciado em http://localhost:8080...")
    server.serve_forever()