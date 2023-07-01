import requests
import json

from .rest import RestApiClient


class HighlevelIdev:
    def __init__(self):
        self.result = json.dumps({
                            "success": False,
                            "message": f"Nothing has been done so far"
                        })

    def delete(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.delete(endpoint="/idev-highlvl/delete")
        return response

    def validate(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/idev-highlvl/validate")
        return response

    def provision(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/idev-highlvl/provision")
        return response

    def provide(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.get(endpoint="/idev-highlvl/actual")
        return response


class HighlevelLdev:
    def __init__(self):
        self.result = json.dumps({
            "success": False,
            "message": f"Nothing has been done so far"
        })

    def delete(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.delete(endpoint="/ldev-highlvl/delete")
        return response

    def validate(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/ldev-highlvl/validate")
        return response

    def provision(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/ldev-highlvl/provision")
        return response

    def provision_opc_server(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/ldev-highlvl/provision-opc-ua-server")
        return response

    def provision_azure(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/ldev-highlvl/provision-azure")
        return response

    def provision_aws(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.post(endpoint="/ldev-highlvl/provision-aws")
        return response

    def provide(self):
        call = RestApiClient(base_url='http://0.0.0.0:5000/v1')
        response = call.get(endpoint="/ldev-highlvl/actual")
        return response
