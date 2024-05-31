from typing import List, Union, Annotated, Optional
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

# Base de datos simulada de usuarios
dummy_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "hashed_password": "secret",  
        "disabled": False
    },
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "full_name": "Alice Wonderson",
        "hashed_password": "secret", 
        "disabled": True
    }
}

# Esquema de seguridad OAuth2 para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic para la gestión de usuarios y tokens
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para obtener el hash de una contraseña
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Función para verificar una contraseña en texto plano contra su hash
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para obtener un usuario de la base de datos simulada
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

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
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str
    
#Ruta para crear usuario
@app.post("/usuarios/", response_model=User)
def crear_usuario(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=False,
        hashed_password=hashed_password
    )
    if user_in_db.username in dummy_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    dummy_users_db[user_in_db.username] = user_in_db.dict()
    return user_in_db

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

# Ruta para obtener la información del usuario actual
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


