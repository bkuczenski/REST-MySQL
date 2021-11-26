from passlib.context import CryptContext
import models

PWD_CONTEXT = CryptContext(schemes=["bcrypt"])

class SecurityHandler:
    def __init__(self) -> None:
        pass

    def _verify_password(self, plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)  
        
    def hash_password(self, password):
        return PWD_CONTEXT.hash(password)

    def authenticate_user(self, db, email: str, password: str):
        # not using db_operations because of circular import
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            return False
        if not self._verify_password(password, user.password):
            return False
        return user


