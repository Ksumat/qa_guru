import json
import os
from http import HTTPStatus

import pytest
from faker import Faker
from lib.api_methods import UsersApi, StatusApi


def pytest_addoption(parser):
    parser.addoption('--env', default='dev')


@pytest.fixture(scope='session')
def env(request):
    return request.config.getoption('--env')


@pytest.fixture(scope='session')
def users_api(env):
    api = UsersApi(env)
    yield api
    api.session.close()


@pytest.fixture(scope='session')
def status_api(env):
    api = StatusApi(env)
    yield api
    api.session.close()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="module")
def fill_test_data(users_api: UsersApi):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = users_api.create_user(data=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        users_api.delete_user(user_id)


@pytest.fixture
def users(users_api: UsersApi):
    response = users_api.get_users()
    assert response.status_code == HTTPStatus.OK
    return response.json()['items']


@pytest.fixture
def fake_new_user():
    fake = Faker()

    def _make_fake_user():
        return {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }

    return _make_fake_user


@pytest.fixture
def create_new_fake_user(users_api: UsersApi, fake_new_user):
    user_data = fake_new_user()
    response = users_api.create_user(data=user_data)
    user = response.json()
    return user['id']
