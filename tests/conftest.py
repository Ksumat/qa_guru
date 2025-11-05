import json
import os
from http import HTTPStatus

import dotenv
import pytest
import requests
from faker import Faker


@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


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
    return response.json()['items']


# @pytest.fixture
# def fake_new_user() -> dict:
#     fake = Faker()
#     fake_new_user = {
#         "email": fake.email(),
#         "first_name": fake.first_name(),
#         "last_name": fake.last_name(),
#         "avatar": fake.image_url()
#     }
#     return fake_new_user

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
def create_new_fake_user(app_url, fake_new_user):
    user_data = fake_new_user()
    response = requests.post(f"{app_url}/api/users/", json=user_data)
    user = response.json()
    return user['id']
