from http import HTTPStatus

import requests


class TestSmoke:
    def test_app_status(self, app_url):
        response = requests.get(f"{app_url}/status/")
        assert response.status_code == HTTPStatus.OK

    def test_database_is_loaded(self, app_url):
        response = requests.get(f"{app_url}/status/")
        flag = response.json()['users']

        assert response.status_code == HTTPStatus.OK
        assert flag is True, "Database is not loaded"
