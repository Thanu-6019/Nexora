# (1) New imports for FastAPI, async, and database
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.expression import text
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import random

# (2) PostgreSQL database setup
DATABASE_URL = "postgresql://user:password@host:port/dbname" # This would be a real connection string
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# (3) JWT and password hashing setup
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# (4) Updated Database Models for SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String) # Store hashed password
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

# (5) Utility functions for authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # In a real app, you would retrieve the user from the database here
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# (6) New Authentication and Event routes
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
    return {"message": "User created successfully"}

@app.post("/login", status_code=status.HTTP_200_OK)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# (7) New Event routes with dependencies
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
# (1) Add the new import for your AI functions
from .ai_matching import match_users_by_skills, recommend_events_for_user
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
# ... other imports from your existing FastAPI file

# (2) Place this new endpoint after your existing routes
@app.post("/match_participants_ai", status_code=status.HTTP_200_OK)
def match_participants_ai(data: dict, current_user: dict = Depends(get_current_user), db=Depends(lambda: SessionLocal())):
    """
    Finds and returns AI-powered matches for participants based on skill similarity.
    """
    participant_ids = data.get('participant_ids', [])
    if not participant_ids:
        return {"message": "No participant IDs provided."}
    
    # In a real app, you would retrieve participants from the database
    # For this example, we'll use a dummy data retrieval
    participants = db.query(User).filter(User.id.in_(participant_ids), User.role == 'participant').all()
    
    # Format the users into the structure the AI function expects
    user_list = [
        {'id': p.id, 'name': p.username, 'skills': p.skills or ''}
        for p in participants
    ]
    
    if len(user_list) < 2:
        return {"message": "Not enough participants for matching."}
    
    # Call the AI function to get the matches
    matches = match_users_by_skills(user_list)
    
    return {"matches": matches}

# (3) Add another endpoint for event recommendations
@app.get("/recommend_events", status_code=status.HTTP_200_OK)
def get_recommended_events(user_id: int, db=Depends(lambda: SessionLocal())):
    """
    Recommends events for a given user based on their skills.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    events = db.query(Event).all()
    if not events:
        return {"message": "No events found to recommend."}
        
    user_profile_string = user.skills
    event_list = [{'title': e.title, 'tags': e.title + ' ' + (e.description or '')} for e in events]
    
    recommended = recommend_events_for_user(user_profile_string, event_list)
    
    return {"recommendations": recommended}
    # (1) Add the new imports for WebSocket and the class
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict

# ... your other existing imports from main.py

# (2) This new class manages active WebSocket connections for each event
class ConnectionManager:
    def __init__(self):
        # A dictionary to hold active connections, with event_id as the key
        # and a list of WebSockets as the value
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

# (3) This is the new WebSocket endpoint. Add it alongside your other routes.
@app.websocket("/ws/chat/{event_id}/{username}")
async def websocket_endpoint(
    websocket: WebSocket, event_id: int, username: str
):
    # Connect the user to the specified chat room (event_id)
    await manager.connect(websocket, event_id)
    print(f"User {username} joined event {event_id} chat.")
    
    try:
        # A loop to receive messages from the client
        while True:
            data = await websocket.receive_text()
            
            # Format the message to be broadcasted to the room
            message = f"{username}: {data}"
            
            # Broadcast the message to all connected clients in this event room
            await manager.broadcast(message, event_id)
            
    except WebSocketDisconnect:
        # Remove the user from the connection list when they disconnect
        manager.disconnect(websocket, event_id)
        print(f"User {username} left event {event_id} chat.")
        # Optionally, broadcast a "user left" message
        await manager.broadcast(f"User {username} has left the chat.", event_id)
import random
from typing import List, Dict
from .carbon_footprint import estimate_event_carbon_footprint
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.expression import text
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ... (Existing imports from your main.py file)

# (1) This new class manages active WebSocket connections for each event
class ConnectionManager:
    def __init__(self):
        # A dictionary to hold active connections, with event_id as the key
        # and a list of WebSockets as the value
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

# ... (Existing SQLAlchemy setup and models)

# (2) Place this new endpoint after your existing routes.
@app.websocket("/ws/chat/{event_id}/{username}")
async def websocket_endpoint(
    websocket: WebSocket, event_id: int, username: str
):
    # Connect the user to the specified chat room (event_id)
    await manager.connect(websocket, event_id)
    print(f"User {username} joined event {event_id} chat.")
    
    try:
        # A loop to receive messages from the client
        while True:
            data = await websocket.receive_text()
            
            # Format the message to be broadcasted to the room
            message = f"{username}: {data}"
            
            # Broadcast the message to all connected clients in this event room
            await manager.broadcast(message, event_id)
            
    except WebSocketDisconnect:
        # Remove the user from the connection list when they disconnect
        manager.disconnect(websocket, event_id)
        print(f"User {username} left event {event_id} chat.")
        # Optionally, broadcast a "user left" message
        await manager.broadcast(f"User {username} has left the chat.", event_id)


# (3) Add a new API endpoint to calculate carbon footprint
@app.get("/events/{event_id}/carbon_footprint", status_code=status.HTTP_200_OK)
def get_carbon_footprint(event_id: int):
    """
    Estimates the carbon footprint for a given event.
    """
    # NOTE: In a real application, you would fetch these details from the database
    # based on the event_id and participant data.
    
    # Dummy data for demonstration purposes
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

# (4) Add a new API endpoint for the leaderboard
@app.get("/events/{event_id}/leaderboard", status_code=status.HTTP_200_OK)
def get_leaderboard(event_id: int):
    """
    Returns a leaderboard of participants for a given event.
    """
    # NOTE: In a real application, you would fetch this data from the database.
    
    # Dummy data for demonstration purposes
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
