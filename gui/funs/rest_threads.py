from PyQt5.QtCore import QThread, pyqtSignal
import requests
import json


class RestThread(QThread):
    rest_response = pyqtSignal()  # Signal to indicate REST call is complete

    def __init__(self, base_url, endpoint, params=None, data=None, get=False, post=False, delete=False):
        super(RestThread, self).__init__()
        self.base_url = base_url
        self.endpoint = endpoint
        self.compl_url = self.base_url + self.endpoint
        self.params = params
        self.data = data

        self.response = {'success': False, 'message': 'Initial Response'}

        self.get = get
        self.post = post
        self.delete = delete
        true_count = 0
        if self.get:
            true_count += 1
        if self.post:
            true_count += 1
        if self.delete:
            true_count += 1

        if true_count > 1 | true_count == 0:
            raise Exception(
                "RestThread has multiple or no defined request types. Only define one (GET, POST or DELETE)")

    def run(self):
        try:
            headers = {'accept': 'application/json'}
            if self.get:
                response = requests.get(self.compl_url, params=self.params, headers=headers)
            elif self.post:
                response = requests.post(self.compl_url, json=self.data, headers=headers)
            elif self.delete:
                response = requests.delete(self.compl_url, params=self.params, headers=headers)

            response.raise_for_status()
            self.response = json.loads(response.text)
        except requests.exceptions.RequestException as e:
            self.response = {'success': False,
                             'message': str(e)}
        except Exception as e:
            self.response = {'success': False,
                             'message': str(e)}
        finally:
            self.rest_response.emit()
