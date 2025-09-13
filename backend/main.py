import os
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import random
from typing import List, Dict

from .carbon_footprint import estimate_event_carbon_footprint

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    role = Column(String, nullable=False)
    skills = Column(String)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, nullable=False)
    organizer_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class ParticipantEvent(Base):
    __tablename__ = "participant_events"
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: dict, db=Depends(lambda: SessionLocal())):
    hashed_password = get_password_hash(data['password'])
    db_user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=hashed_password,
        role=data.get('role', 'participant'),
        skills=data.get('skills', '')
    )
    db.add(db_user)
    db.commit()
    return {"message": "User  created successfully"}

@app.post("/login", status_code=status.HTTP_200_OK)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(data: dict, current_user: dict = Depends(get_current_user), db=Depends(lambda: SessionLocal())):
    organizer = db.query(User).filter(User.username == current_user['username']).first()
    if not organizer or organizer.role != 'organizer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizers can create events")

    event = Event(
        title=data['title'],
        description=data.get('description'),
        date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
        organizer_id=organizer.id
    )
    db.add(event)
    db.commit()
    return {"message": "Event created successfully"}

@app.get("/events")
def get_events(db=Depends(lambda: SessionLocal())):
    events = db.query(Event).all()
    return events

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, event_id: int):
        await websocket.accept()
        if event_id not in self.active_connections:
            self.active_connections[event_id] = []
        self.active_connections[event_id].append(websocket)

    def disconnect(self, websocket: WebSocket, event_id: int):
        self.active_connections[event_id].remove(websocket)

    async def broadcast(self, message: str, event_id: int):
        if event_id in self.active_connections:
            for connection in self.active_connections[event_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{event_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, event_id: int, username: str):
    await manager.connect(websocket, event_id)
    print(f"User  {username} joined event {event_id} chat.")
    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            await manager.broadcast(message, event_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, event_id)
        print(f"User  {username} left event {event_id} chat.")
        await manager.broadcast(f"User  {username} has left the chat.", event_id)

@app.get("/events/{event_id}/carbon_footprint", status_code=status.HTTP_200_OK)
def get_carbon_footprint(event_id: int):
    dummy_participants = random.randint(50, 500)
    dummy_transport = {
        "car": 0.4,
        "train": 0.3,
        "electric_car": 0.2,
        "bike": 0.1,
    }
    footprint_kg = estimate_event_carbon_footprint(dummy_participants, dummy_transport)
    return {
        "event_id": event_id,
        "estimated_carbon_footprint_kg": round(footprint_kg, 2)
    }

@app.get("/events/{event_id}/leaderboard", status_code=status.HTTP_200_OK)
def get_leaderboard(event_id: int):
    dummy_leaderboard_data = [
        {"name": "Alice", "score": 950},
        {"name": "Bob", "score": 920},
        {"name": "Charlie", "score": 880},
        {"name": "Diana", "score": 850},
        {"name": "Frank", "score": 790},
    ]
    return {
        "event_id": event_id,
        "leaderboard": dummy_leaderboard_data
    }
