from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from typing import Optional



def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


def create_user(body: UserModel, db: Session) -> User:
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Failed to get Gravatar image: {e}")
        avatar = None

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: Optional[str], db: Session) -> None:
    user.refresh_token = token
    db.commit()


def confirmed_email(email: str, db: Session) -> None:
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

def update_avatar(email, url: str, db: Session) -> User:
    user = get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

def update_password(user: User, new_password: str, db: Session):
    user.password = new_password
    db.commit()