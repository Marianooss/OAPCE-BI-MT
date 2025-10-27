import bcrypt
from models import Usuario, RolEnum
from database import get_db

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def authenticate_user(email: str, password: str):
    db = get_db()
    try:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
    finally:
        db.close()

def create_user(nombre: str, email: str, password: str, rol: str = "operador"):
    db = get_db()
    try:
        password_hash = hash_password(password)
        rol_enum = RolEnum[rol]
        user = Usuario(
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol_enum
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def get_user_by_email(email: str):
    db = get_db()
    try:
        return db.query(Usuario).filter(Usuario.email == email).first()
    finally:
        db.close()
