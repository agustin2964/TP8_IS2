""" Trabajo practico 7 - IS2 - UADERFCyT
re-factorizacion del codigo del TP6"""
#copyright UADERFCyT-IS2©2024 todos los derechos reservados

import json
import sys

from datetime import datetime

class JsonReader:
    """ clase JsonReader, implementa el patron singleton
    y cumple la misma funcion que la funcion getJason"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JsonReader, cls).__new__(cls)
        return cls._instance
    def get_json(self, jsonfile, jsonkey='token1'):
        """ cumple la misma funcion que la funcion getJason,
        pero ahora es un metodo de la clase JsonReader """
        with open(jsonfile, 'r', encoding='utf-8') as myfile:
            data = json.load(myfile)
        return data[jsonkey]

class JsonWriter:
    """ clase JsonWriter, implementa el patron singleton """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JsonWriter, cls).__new__(cls)
        return cls._instance
    def write_json(self, jsonfile, jsonkey, jsonvalue):
        """ reescribe el valor de jsonkey por jsonvalue en el archivo jsonfile """
        with open(jsonfile, 'r', encoding='utf-8') as myfile:
            data = json.load(myfile)
        data[jsonkey] = jsonvalue
        with open(jsonfile, 'w', encoding='utf-8') as myfile:
            json.dump(data, myfile, indent=4)

class Historial:
    """ Clase historial, implementa el patron singleton e iterator """
    _instance = None
    num_pedidos = 0
    pagos = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Historial, cls).__new__(cls)
        return cls._instance
    def guardar_pago(self, token, monto):
        """ guarda un pago en el historial, con el numero de pedido, el token utilizado,
        el monto y la fecha y hora del pago """
        self.num_pedidos += 1
        self.pagos.append({
            'pedido': self.num_pedidos,
            'token': token,
            'monto': monto,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    def __iter__(self):
        yield from self.pagos

class AbstractHandler:

    """ Clase AbstractHandler: clase abstracta para el patron chain of responsibility"""
    def __init__(self, nxt):

        """ define el siguiente handler en la cadena de responsabilidad """

        self._nxt = nxt

    def handle(self, request):

        """ intenta procesar la solicitud, devuelve true si se procesa,
        sino delega al siguiente handler """

        handled = self.process_request(request)

        if not handled:
            self._nxt.handle(request)

    def process_request(self, request):

        """throws a NotImplementedError"""

        raise NotImplementedError('First implement it !')

class HandlerA(AbstractHandler):
    """ handler concreto del token1 """
    def process_request(self, request):
        """ procesa la solicitud si la cuenta token1 tiene fondos suficientes,
        sino devuelve false para delegar al siguiente handler """
        balance = JsonReader().get_json('./sitedata.json', 'token1')
        if request <= balance:
            JsonWriter().write_json('./sitedata.json', 'token1', balance - request)
            Historial().guardar_pago('token1', request)
            print(f"${request} debitado de token1 por {self.__class__.__name__}")
            return True
        return False

class HandlerB(AbstractHandler):
    """ handler concreto del token2 """
    def process_request(self, request):
        """ procesa la solicitud si la cuenta token2 tiene fondos suficientes,
        sino devuelve false para delegar al siguiente handler """
        balance = JsonReader().get_json('./sitedata.json', 'token2')
        if request <= balance:
            JsonWriter().write_json('./sitedata.json', 'token2', balance - request)
            Historial().guardar_pago('token2', request)
            print(f"${request} debitado de token2 por {self.__class__.__name__}")
            return True
        return False

class DefaultHandler(AbstractHandler):
    """ handler concreto por defecto """
    def process_request(self, request):
        """ imprime un mensaje indicando que no se pudo procesar la solicitud """
        print(f"No se pudo procesar la solicitud de ${request} por falta de fondos")
        return True

class User:
    """ clase User, cliente del patron chain of responsibility """
    def __init__(self):
        """ define la cadena de responsabilidad """
        self.handler = HandlerA(HandlerB(DefaultHandler(None)))

    def set_handler(self, handler):
        """ cambia la cadena de handlers de un mismo user """
        self.handler = handler

    def make_request(self, amount):
        """ realiza una solicitud de debito por el monto especificado """
        self.handler.handle(amount)

if len(sys.argv) > 1:
    if sys.argv[1] == "--version":
        print("version 1.2")
else:
    JsonWriter().write_json('./sitedata.json', 'token1', 1000)
    JsonWriter().write_json('./sitedata.json', 'token2', 2000)
    user = User()
    user.make_request(500)
    user.make_request(500)
    user.make_request(500)
    user.make_request(500)
    user.make_request(500)
    user.make_request(500)
    user.make_request(500)
    print()
    for pago in Historial():
        print(pago)
