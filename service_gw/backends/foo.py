from service_gw.backends.base import BaseServiceGateway


class FooBarServiceGateway(BaseServiceGateway):

    def provision(self):
        return {'URI': 'foo://bar'}

    def delete(self, reference):
        return True