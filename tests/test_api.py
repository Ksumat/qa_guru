import math
from http import HTTPStatus
from random import randint

import pytest
from app.models.User import User
from lib.api_methods import UsersApi


@pytest.mark.usefixtures("fill_test_data")
def test_users(users_api: UsersApi):
    response = users_api.get_users()
    assert response.status_code == HTTPStatus.OK

    user_list = response.json()['items']
    for user in user_list:
        User.model_validate(user)


@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))


def test_user(users_api: UsersApi, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = users_api.get_user(user_id)
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        User.model_validate(user)


@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(users_api: UsersApi, user_id):
    response = users_api.get_user(user_id)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("fill_test_data")
@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(users_api: UsersApi, user_id):
    response = users_api.get_user(user_id)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestPagination:
    @pytest.mark.usefixtures("fill_test_data")
    def test_expected_count_of_users(self, users_api: UsersApi):
        response = users_api.get_users()
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        if data['page'] != data['pages']:
            assert len(data['items']) == data['size'], f"Кол-во юзеров в ответе: {len(data['items'])}, не совпадает с " \
                                                       f" максимальным кол-вом на странице: {data['size']}"
        elif data['page'] == data['pages']:
            assert len(data['items']) == data['total'] % data['size'], f"Кол-во юзеров в ответе: {len(data['items'])}," \
                                                                       f" не совпадает с ожидаемым: {data['total'] % data['size']}"

    @pytest.mark.usefixtures("fill_test_data")
    @pytest.mark.parametrize("size", {1, 5, 10, 30, randint(1, 100)})
    def test_count_pages_different_sizes(self, users_api: UsersApi, size):
        response = users_api.get_users(params={'size': size})
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data['pages'] == math.ceil(data['total'] / data['size']), f"кол-во страниц не соответствует ожидаемому"

    @pytest.mark.usefixtures("fill_test_data")
    @pytest.mark.parametrize("page_1, page_2, size", [(1, 2, 1), (1, 2, 5), (1, randint(2, 100), randint(1, 100))])
    def test_different_data_on_different_pages(self, users_api: UsersApi, page_1, page_2, size):
        response_1 = users_api.get_users(params={'page': page_1, 'size': size})
        response_2 = users_api.get_users(params={'page': page_2, 'size': size})
        data_1, data_2 = response_1.json()['items'], response_2.json()['items']

        assert response_1.status_code == HTTPStatus.OK
        assert response_2.status_code == HTTPStatus.OK
        assert data_1 != data_2, "На разных страницах одинаковые данные"


class TestMethods:
    def test_create_user(self, users_api: UsersApi, fake_new_user):
        """- Тест на post: создание. Предусловия: подготовленные тестовые данные """
        user_data = fake_new_user()
        response = users_api.create_user(data=user_data)

        assert response.status_code == HTTPStatus.CREATED
        user = response.json()
        User.model_validate(user)

        for key in user_data:
            assert user_data[key] == user[key], "данные не совпадают"

    def test_delete_user(self, users_api: UsersApi, create_new_fake_user):
        """- Тест на delete: удаление. Предусловия: созданный пользователь"""
        user_id = create_new_fake_user
        response = users_api.delete_user(user_id)
        assert response.status_code == HTTPStatus.OK
        assert response.json()['message'] == 'User deleted'

        response1 = users_api.get_user(user_id)
        assert response1.status_code == HTTPStatus.NOT_FOUND

    def test_patch_user(self, users_api: UsersApi, create_new_fake_user, fake_new_user):
        """- Тест на patch: изменение. Предусловия: созданный пользователь"""
        user_id = create_new_fake_user
        upd_data_user = fake_new_user()
        response = users_api.update_user(user_id, data=upd_data_user)

        assert response.status_code == HTTPStatus.OK
        response1 = users_api.get_user(user_id)
        user = response1.json()
        User.model_validate(user)

        for key in upd_data_user:
            assert upd_data_user[key] == user[key], "данные не совпадают"
