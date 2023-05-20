from typing import List
from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session

from sqlalchemy import or_, extract
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate, ContactBirthday


def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user: User) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()


def create_contact(db: Session, contact: ContactCreate, user: User) -> Contact:
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user: User) -> Contact:
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not db_contact:
        raise ValueError("Contact not found")
    for field, value in contact.dict(exclude_unset=True).items():
        setattr(db_contact, field, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user: User) -> Contact:
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not db_contact:
        raise ValueError("Contact not found")
    db.delete(db_contact)
    db.commit()
    return db_contact


def search_contacts(db: Session, query: str, user: User) -> List[Contact]:
    if not query:
        return []
    return db.query(Contact).filter(Contact.user_id == user.id).filter(or_(
        Contact.first_name.ilike(f"%{query}%"),
        Contact.last_name.ilike(f"%{query}%"),
        Contact.email.ilike(f"%{query}%"),
    )).all()


def get_contacts_with_birthdays(db: Session, user: User):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.user_id == user.id).filter(
        extract('month', Contact.birthday) == today.month,
        extract('day', Contact.birthday) >= today.day,
        extract('day', Contact.birthday) <= next_week.day
    ).all()
    return contacts
