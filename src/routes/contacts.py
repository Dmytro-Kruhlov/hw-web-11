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
    "/{days}",
    response_model=List[ResponseContact],
    dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
)
async def get_contacts(
    days: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.contacts_per_days(days, db, current_user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ResponseContact,
    dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
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
    owner = await repository_contacts.update_contact(body, contact_id, db, current_user)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return owner


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
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
