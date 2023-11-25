import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdateModel
from src.repository.contacts import (
    get_contacts,
    get_contact_by_email,
    get_contact_by_filter,
    get_contact_by_id,
    create_contact,
    update_contact,
    remove_contact,
    contacts_per_days,
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1, username="Dima", email="test@test.com", password="qwerty"
        )

    async def test_get_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await get_contacts(self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contacts_not_found(self):
        self.session.query().filter_by().all.return_value = None
        result = await get_contacts(self.session, self.user)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            firstname="Oleg",
            lastname="Petrov",
            email="tes@te.com",
            phone="12345678",
            birthday=None
        )
        result = await create_contact(body, self.session, self.user)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.birthday, None)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_contact_by_filter_firstname(self):
        contact = Contact()
        self.session.query().filter_by().all.return_value = contact
        result = await get_contact_by_filter(self.session, self.user, "Vasya")
        self.assertEqual(result, contact)

    async def test_get_contact_by_filter_firstname_and_lastname(self):
        contact = Contact()
        self.session.query().filter_by().filter_by().all.return_value = contact
        result = await get_contact_by_filter(self.session, self.user, "Vasya", "Petrov")
        self.assertEqual(result, contact)

    async def test_get_contact_by_filter_all_query(self):
        contact = Contact()
        self.session.query().filter_by().filter_by().filter_by().all.return_value = contact
        result = await get_contact_by_filter(self.session, self.user, "Vasya", "Petrov", "test@test.com")
        self.assertEqual(result, contact)

    async def test_get_contact_by_id(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(1, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_get_contact_by_email(self):
        contact = Contact()
        self.session.query().filter_by().all.return_value = contact
        result = await get_contact_by_email("test@test.com", self.session, self.user)
        self.assertEqual(result, contact)

    async def test_contacts_per_days(self):
        contact = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contact
        result = await contacts_per_days(5, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_update_contact(self):
        body = ContactUpdateModel(
            email="test@test.com",
            phone="12346789"
        )
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await update_contact(body, 1, self.session, self.user)
        self.assertEqual(result.phone, body.phone)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove_contact(1, self.session)
        self.assertEqual(result, contact)
