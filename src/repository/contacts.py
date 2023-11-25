from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdateModel
from datetime import date, timedelta


async def get_contacts(db: Session, current_user: User):
    """
    The get_contacts function returns a list of contacts for the current user.

    :param db: Session: Access the database
    :param current_user: User: Get the user_id from the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=current_user.id).all()
    return contacts


async def get_contact_by_id(contact_id: int, db: Session, current_user: User):
    """
    The get_contact_by_id function returns a contact by its id. Args: contact_id (int): The id of the contact to be
    returned. db (Session): A database session object used for querying the database. current_user (User): The user
    who is making this request, which will be used to ensure that they are only able to access their own contacts and
    not those of other users.

    :param contact_id: int: Specify the id of the contact that is being retrieved from the database
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user's id
    :return: A list of contacts
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    return contact


async def get_contact_by_email(contact_email: str, db: Session, current_user: User):
    """
    The get_contact_by_email function takes in a contact_email and returns the contact with that email. Args:
    contact_email (str): The email of the desired Contact object. db (Session): A database session to query for the
    Contact object. current_user (User): The user who is making this request, used to ensure they are only getting
    their own contacts back.

    :param contact_email: str: Get the email of the contact
    :param db: Session: Connect to the database
    :param current_user: User: Ensure that the user is only able to access their own contacts
    :return: A list of contacts
    :doc-author: Trelent
    """
    contact = (
        db.query(Contact).filter_by(email=contact_email, user_id=current_user.id).all()
    )
    return contact


async def get_contact_by_filter(
    db: Session,
    current_user: User,
    firstname: str = None,
    lastname: str = None,
    email: str = None,
):
    """
    The get_contact_by_filter function returns a list of contacts that match the filter criteria.
    The function takes in three optional parameters: firstname, lastname, and email.
    If no parameters are passed to the function it will return all contacts for the current user.

    :param db: Session: Pass the database session to the function
    :param current_user: User: Filter the contacts by user
    :param firstname: str: Filter the contacts by firstname
    :param lastname: str: Filter the contacts by lastname
    :param email: str: Filter the contacts by email
    :param : Filter the contacts by firstname, lastname and email
    :return: A list of contacts
    :doc-author: Trelent
    """
    query = db.query(Contact)

    if firstname:
        query = query.filter_by(firstname=firstname, user_id=current_user.id)
    if lastname:
        query = query.filter_by(lastname=lastname, user_id=current_user.id)
    if email:
        query = query.filter_by(email=email, user_id=current_user.id)
    contacts = query.all()
    return contacts


async def create_contact(body: ContactModel, db: Session, current_user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Define the type of data that is expected to be passed in
    :param db: Session: Access the database
    :param current_user: User: Get the user_id from the current user
    :return: The newly created contact
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(), user_id=current_user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    body: ContactUpdateModel, contact_id: int, db: Session, current_user: User
):
    """
    The update_contact function updates a contact in the database. Args: body (ContactUpdateModel): The updated
    contact information. contact_id (int): The id of the contact to update. db (Session): A connection to the
    database session.  This is used for querying and updating data in our DBMS, PostgreSQL, via SQLAlchemy's ORM
    layer.  See https://docs.sqlalchemy.org/en/13/orm/.

    :param body: ContactUpdateModel: Get the data from the request body
    :param contact_id: int: Identify which contact to update
    :param db: Session: Access the database
    :param current_user: User: Get the current user from the request
    :return: A contact object
    :doc-author: Trelent
    """
    contact = (
        db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    )
    if contact:
        contact.phone = body.phone
        contact.email = body.email
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.

    :param contact_id: int: Specify the contact id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def contacts_per_days(days: int, db: Session, current_user: User):
    """
    The contacts_per_days function returns a list of contacts that have birthdays within the next X days.

    :param days: int: Determine how many days in the future we want to look for contacts
    :param db: Session: Pass the database session to the function
    :param current_user: User: Filter the contacts by user
    :return: All contacts that have a birthday between today and the number of days in the future
    :doc-author: Trelent
    """
    today = date.today()
    future_date = today + timedelta(days)
    today_str = today.strftime("%Y-%m-%d")
    future_date_str = future_date.strftime("%Y-%m-%d")
    contacts = (
        db.query(Contact)
        .filter(
            Contact.birthday > today_str,
            Contact.birthday <= future_date_str,
            user_id=current_user.id,
        )
        .all()
    )
    return contacts
