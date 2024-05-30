from typing import List, Union, Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

# Inicializa la aplicación FastAPI
app = FastAPI()

# Configuración del contexto de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Claves y configuración para el token JWT
SECRET_KEY = "27A0D7C4CCCE76E6BE39225B7EEE8BD0EF890DE82D49E459F4C405C583080AB0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Base de datos simulada para usuarios (lista en lugar de una base de datos real)
dummy_users_db = []

# Esquema de seguridad OAuth2 para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic para la gestión de usuarios y tokens
class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para obtener el hash de una contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para verificar una contraseña en texto plano contra su hash
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para obtener un usuario de la base de datos simulada
def get_user(db, username: str):
    for user in db:
        if user.username == username:
            return user
    return None

# Función para autenticar un usuario verificando su contraseña
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Dependencia para obtener el usuario actual a partir del token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(dummy_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Ruta para registrar un nuevo usuario
@app.post("/usuarios/", response_model=User)
def crear_usuario(user: User):
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    dummy_users_db.append(user_in_db)
    return user

# Ruta para iniciar sesión y obtener el token de acceso
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(dummy_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
