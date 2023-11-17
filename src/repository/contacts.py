from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdateModel
from datetime import date, timedelta


async def get_contacts(db: Session, current_user: User):
    contacts = db.query(Contact).filter_by(user_id=current_user.id).all()
    return contacts


async def get_contact_by_id(contact_id: int, db: Session, current_user: User):
    contact = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).all()
    return contact


async def get_contact_by_email(contact_email: str, db: Session, current_user: User):
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
    contact = Contact(**body.model_dump(), user_id=current_user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    body: ContactUpdateModel, contact_id: int, db: Session, current_user: User
):
    contact = (
        db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    )
    if contact:
        contact.phone = body.phone
        contact.email = body.email
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def contacts_per_days(days: int, db: Session, current_user: User):
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
