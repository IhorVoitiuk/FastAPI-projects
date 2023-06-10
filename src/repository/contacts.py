import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel


async def get_contact_by_id(contact_id: int, db: Session):
    """
    The get_contact_by_id function takes in a contact_id and returns the corresponding Contact object.
        Args:
            contact_id (int): The id of the desired Contact object.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: Session: Pass the database session to the function
    :return: The first contact in the database with an id equal to the one passed as a parameter
    :doc-author: Ihor Voitiuk
    """

    contact = db.query(Contact).filter_by(id=contact_id).first()
    return contact


async def get_contacts(limit: int, offset: int, db: Session):
    """
    The get_contacts function returns a list of contacts from the database.
        Args:
            limit (int): The number of contacts to return.
            offset (int): The index at which to start returning contacts.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Ihor Voitiuk
    """

    contacts = db.query(Contact).limit(limit).offset(offset).all()
    return contacts


async def create_contact(body: ContactModel, db: Session):
    """
    The create_contact function takes in a Contact object and adds it to the database.
        Args:
            body (ContactModel): The Contact object to be added to the database.

    :param body: ContactModel: Specify the contact object to be added to the database
    :param db: Session: Pass the database session to the function
    :return: The created contact object
    :doc-author: Ihor Voitiuk
    """

    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, db: Session):
    """
    The update_contact function takes in a Contact object and updates it in the database.
        Args:
            contact_id (int): The id of the desired Contact object.
            body (ContactModel): The Contact object to be updated in the database.

    :param contact_id: int: Specify the id of the contact to be updated
    :param body: ContactModel: Specify the contact object to be updated in the database
    :param db: Session: Pass the database session to the function
    :return: The updated contact object
    :doc-author: Ihor Voitiuk
    """

    contact = await get_contact_by_id(contact_id, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.description = body.description
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A session object that is used to query and update the database.

    :param contact_id: int: Specify the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact object that was deleted
    :doc-author: Ihor Voitiuk
    """

    contact = await get_contact_by_id(contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(
    db: Session, first_name: str = None, last_name: str = None, email: str = None
):
    """
    The search_contacts function searches the database for contacts that match the given parameters.
        If no parameters are provided, it returns None.

    :param db: Session: Pass in the database session
    :param first_name: str: Search for a contact by first name
    :param last_name: str: Filter the results by last name
    :param email: str: Search for a contact by email
    :return: A list of contact objects or None if no seach contacts
    :doc-author: Ihor Voitiuk
    """

    if first_name and last_name and email:
        return (
            db.query(Contact)
            .filter(
                Contact.first_name == first_name.capitalize(),
                Contact.last_name == last_name.capitalize(),
                Contact.email == email.lower(),
            )
            .all()
        )
    elif first_name and last_name:
        return (
            db.query(Contact)
            .filter(
                Contact.first_name == first_name.capitalize(),
                Contact.last_name == last_name.capitalize(),
            )
            .all()
        )
    elif last_name and email:
        return (
            db.query(Contact)
            .filter(
                Contact.last_name == last_name.capitalize(),
                Contact.email == email.lower(),
            )
            .all()
        )
    elif first_name and email:
        return (
            db.query(Contact)
            .filter(
                Contact.first_name == first_name.capitalize(),
                Contact.email == email.lower(),
            )
            .all()
        )
    elif first_name:
        return (
            db.query(Contact)
            .filter(Contact.first_name == first_name.capitalize())
            .all()
        )
    elif last_name:
        return (
            db.query(Contact).filter(Contact.last_name == last_name.capitalize()).all()
        )
    elif email:
        return db.query(Contact).filter(Contact.email == email.lower()).all()

    return None


async def birthday_contacts(db: Session):
    """
    The birthday_contacts function returns a list of contacts whose birthday is within the next week.

    :param db: Session: Pass the database session to the function
    :return: A list of contacts that have a birthday within the next 7 days
    :doc-author: Ihor Voitiuk
    """
    
    start_day = datetime.date.today() + datetime.timedelta(days=1)
    end_day = datetime.date.today() + datetime.timedelta(days=8)
    contacts = (
        db.query(Contact)
        .filter(Contact.birthday >= start_day, Contact.birthday <= end_day)
        .all()
    )

    return contacts

    # sql_query = """
    #     SELECT * FROM contact
    #     WHERE date_part('month', birthday) = date_part('month', CURRENT_DATE + INTERVAL '1 DAY')
    #         AND date_part('day', birthday) BETWEEN date_part('day', CURRENT_DATE + INTERVAL '1 DAY')
    #                                         AND date_part('day', CURRENT_DATE + INTERVAL '8 DAY')
    # """
    # contacts = db.execute(text(sql_query)).fetchall()

    # return contacts
