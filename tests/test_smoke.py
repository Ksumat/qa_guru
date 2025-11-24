from http import HTTPStatus
from lib.api_methods import StatusApi



class TestSmoke:
    def test_app_status(self, status_api: StatusApi):
        response = status_api.get_status()
        assert response.status_code == HTTPStatus.OK

    def test_database_is_loaded(self, status_api: StatusApi):
        response = status_api.get_status()
        flag = response.json()['database']

        assert response.status_code == HTTPStatus.OK
        assert flag is True, "Database is not loaded"
