import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal

class RestApiClient(QThread):
    rest_response = pyqtSignal()

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def _get_request(self, url, params=None):
        global response
        try:
            headers = {'accept': 'application/json'}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            response = json.loads(response.text)
        except requests.exceptions.RequestException as e:
            response = {'success': False,
                     'message': str(e)}
        except Exception as e:
            response = {'success': False,
                     'message': str(e)}
        finally:
            self.rest_response.emit()
            return response

    def _post_request(self, url, data=None):
        global response
        try:
            headers = {'accept': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            response = json.loads(response.text)
        except requests.exceptions.RequestException as e:
            response = {'success': False,
                     'message': str(e)}
        except Exception as e:
            response = {'success': False,
                     'message': str(e)}
        finally:
            self.rest_response.emit()
            return response

    def _delete_request(self, url, params=None):
        global response
        try:
            headers = {'accept': 'application/json'}
            response = requests.delete(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            response = json.loads(response.text)
        except requests.exceptions.RequestException as e:
            response = {'success': False,
                     'message': str(e)}
        except Exception as e:
            response = {'success': False,
                     'message': str(e)}
        finally:
            self.rest_response.emit()
            return response

    def get(self, endpoint, params=None):
        url = self.base_url + endpoint
        return self._get_request(url, params)

    def post(self, endpoint, data=None):
        url = self.base_url + endpoint
        return self._post_request(url, data)

    def delete(self, endpoint, params=None):
        url = self.base_url + endpoint
        return self._delete_request(url, params)