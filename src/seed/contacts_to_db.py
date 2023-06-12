from faker import Faker
from src.database.db import DBSession
from src.database.models import Contact


fake = Faker()
session = DBSession()
DEFAULT_CONTACTS = 50


def create_contact_person(quantity):
    """
    The create_contact_person function creates a contact person with the following attributes:
    first_name, last_name, email, phone_number, birthday and description.
    The function takes one argument which is the quantity of contacts to be created.

    :param quantity: Determine how many contact persons are created
    :return: None
    :doc-author: Ihor Voitiuk
    """
    
    for _ in range(quantity):
        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.ascii_free_email(),
            phone_number=fake.phone_number(),
            birthday=fake.date_of_birth(),
            description=fake.text(),
        )
        session.add(contact)
    session.commit()


if __name__ == "__main__":
    create_contact_person(DEFAULT_CONTACTS)
    print("Contacts created:", DEFAULT_CONTACTS)
