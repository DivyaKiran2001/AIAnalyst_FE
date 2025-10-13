from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
import random
import string
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import socketio
app = FastAPI()
origins = [
    "https://3000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io",  # frontend
    "https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io",  # backend
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MongoDB Atlas Connection
# -------------------------
MONGO_URI = "mongodb+srv://divyakirantatikonda_db_user:hQZOVv9ROilEKN4j@cluster0.l492nrq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["StartupAnalyst"]

# Create users collection with schema validation (run only once)
try:
    db.create_collection(
        "Users",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "uid","password","role"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "uid": {"bsonType": "string"},
                    "password": {"bsonType": "string"},
                    "role": {"bsonType": "string"}
                }
            }
        }
    )
except Exception:
    # collection already exists
    pass


# FounderDetails Collection
try:
    db.create_collection(
        "FounderDetails",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "yourName",
                    "emailId",
                    "gender",
                    "phoneNumber",
                    "linkedinUrl",
                    "singleFounder",
                    "role",
                ],
                "properties": {
                    "yourName": {"bsonType": "string"},
                    "emailId": {"bsonType": "string"},
                    "gender": {"bsonType": "string"},
                    "phoneNumber": {"bsonType": "string"},
                    "linkedinUrl": {"bsonType": "string"},
                    "singleFounder": {"bsonType": "string"},
                    "referrer": {"bsonType": ["string", "null"]},
                    "role": {"bsonType": "string"},
                    "uid": {"bsonType": "string"},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'FounderDetails' collection created with schema.")
except Exception:
    print("ℹ️ 'FounderDetails' collection already exists.")

try:
    db.create_collection(
        "StartupDetails",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "startupName",
                    "registeredName",
                    "incorporationMonth",
                    "incorporationYear",
                    "about",
                    "emailId",
                    "uid"
                ],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "registeredName": {"bsonType": "string"},
                    "incorporationMonth": {"bsonType": "string"},
                    "incorporationYear": {"bsonType": "string"},
                    "about": {"bsonType": "string"},
                    "emailId": {"bsonType": "string"},  # founder email
                    "uid": {"bsonType": "string"},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'StartupDetails' collection created with schema.")
except Exception:
    print("ℹ️ 'StartupDetails' collection already exists.")

try:
    db.create_collection(
        "InvestorInterests",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["startupName", "founderEmail", "investorEmail", "status", "createdAt"],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "founderEmail": {"bsonType": "string"},
                    "investorEmail": {"bsonType": "string"},
                    "status": {"bsonType": "string"},  # e.g., "interested", "chatting", "closed"
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'InvestorInterests' collection created with schema validation.")
except Exception:
    print("ℹ️ 'InvestorInterests' collection already exists.")


# ----------------- Create Chats collection with schema validation -----------------
try:
    db.create_collection(
        "Chats",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["participants", "messages", "createdAt"],
                "properties": {
                    "participants": {
                        "bsonType": "array",
                        "minItems": 2,
                        "items": {"bsonType": "string"}  # emails or UIDs
                    },
                    "messages": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["senderId", "text", "timestamp"],
                            "properties": {
                                "senderId": {"bsonType": "string"},
                                "text": {"bsonType": "string"},
                                "timestamp": {"bsonType": "date"},
                            },
                        },
                    },
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'Chats' collection created with schema validation")
except Exception:
    print("ℹ️ 'Chats' collection already exists")

chat_collection = db["Chats"]
users_collection = db["Users"]
interests_collection=db["InvestorInterests"]

founder_collection = db["FounderDetails"]
startup_collection = db["StartupDetails"]

from pydantic import BaseModel
class FounderDetails(BaseModel):
    yourName: str
    emailId: EmailStr
    gender: str
    phoneNumber: str
    linkedinUrl: str
    singleFounder: str
    referrer: str | None = None

class StartupDetails(BaseModel):
   
    startupName: str
    registeredName: str
    incorporationMonth: str
    incorporationYear: str
    about: str

# --- Pydantic Model ---
class Interest(BaseModel):
    startupName: str
    founderEmail: str
    investorEmail: str
    status: str = "pending"
    createdAt: datetime | None = None

    
class AcceptInterest(BaseModel):
    founderEmail: str
    investorEmail: str

# ----------------- Socket.IO Server -----------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("aianalyst-61509-firebase-adminsdk-fbsvc-5b4a8376b1.json")  # download from Firebase console
firebase_admin.initialize_app(cred)

@app.get("/api/founder/interested-investors")
async def get_interested_investors(founderEmail: str):
    interests = list(interests_collection.find({"founderEmail": founderEmail}, {"_id": 0}))
    print(interests)
    return {"investors": interests}
    
def verify_firebase_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        print("✅ Valid Firebase token:", decoded_token)
        return decoded_token
    except Exception as e:
        print("❌ Token verification error:", e)
        raise HTTPException(status_code=401, detail="Invalid Firebase token")



# -------------------------
# Auth Endpoint
# -------------------------
@app.post("/api/auth")
async def auth_user(request: Request):
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        print("No bearer...")
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)

    user_data = await request.json()
    print(user_data)
    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not role:
        raise HTTPException(status_code=400, detail="Role is required")


    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        # Update role if different
        if existing_user.get("role") != role:
            users_collection.update_one({"email": email}, {"$set": {"role": role}})
        return {"status": "success", "user": {"email": email, "role": existing_user.get("role")}}

    users_collection.insert_one({
        "uid": decoded_token["uid"],
        "email": email,
        "password": password or "",
        "role": role
    })

    print(f"Inserted user: {email} as {role}")

    return {"status": "success", "user": {"email": email, "role": role}}

@app.post("/api/founder-details")
async def add_founder_details(request: Request, data: FounderDetails):
    """Store founder profile details"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    uid = decoded_token["uid"]

    existing = founder_collection.find_one({"emailId": data.emailId})
    if existing:
        return {"message": "Founder profile already exists", "founder_id": str(existing["_id"])}

    founder_doc = data.dict()
    founder_doc["uid"] = uid
    founder_doc["role"] = "founder"
    founder_doc["createdAt"] = datetime.utcnow()

    result = founder_collection.insert_one(founder_doc)
    return {"message": "Founder details saved", "founder_id": str(result.inserted_id)}

@app.get("/api/founder/{email}")
def get_founder(email: str):
    """Fetch founder details"""
    founder = founder_collection.find_one({"emailId": email})
    if not founder:
        raise HTTPException(status_code=404, detail="Founder not found")
    founder["_id"] = str(founder["_id"])
    return founder

@app.post("/api/startup-details")
async def add_startup_details(request: Request, data: StartupDetails):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    uid = decoded_token["uid"]
    email = decoded_token.get("email")  # Get email from logged-in user
    print("Email",email)

    # Check if startup for this email already exists
    existing = startup_collection.find_one({"emailId": email})
    if existing:
        return {"message": "Startup already exists", "startup_id": str(existing["_id"])}

    startup_doc = data.dict()
    startup_doc["uid"] = uid
    startup_doc["emailId"] = email  # auto-set from logged-in user
    startup_doc["createdAt"] = datetime.utcnow()

    result = startup_collection.insert_one(startup_doc)
    return {"message": "Startup details saved", "startup_id": str(result.inserted_id)}

# -------------------------
# Get Startup Details by Email
# -------------------------
@app.get("/api/startup-details")
def get_startup_details(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    email = decoded_token.get("email")  # Get email from logged-in user

    startup = startup_collection.find_one({"emailId": email})
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    startup["_id"] = str(startup["_id"])
    return startup

@app.get("/api/startups")
def get_startups():
    startups = list(startup_collection.find({}, {"_id": 0}))
    return startups


# ----------------- Socket.IO Events -----------------
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, data):
    """
    User joins a room
    data: { "participants": ["founderEmail", "investorEmail"] }
    """
    participants = sorted(data["participants"])  # sort to make room unique
    room = "_".join(participants)
    await sio.save_session(sid, {"room": room})
    sio.enter_room(sid, room)
    print(f"{sid} joined room {room}")

# @sio.event
# async def send_message(sid, data):
#     """
#     Receive a message from client and broadcast it to the room.
#     data: { "senderId": "...", "text": "...", "participants": ["founderEmail", "investorEmail"] }
#     """
#     participants = sorted(data["participants"])
#     room = "_".join(participants)
#     message = {
#         "senderId": data["senderId"],
#         "text": data["text"],
#         "timestamp": datetime.utcnow().isoformat()
#     }

#     # Save message to MongoDB
#     chat_doc = chat_collection.find_one({"participants": participants})
#     if chat_doc:
#         chat_collection.update_one(
#             {"participants": participants},
#             {"$push": {"messages": message}}
#         )
#     else:
#         chat_collection.insert_one({
#             "participants": participants,
#             "messages": [message],
#             "createdAt": datetime.utcnow().isoformat()
#         })

#     # Broadcast message to room
#     await sio.emit("receive_message", message, room=room)

@sio.event
async def send_message(sid, data):
    participants = sorted(data["participants"])
    room = "_".join(participants)

    # ✅ Store as datetime for MongoDB
    message_doc = {
        "senderId": data["senderId"],
        "text": data["text"],
        "timestamp": datetime.utcnow()  # <-- keep as datetime
    }

    # Save to MongoDB
    chat_doc = chat_collection.find_one({"participants": participants})
    if chat_doc:
        chat_collection.update_one(
            {"participants": participants},
            {"$push": {"messages": message_doc}}
        )
    else:
        chat_collection.insert_one({
            "participants": participants,
            "messages": [message_doc],
            "createdAt": datetime.utcnow()
        })

    # ✅ Emit to clients (convert datetime to ISO string)
    message_emit = message_doc.copy()
    message_emit["timestamp"] = message_emit["timestamp"].isoformat()
    await sio.emit("receive_message", message_emit, room=room)


# ----------------- API to fetch chat history -----------------
from typing import List
from fastapi import Query

# @app.get("/api/chat/")
# def get_chat_history(participants: List[str] = Query(...)):
#     """
#     Fetch chat history by participants array
#     Example: /api/chat/?participants=founder@example.com&participants=investor@example.com
#     """
#     participants_sorted = sorted(participants)
#     chat = chat_collection.find_one({"participants": participants_sorted})
#     if chat:
#         chat["_id"] = str(chat["_id"])
#         for msg in chat["messages"]:
#             msg["timestamp"] = msg["timestamp"].isoformat()
#         return chat
#     return {"participants": participants_sorted, "messages": []}


@app.get("/api/chat/")
def get_chat_history(participants: List[str] = Query(...)):
    participants_sorted = sorted(participants)
    chat = chat_collection.find_one({"participants": participants_sorted})
    if chat:
        chat["_id"] = str(chat["_id"])
        for msg in chat["messages"]:
            msg["timestamp"] = msg["timestamp"].isoformat()  # convert datetime -> string
        return chat
    return {"participants": participants_sorted, "messages": []}

# ----------------- Example MongoDB document -----------------
"""
Chats collection schema:

{
    "_id": ObjectId(),
    "participants": ["founder@example.com", "investor@example.com"],
    "messages": [
        {
            "senderId": "founder123",
            "text": "Hello, I’m interested in funding your startup",
            "timestamp": datetime.utcnow()
        },
        {
            "senderId": "investor456",
            "text": "Great! Let’s discuss further",
            "timestamp": datetime.utcnow()
        }
    ],
    "createdAt": datetime.utcnow()
}
"""

# @app.post("/api/investor-interest")
# async def add_investor_interest(request: Request):
#     data = await request.json()
#     startup_name = data.get("startupName")
#     founder_email = data.get("founderEmail")
#     investor_email = data.get("investorEmail")

#     if not all([startup_name, founder_email, investor_email]):
#         raise HTTPException(status_code=400, detail="Missing required fields")

#     existing_interest = db["InvestorInterests"].find_one({
#         "startupName": startup_name,
#         "investorEmail": investor_email
#     })

#     if existing_interest:
#         return {"message": "Already marked as interested"}

#     db["InvestorInterests"].insert_one({
#         "startupName": startup_name,
#         "founderEmail": founder_email,
#         "investorEmail": investor_email,
#         "status": "interested",
#         "createdAt": datetime.utcnow()
#     })

#     return {"message": "Interest recorded successfully"}
# --- POST: create interest ---
@app.post("/api/interests")
def create_interest(interest: Interest):
    existing = interests_collection.find_one({
        "startupName": interest.startupName,
        "founderEmail": interest.founderEmail,
        "investorEmail": interest.investorEmail
    })
    if existing:
        raise HTTPException(status_code=400, detail="Interest already exists")

    interest_data = interest.dict()
    if not interest_data.get("createdAt"):
        interest_data["createdAt"] = datetime.utcnow()
    result=interests_collection.insert_one(interest_data)
        # Add _id as string for JSON response
    interest_data["_id"] = str(result.inserted_id)

    return interest_data


@app.get("/api/interests")
def get_interests(investorEmail: str):
    records = list(interests_collection.find({"investorEmail": investorEmail}, {"_id": 0}))
    return records  # <-- returns array directly



# @app.get("/api/founder/interested-investors")
# async def get_interested_investors(founderEmail: str):
#     interests = list(db["InvestorInterests"].find({"founderEmail": founderEmail}, {"_id": 0}))
#     return {"investors": interests}




@app.post("/api/interests/accept")
def accept_interest(data: AcceptInterest):
    result = interests_collection.update_one(
        {"founderEmail": data.founderEmail, "investorEmail": data.investorEmail},
        {"$set": {"status": "accepted"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Interest not found")

    return {"message": "Interest accepted"}