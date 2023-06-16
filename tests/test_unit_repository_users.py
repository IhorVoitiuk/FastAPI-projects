import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This adds the parent directory of the current file to the Python path

import unittest
import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    reset_password,
    update_avatar,
)


class TestRepositoryUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        # self.query = self.session.query.return_value
        # self.query.limit.return_value = self.query
        # self.query.offset.return_value = self.query
        self.user = User(
            id=1,
            username="TestName",
            email="TestEmail@example.com",
            password="TestPassword",
            created_at=datetime.date(2023, 4, 20),
            avatar="http://avatars.example.com/profile/1",
            refresh_token="H#KL#@L@#H#KL#H@JK!JKL",
            confirmed=False,
        )

    def tearDown(self):
        del self.session
        del self.user

    async def test_get_user_by_email(self):
        email = "TestEmail@example.com"
        self.session.query().filter().first.return_value = self.user
        user = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(user.email, email)

    async def test_create_user(self):
        body = UserModel(
            username="Dimas",
            email="dima@example.com",
            password="password/",
        )

        user = await create_user(body=body, db=self.session)
        self.assertEqual(user.username, body.username)
        self.assertEqual(user.email, body.email)
        self.assertEqual(user.password, body.password)

    async def test_update_token(self):
        token = "token_example"
        self.session.commit.return_value = self.user
        result = await update_token(user=self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirmed_email(self):
        email = "TestEmail@example.com"
        self.session.query().filter().first.return_value = self.user
        result = await confirmed_email(email=email, db=self.session)
        self.assertEqual(self.user.confirmed, True)

    async def test_reset_password(self):
        email = "TestEmail@example.com"
        new_password = "trololo"
        self.session.query().filter().first.return_value = self.user
        result = await reset_password(
            email=email, new_password=new_password, db=self.session
        )
        self.assertEqual(result.password, new_password)
        self.assertEqual(self.user.password, new_password)

    async def test_update_avatar(self):
        email = "TestEmail@example.com"
        avatar = "http://avatars.example.com/profile/11232"
        self.session.query().filter().first.return_value = self.user
        result = await update_avatar(email=email, url=avatar, db=self.session)
        self.assertEqual(self.user.avatar, avatar)


if __name__ == "__main__":
    unittest.main()
