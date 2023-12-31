from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas import ContactModel, ResponseContact, ContactUpdateModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get(
    "/",
    response_model=List[ResponseContact],
    dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
)
async def get_contacts(
    db: Session = Depends(get_db),
    firstname: str = Query(default=None),
    lastname: str = Query(default=None),
    email: str = Query(default=None),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function returns a list of contacts.

    :param db: Session: Get the database session
    :param firstname: str: Filter the contacts by firstname
    :param lastname: str: Filter the contacts by lastname
    :param email: str: Filter the contacts by email
    :param current_user: User: Get the current user from the database
    :param : Get the contact by id
    :return: A list of contacts
    :doc-author: Trelent
    """
    if firstname or lastname or email:
        contacts = await repository_contacts.get_contact_by_filter(
            db, current_user, firstname, lastname, email
        )
    else:
        contacts = await repository_contacts.get_contacts(db, current_user)

    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found"
        )

    return contacts


@router.get(
    "/days/{days}",
    response_model=List[ResponseContact],
    dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
)
async def get_contacts_by_days(
    days: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function returns a list of contacts for the current user.
    The function takes in an optional days parameter, which is used to filter the results by date.
    If no days parameter is provided, all contacts are returned.

    :param days: int: Specify the number of days to get contacts for
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user from the database
    :param : Specify the number of days to look back for contacts
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.contacts_per_days(days, db, current_user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts


@router.get(
    "/contact/{contact_id}",
    response_model=ResponseContact,
    dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
)
async def get_contact_by_id(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it raises an HTTP 404 error.

    :param contact_id: int: Get the contact id from the path
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :param : Specify the type of data that is expected in the request body
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post(
    "/",
    response_model=ResponseContact,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=2, seconds=5))],
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Get the current user
    :param : Get the contact id from the url
    :return: A contact model object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_email(body.email, db, current_user)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contact with email:{body.email} already exist!",
        )
    contact = await repository_contacts.create_contact(body, db, current_user)

    return contact


@router.patch(
    "/{contact_id}",
    response_model=ResponseContact,
    dependencies=[Depends(allowed_operation_update), Depends(RateLimiter(times=2, seconds=5))],
)
async def update_contact(
    body: ContactUpdateModel,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
        The function takes an id of the contact to be updated, and a body containing
        all fields that are to be updated. If any field is not provided, it will not
        be changed in the database.

    :param body: ContactUpdateModel: Get the data from the request body
    :param contact_id: int: Specify the contact id to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :param : Get the id of the contact to be deleted
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(allowed_operation_remove), Depends(RateLimiter(times=2, seconds=5))],
)
async def remove_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the contact to be removed
    :param db: Session: Pass the database connection to the repository layer
    :param current_user: User: Get the current user from the database
    :param : Get the contact id from the path
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
