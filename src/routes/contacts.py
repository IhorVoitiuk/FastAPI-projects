from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact
from src.services.auth import auth_service
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as respository_contacts


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/search",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_contacts(
    first_name: str = Query(None),
    last_name: str = Query(None),
    email: str = Query(None),
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The search_contacts function is used to search for contacts in the database.
        The function takes in a first name, last name, and email address as parameters.
        It then searches the database for any contacts that match those parameters and returns them or None.

    :param first_name: str: Pass the first name of a contact to search for
    :param last_name: str: Search for contacts by last name
    :param email: str: Search for a contact by email
    :param db: Session: Pass the database session to the respository_contacts
    :param current_user: Contact: Get the current user from the database
    :param : Specify the type of data that is expected in the request body
    :return: A list of contacts
    :doc-author: Ihor Voitiuk
    """

    contacts = await respository_contacts.search_contacts(
        db, first_name, last_name, email
    )
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contacts


@router.get(
    "/birthday",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def birthday_contacts(
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The birthday_contacts function returns a list of contacts that have birthdays next week (7 deys).


    :param db: Session: Get the database session
    :param current_user: Contact: Get the current user from the database
    :param : Get the database connection
    :return: The contacts that have a birthday today
    :doc-author: Ihor Voitiuk
    """

    contacts = await respository_contacts.birthday_contacts(db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Specify the path parameter
    :param db: Session: Get the database session
    :param current_user: Contact: Get the current user
    :param : Specify the id of the contact to be retrieved
    :return: A contact object
    :doc-author: Ihor Voitiuk
    """

    contact = await respository_contacts.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    limit: int = Query(ge=5, le=10),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts returned by the api
    :param offset: int: Skip the first n records
    :param db: Session: Pass the database session to the function
    :param current_user: Contact: Get the current user
    :param : Limit the number of contacts returned
    :return: A list of contacts
    :doc-author: Ihor Voitiuk
    """

    contacts = await respository_contacts.get_contacts(limit, offset, db)
    return contacts


@router.post(
    "/",
    response_model=ContactResponse,
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contacts(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The create_contacts function creates a new contact in the database.

    :param body: ContactModel: Define the type of data that will be sent in the request body
    :param db: Session: Pass the database session to the repository layer
    :param current_user: Contact: Get the current user from the database
    :param : Get the contact id from the url
    :return: A contactmodel object
    :doc-author: Ihor Voitiuk
    """

    contact = await respository_contacts.create_contact(body, db)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def updade_contac(
    body: ContactModel,
    contact_id: int = Path(description="The ID of the contacts to update", ge=1),
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The updade_contac function updates a contact in the database.

    :param body: ContactModel: Validate the input data
    :param contact_id: int: Get the id of the contact to delete
    :param ge: Specify that the contact_id must be greater than or equal to 1
    :param db: Session: Get the database session
    :param current_user: Contact: Get the current user from the database
    :param : Get the id of the contact to delete
    :return: A contactmodel object
    :doc-author: Ihor Voitiuk
    """

    contact = await respository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete(
    "/contact_id",
    status_code=status.HTTP_204_NO_CONTENT,
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def remove_contact(
    contact_id: int = Path(description="The ID of the contacts to delete", ge=1),
    db: Session = Depends(get_db),
    current_user: Contact = Depends(auth_service.current_user),
):
    """
    The remove_contact function deletes a contact from the database.

    :param contact_id: int: Get the id of the contact to delete
    :param ge: Specify that the contact_id must be greater than or equal to 1
    :param db: Session: Get the database session
    :param current_user: Contact: Get the current user from the database
    :param : Get the id of the contact to update
    :return: The contact that was deleted
    :doc-author: Ihor Voitiuk
    """

    contact = await respository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
