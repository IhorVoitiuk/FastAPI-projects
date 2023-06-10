import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This adds the parent directory of the current file to the Python path


import unittest
import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contact_by_id,
    get_contacts,
    create_contact,
    update_contact,
    remove_contact,
    search_contacts,
    birthday_contacts,
)


class TestNotes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.query = self.session.query.return_value
        self.query.limit.return_value = self.query
        self.query.offset.return_value = self.query

    async def test_get_contact_by_id(self):
        contact = Contact(
            id=1,
            first_name="Max",
            last_name="Prosck",
            email="max@gmail.com",
            phone_number="+380735637222",
            birthday="2000-04-22",
            description="Hello World! Ehoo...",
        )
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(1, db=self.session)
        self.assertEqual(result, contact)
        self.assertEqual(result.first_name, contact.first_name)

    async def test_get_contacts(self):
        self.query.all.return_value = [
            Contact(id=1, first_name="John", email="john@example.com"),
            Contact(id=2, first_name="Jane", email="jane@example.com"),
        ]

        contacts = await get_contacts(limit=2, offset=0, db=self.session)

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].id, 1)
        self.assertEqual(contacts[0].first_name, "John")
        self.assertEqual(contacts[0].email, "john@example.com")
        self.assertEqual(contacts[1].id, 2)
        self.assertEqual(contacts[1].first_name, "Jane")
        self.assertEqual(contacts[1].email, "jane@example.com")

        self.session.query.assert_called_once_with(Contact)
        self.query.limit.assert_called_once_with(2)
        self.query.offset.assert_called_once_with(0)
        self.query.all.assert_called_once_with()

    async def test_create_contact(self):
        body = ContactModel(
            first_name="Dima",
            last_name="Grench",
            email="example@gmail.com",
            phone_number="+380735637891",
            birthday="2000-04-28",
            description="Hello World!",
        )

        result = await create_contact(body=body, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)

    async def test_update_contact(self):
        body = ContactModel(
            id=1,
            first_name="Dima",
            last_name="Grench",
            email="example@gmail.com",
            phone_number="+380735637891",
            birthday="2000-04-28",
            description="Hello World!",
        )

        contact = Contact(
            id=1,
            first_name="Max",
            last_name="Prosck",
            email="max@gmail.com",
            phone_number="+380735637222",
            birthday="2000-04-22",
            description="Hello World! Ehoo...",
        )

        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=contact.id, body=body, db=self.session)
        self.assertEqual(result, contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact(self):
        contact = Contact(
            id=1,
            first_name="Max",
            last_name="Prosck",
            email="max@gmail.com",
            phone_number="+380735637222",
            birthday="2000-04-22",
            description="Hello World! Ehoo...",
        )

        self.session.query().filter_by().first.return_value = contact
        self.session.delete.return_value = None
        result = await remove_contact(contact_id=contact.id, db=self.session)
        self.assertEqual(result, contact)
        self.assertTrue(hasattr(result, "id"))

    async def test_search_contacts(self):
        contacts_list = [
            Contact(id=1, first_name="John", email="john@example.com"),
            Contact(id=2, first_name="Jane", email="jane@example.com"),
        ]

        self.session.query().filter().all.return_value = contacts_list[1]
        contacts = await search_contacts(db=self.session, email="jane@example.com")

        self.assertEqual(contacts_list[1], contacts)

    async def test_birthday_contacts(self):
        contacts_list = [
            Contact(
                id=1,
                first_name="John",
                email="john@example.com",
                birthday=datetime.date(2023, 4, 20),
            ),
            Contact(
                id=2,
                first_name="Jane",
                email="jane@example.com",
                birthday=datetime.date(2023, 4, 25),
            ),
            Contact(
                id=3,
                first_name="Max",
                email="max@gmail.com",
                birthday=datetime.date(2023, 4, 27),
            ),
            Contact(
                id=4,
                first_name="Dima",
                email="dima@example.com",
                birthday=datetime.date(2023, 4, 18),
            ),
        ]
        start_day = datetime.date(2023, 4, 20)
        end_day = datetime.date(2023, 4, 27)
        self.session.query().filter().all.return_value = contacts_list[:-1]
        contacts = await birthday_contacts(db=self.session)

        self.assertEqual(contacts_list[:-1], contacts)
        self.assertEqual(contacts[0].birthday, start_day)
        self.assertEqual(contacts[-1].birthday, end_day)


if __name__ == "__main__":
    unittest.main()
