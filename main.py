from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from auth import AuthHandler
from schemas import AuthDetails

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



class Notification(BaseModel):
    user_id: int
    message: str
    timestamp: int
    is_read: bool = None
    is_seen: bool = None
    link: str

auth_handler = AuthHandler()
users = []

@app.post('/register', status_code=201)
def register(auth_details: AuthDetails):
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    users.append({
        'username': auth_details.username,
        'password': hashed_password    
    })
    return


@app.post('/login')
def login(auth_details: AuthDetails):
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break
    
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    return { 'token': token }


@app.get('/unprotected')
def unprotected():
    return { 'hello': 'world' }


@app.get('/protected')
def protected(username=Depends(auth_handler.auth_wrapper)):
    return { 'name': username }

NOTIFICATION = []
@app.get("/")
def read_notification(db: Session = Depends(get_db)):
    return db.query(models.Notifications).all()

            
@app.post("/")
def create_notification(notification: Notification, db: Session = Depends (get_db)):    
    notification_model = models.Notifications()
    notification_model.user_id = notification.user_id
    notification_model.message = notification.message
    notification_model.timestamp = notification.timestamp
    notification_model.is_read = notification.is_read
    notification_model.is_seen = notification.is_seen
    notification_model.link = notification.link

    db.add(notification_model)
    db.commit()

    return notification

@app.delete("/{notification_id}") 
def delete_notification(notification_id: int, db: Session = Depends(get_db)):

    notification_model = db.query(models.Notifications).fil(models.Notifications.id == notification_id).first()
    if notification_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {notification_id} : Does Not Exist"
    )

    db.query(models.Notifications).filter(models.Notification.id == notification_id).delete()
    db.commit()
