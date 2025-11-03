import json
from http import HTTPStatus
from random import randint

import pytest
import requests
from app.models.User import User


@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


@pytest.mark.usefixtures("fill_test_data")
def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK

    user_list = response.json()
    for user in user_list:
        User.model_validate(user)


@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))


def test_user(app_url, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        User.model_validate(user)


@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestPagination:
    def test_expected_count_of_users(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        if data['page'] != data['pages']:
            assert len(data['items']) == data['size'], f"Кол-во юзеров в ответе: {len(data['items'])}, не совпадает с " \
                                                       f" максимальным кол-вом на странице: {data['size']}"
        elif data['page'] == data['pages']:
            assert len(data['items']) == data['total'] % data['size'], f"Кол-во юзеров в ответе: {len(data['items'])}," \
                                                                       f" не совпадает с ожидаемым: {data['total'] % data['size']}"

    @pytest.mark.parametrize("size", {1, 5, 10, 30, randint(1, 100)})
    def test_count_pages_different_sizes(self, app_url, size):
        response = requests.get(f"{app_url}/api/users/?size={size}")
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data['pages'] == math.ceil(data['total'] / data['size']), f"кол-во страниц не соответствует ожидаемому"

    @pytest.mark.parametrize("page_1, page_2, size", [(1, 2, 1), (1, 2, 5), (1, randint(2, 100), randint(1, 100))])
    def test_different_data_on_different_pages(self, app_url, page_1, page_2, size):
        response_1 = requests.get(f"{app_url}/api/users/?page={page_1}&size={size}")
        response_2 = requests.get(f"{app_url}/api/users/?page={page_2}&size={size}")
        data_1, data_2 = response_1.json()['items'], response_2.json()['items']

        assert response_1.status_code == HTTPStatus.OK
        assert response_2.status_code == HTTPStatus.OK
        assert data_1 != data_2, "На разных страницах одинаковые данные"


