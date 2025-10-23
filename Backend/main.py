from fastapi import FastAPI, HTTPException
from fastapi import Request as FastAPIRequest
from google.auth.transport.requests import Request as GoogleRequest
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pymongo.errors import CollectionInvalid
import os
from bson import ObjectId
import smtplib
import random
import string
from email.mime.text import MIMEText
from datetime import datetime, timedelta,time
import socketio
import json
import pytz
from datetime import datetime
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

app = FastAPI()
load_dotenv()
origins = [
    "https://3000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev",
    "https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev",
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

# ----------------- Create Meetings Collection with Schema -----------------
try:
    db.create_collection(
        "Meetings",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["startupName", "founderEmail", "investorEmail", "proposedDateTime", "status", "createdAt"],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "founderEmail": {"bsonType": "string"},
                    "investorEmail": {"bsonType": "string"},
                    "proposedDateTime": {"bsonType": "date"},
                    "status": {"bsonType": "string"},  # "pending", "accepted", "declined"
                    "createdAt": {"bsonType": "date"}
                },
            }
        },
    )
    print("✅ 'Meetings' collection created with schema validation.")
except Exception:
    print("ℹ️ 'Meetings' collection already exists.")

try:
    db.create_collection(
        "UserGoogleCredentials",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "credentials"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "credentials": {"bsonType": "object"},
                },
            }
        },
    )
    print("✅ 'UserGoogleCredentials' collection created.")
except Exception:
    print("ℹ️ 'UserGoogleCredentials' collection already exists.")

try:
    db.create_collection(
        "FounderSlots",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["founderEmail", "date", "startTime", "endTime", "status", "createdAt"],
                "properties": {
                    "founderEmail": {"bsonType": "string"},
                    "date": {"bsonType": "string"},  # YYYY-MM-DD
                    "startTime": {"bsonType": "date"},
                    "endTime": {"bsonType": "date"},
                    "status": {"bsonType": "string"},  # "available", "booked"
                    "createdAt": {"bsonType": "date"}
                },
            }
        },
    )
    print("✅ 'FounderSlots' collection created with schema validation.")
except CollectionInvalid:
    print("ℹ️ 'FounderSlots' collection already exists.")

founder_slots_collection = db["FounderSlots"]
chat_collection = db["Chats"]
users_collection = db["Users"]
interests_collection=db["InvestorInterests"]

founder_collection = db["FounderDetails"]
startup_collection = db["StartupDetails"]
meetings_collection = db["Meetings"]
user_credentials_collection = db["UserGoogleCredentials"]


# ------------------ Google OAuth Setup ------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rg6rwqiydysl6ocy.cloudworkstations.dev/api/google/oauth2callback"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


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
class MeetingRequest(BaseModel):
    startupName: str
    founderEmail: EmailStr
    investorEmail: EmailStr
    proposedDateTime: datetime

class RespondMeeting(BaseModel):
    meetingId: str
    action: str  # accept or decline


class OAuthRequest(BaseModel):
    email: EmailStr
# ----------------- Socket.IO Server -----------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("aianalyst-61509-firebase-adminsdk-fbsvc-d2fbeecd8c.json")  # download from Firebase console
firebase_admin.initialize_app(cred)


# ----------------- Helper Functions -----------------
def check_investor_interest(founder_email, investor_email):
    """Check if investor is allowed to request a meeting."""
    record = interests_collection.find_one({
        "founderEmail": founder_email,
        "investorEmail": investor_email,
        "status": "accepted"
    })
    return record is not None

# ------------------ Helper: Check Time Conflict ------------------
# def check_time_conflict(email, proposed_datetime, duration_hours=1):
#     start = proposed_datetime
#     end = proposed_datetime + timedelta(hours=duration_hours)
#     conflict = meetings_collection.find_one({
#         "$or": [
#             {"founderEmail": email},
#             {"investorEmail": email}
#         ],
#         "status": {"$in": ["accepted"]},
#         "$and": [
#             {"proposedDateTime": {"$lt": end}},
#             {"proposedDateTime": {"$gte": start - timedelta(hours=duration_hours)}}
#         ]
#     })
#     return conflict is not None


# def check_time_conflict(email, proposed_datetime, duration_minutes=30):
#     start = proposed_datetime
#     end = proposed_datetime + timedelta(hours=duration_minutes)

#     meeting_conflict = meetings_collection.find_one({
#         "$or": [
#             {"founderEmail": email},
#             {"investorEmail": email}
#         ],
#         "status": {"$in": ["pending", "accepted"]},
#         "$expr": {
#             "$and": [
#                 {"$lt": ["$proposedDateTime", end]},   # existing start < new end
#                 {"$gt": ["$endTime", start]}           # existing end > new start
#             ]
#         }
#     })
#     # 2️⃣ Check conflicts with booked founder slots
#     # slot_conflict = founder_slots_collection.find_one({
#     #     "founderEmail": email,
#     #     "status": "booked",
#     #     "$expr": {
#     #         "$and": [
#     #             {"$lt": ["$startTime", end]},
#     #             {"$gt": ["$endTime", start]}
#     #         ]
#     #     }
#     # })

#     #return meeting_conflict is not None or slot_conflict is not None
#     return meeting_conflict is not None 


def check_time_conflict(email, proposed_datetime, duration_minutes=30, exclude_meeting_id=None):
    start = proposed_datetime
    end = proposed_datetime + timedelta(minutes=duration_minutes)

    query = {
        "$or": [
            {"founderEmail": email},
            {"investorEmail": email}
        ],
        "status": {"$in": ["pending", "accepted"]},
        "$expr": {
            "$and": [
                {"$lt": ["$proposedDateTime", end]},
                {"$gt": ["$endTime", start]}
            ]
        }
    }

    # 👇 exclude the same meeting being accepted
    if exclude_meeting_id:
        query["_id"] = {"$ne": ObjectId(exclude_meeting_id)}

    meeting_conflict = meetings_collection.find_one(query)
    return meeting_conflict is not None


# ------------------ Generate and Store Slots ------------------
# @app.post("/api/founder/slots")
# def generate_and_store_slots(founderEmail: str, date: str):
#     """
#     Generate 30-min founder slots between 9 AM - 6 PM
#     excluding 1 PM - 2 PM, and store in MongoDB.
#     """
#     try:
#         base_date = datetime.strptime(date, "%Y-%m-%d")
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

#     # Check if slots already exist
#     existing = list(founder_slots_collection.find({"founderEmail": founderEmail, "date": date}))
#     if existing:
#         return {"message": "Slots already exist for this founder on this date", "slots": existing}

#     ist = pytz.timezone("Asia/Kolkata")
#     start_time = datetime.combine(base_date, time(9, 0, tzinfo=ist))
#     end_time = datetime.combine(base_date, time(18, 0, tzinfo=ist))
#     lunch_start = datetime.combine(base_date, time(13, 0, tzinfo=ist))
#     lunch_end = datetime.combine(base_date, time(14, 0, tzinfo=ist))

#     slot_duration = timedelta(minutes=30)
#     slots_to_insert = []
#     current = start_time

#     while current < end_time:
#         next_slot = current + slot_duration

#         # Skip lunch hour slots
#         if next_slot <= lunch_start or current >= lunch_end:
#             slot_doc = {
#                 "founderEmail": founderEmail,
#                 "date": date,
#                 "startTime": current,
#                 "endTime": next_slot,
#                 "status": "available",
#                 "createdAt": datetime.utcnow()
#             }
#             slots_to_insert.append(slot_doc)

#         current = next_slot

#     if not slots_to_insert:
#         raise HTTPException(status_code=400, detail="No valid slots generated.")

#     # Insert slots in MongoDB
#     founder_slots_collection.insert_many(slots_to_insert)

#     return {"message": "✅ Slots generated and stored successfully.", "totalSlots": len(slots_to_insert)}

# ------------------ Get Available Slots ------------------
# @app.get("/api/founder/slots")
# def get_slots(founderEmail: str, date: str):
#     """Retrieve all available slots for a founder on a specific date."""
#     slots = list(founder_slots_collection.find(
#         {"founderEmail": founderEmail, "date": date},
#         {"_id": 0}
#     ))
#     if not slots:
#         raise HTTPException(status_code=404, detail="No slots found for this date.")
#     return {"date": date, "slots": slots}

# ------------------ Get Available Slots (Auto-Generate if Not Exists & Only Available) ------------------
@app.get("/api/founder/slots")
def get_slots(founderEmail: str, date: str):
    """
    Retrieve all available slots for a founder on a specific date.
    If slots do not exist yet, generate them automatically.
    Only return slots with status 'available'.
    """
    # Parse date
    try:
        base_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Fetch existing available slots
    available_slots = list(founder_slots_collection.find(
        {"founderEmail": founderEmail, "date": date, "status": "available"}
    ))

    if available_slots:
        # Convert ObjectId and datetime to string for JSON
        for slot in available_slots:
            slot["_id"] = str(slot["_id"])
            slot["startTime"] = slot["startTime"].astimezone(pytz.timezone("Asia/Kolkata")).isoformat()
            slot["endTime"] = slot["endTime"].astimezone(pytz.timezone("Asia/Kolkata")).isoformat()
            slot["createdAt"] = slot["createdAt"].isoformat()
        return {"date": date, "slots": available_slots}

    # Check if any slots exist at all
    existing_slots = list(founder_slots_collection.find(
        {"founderEmail": founderEmail, "date": date}
    ))
    if existing_slots:
        # Slots exist but none are available
        return {"date": date, "slots": []}

    # No slots exist, generate automatically
    ist = pytz.timezone("Asia/Kolkata")
    start_time = ist.localize(datetime.combine(base_date, time(9, 0)))
    end_time = ist.localize(datetime.combine(base_date, time(18, 0)))
    lunch_start = ist.localize(datetime.combine(base_date, time(13, 0)))
    lunch_end = ist.localize(datetime.combine(base_date, time(14, 0)))

    slot_duration = timedelta(minutes=30)
    slots_to_insert = []
    current = start_time

    while current < end_time:
        next_slot = current + slot_duration
        # Skip lunch
        if next_slot <= lunch_start or current >= lunch_end:
            slot_doc = {
                "founderEmail": founderEmail,
                "date": date,
                "startTime": current,
                "endTime": next_slot,
                "status": "available",
                "createdAt": datetime.utcnow()
            }
            slots_to_insert.append(slot_doc)
        current = next_slot

    if not slots_to_insert:
        raise HTTPException(status_code=400, detail="No valid slots generated.")

    # Insert slots in MongoDB
    result = founder_slots_collection.insert_many(slots_to_insert)

    # Convert inserted slots to JSON-friendly format
    for slot, oid in zip(slots_to_insert, result.inserted_ids):
        slot["_id"] = str(oid)
        slot["startTime"] = slot["startTime"].isoformat()
        slot["endTime"] = slot["endTime"].isoformat()
        slot["createdAt"] = slot["createdAt"].isoformat()

    return {"date": date, "slots": slots_to_insert}


# def get_calendar_service(email: str):
#     user_cred = user_credentials_collection.find_one({"email": email})
#     if not user_cred:
#         raise HTTPException(status_code=403, detail=f"Google Calendar not connected for {email}")

#     creds = Credentials.from_authorized_user_info(user_cred["credentials"], SCOPES)
#     if creds.expired and creds.refresh_token:
#         creds.refresh(GoogleRequest())
#         user_credentials_collection.update_one(
#             {"email": email},
#             {"$set": {"credentials": json.loads(creds.to_json())}}
#         )
#     return build("calendar", "v3", credentials=creds)


# def get_calendar_service(email: str):
#     user_cred = user_credentials_collection.find_one({"email": email})
#     if not user_cred:
#         raise HTTPException(status_code=403, detail=f"Google Calendar not connected for {email}")

#     creds_data = user_cred["credentials"]

#     # 👇 Ensure expiry is a string (convert datetime → ISO string)
#     if isinstance(creds_data.get("expiry"), datetime):
#         creds_data["expiry"] = creds_data["expiry"].isoformat() + "Z"

#     creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

#     if creds.expired and creds.refresh_token:
#         creds.refresh(GoogleRequest())
#         user_credentials_collection.update_one(
#             {"email": email},
#             {"$set": {"credentials": json.loads(creds.to_json())}}
#         )

#     return build("calendar", "v3", credentials=creds)

def get_calendar_service(user_email):
    creds_data = user_credentials_collection.find_one({"email": user_email})
    if not creds_data or "credentials" not in creds_data:
        raise HTTPException(status_code=401, detail=f"Google authorization expired for {user_email}. Please reconnect your calendar.")

    creds_data = creds_data["credentials"]

    # ✅ Convert expiry to string if it's a datetime
    if isinstance(creds_data.get("expiry"), datetime):
        creds_data["expiry"] = creds_data["expiry"].isoformat() + "Z"

    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

    # ✅ Auto-refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            user_credentials_collection.update_one(
                {"email": user_email},
                {"$set": {"credentials": json.loads(creds.to_json())}}
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Google authorization expired for {user_email}. Please reconnect your calendar.")

    return build("calendar", "v3", credentials=creds)

# ------------------ OAuth Flow ------------------
# @app.get("/api/google/authorize")
# def authorize_google(email: str):
#     """Generate OAuth consent screen URL"""
#     from google_auth_oauthlib.flow import Flow
#     flow = Flow.from_client_config(
#         {
#             "web": {
#                 "client_id": GOOGLE_CLIENT_ID,
#                 "client_secret": GOOGLE_CLIENT_SECRET,
#                 "redirect_uris": [REDIRECT_URI],
#                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                 "token_uri": "https://oauth2.googleapis.com/token"
#             }
#         },
#         scopes=SCOPES
#     )
#     flow.redirect_uri = REDIRECT_URI
#     authorization_url, state = flow.authorization_url(
#         access_type="offline",
#         include_granted_scopes="true",
#         prompt="consent",
#         state=email
#     )
#     return {"auth_url": authorization_url}


# @app.get("/api/google/oauth2callback")
# def oauth2callback(code: str, state: str):
#     """Callback from Google with tokens"""
#     from google_auth_oauthlib.flow import Flow
#     try :
#         email, role = state.split("|") 
#         flow = Flow.from_client_config(
#             {
#                 "web": {
#                     "client_id": GOOGLE_CLIENT_ID,
#                     "client_secret": GOOGLE_CLIENT_SECRET,
#                     "redirect_uris": [REDIRECT_URI],
#                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                     "token_uri": "https://oauth2.googleapis.com/token"
#                 }
#             },
#             scopes=SCOPES
#         )
#         flow.redirect_uri = REDIRECT_URI
#         flow.fetch_token(code=code)
#         creds = flow.credentials

#         user_credentials_collection.update_one(
#             {"email": state},
#             {"$set": {"credentials": json.loads(creds.to_json())}},
#             upsert=True
#         )
#         #return RedirectResponse(url=f"https://3000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/investor-dashboard?calendarConnected=true")
#         # Redirect based on role
#         if role == "founder":
#             dashboard_url = "https://3000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/founder-dashboard?calendarConnected=true"
#         else:
#             dashboard_url = "https://3000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/investor-dashboard?calendarConnected=true"

#         return RedirectResponse(url=dashboard_url)
#     except Exception as e:
#         print("❌ OAuth Callback Error:", e)
#         raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google/authorize")
def authorize_google(email: str):
    """
    Redirect user to Google OAuth consent screen.
    Role is optional and defaults to founder.
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=email
    )
    print(authorization_url)
    # ✅ Redirect browser to Google consent screen
    return RedirectResponse(url=authorization_url)
    # return {"auth_url": authorization_url}


@app.get("/api/google/oauth2callback")
def oauth2callback(code: str, state: str):
    """
    Callback from Google with code.
    Save credentials and redirect user to dashboard.
    """
    try:
        email, role = state.split("|")

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save credentials in MongoDB
        user_credentials_collection.update_one(
            {"email": email},
            {"$set": {"credentials": json.loads(creds.to_json())}},
            upsert=True
        )

        # Redirect user to appropriate dashboard
        if role == "founder":
            dashboard_url = "https://3000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev/founder-dashboard?calendarConnected=true"
        else:
            dashboard_url = "https://3000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev/investor-home?calendarConnected=true"

        return RedirectResponse(url=dashboard_url)
    except Exception as e:
        print("❌ OAuth Callback Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google/is_connected")
def is_connected(email: str):
    user = user_credentials_collection.find_one({"email": email})
    return {"connected": bool(user)}

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
async def auth_user(request: FastAPIRequest):
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
async def add_founder_details(request: FastAPIRequest, data: FounderDetails):
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
async def add_startup_details(request: FastAPIRequest, data: StartupDetails):
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
def get_startup_details(request: FastAPIRequest):
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

# ------------------ Create Meeting ------------------
@app.post("/api/meetings")
def create_meeting(meeting: MeetingRequest):
    if not check_investor_interest(meeting.founderEmail, meeting.investorEmail):
        raise HTTPException(status_code=403, detail="Investor not allowed to request meeting")

    if check_time_conflict(meeting.founderEmail, meeting.proposedDateTime) or \
       check_time_conflict(meeting.investorEmail, meeting.proposedDateTime):
        raise HTTPException(status_code=409, detail="Meeting time conflicts with another meeting")

    meeting_end = meeting.proposedDateTime + timedelta(minutes=30)

    meeting_doc = {
        "startupName": meeting.startupName,
        "founderEmail": meeting.founderEmail,
        "investorEmail": meeting.investorEmail,
        "proposedDateTime": meeting.proposedDateTime,
        "endTime": meeting_end,
        "status": "pending",
        "createdAt": datetime.utcnow()
    }

    # Insert into Meetings collection
    result = meetings_collection.insert_one(meeting_doc)
    meeting_id = result.inserted_id

    # Update FounderSlots — mark slot as "booked"
    slot_update = founder_slots_collection.update_one(
        {
            "founderEmail": meeting.founderEmail,
            "startTime": {"$lte": meeting.proposedDateTime},
            "endTime": {"$gt": meeting.proposedDateTime},
            "status": "available"
        },
        {"$set": {"status": "booked"}}
    )

     # Debug info (optional)
    if slot_update.modified_count == 0:
        print(f"⚠️ No matching available slot found for {meeting.founderEmail} at {meeting.proposedDateTime}")

    meeting_doc["_id"] = str(meeting_id)
    return {"message": "✅ Meeting created successfully", "meeting": meeting_doc}
    # meeting_doc = meeting.dict()
    # meeting_doc["status"] = "pending"
    # meeting_doc["createdAt"] = datetime.utcnow()
    # result = meetings_collection.insert_one(meeting_doc)
    # meeting_doc["_id"] = str(result.inserted_id)
    # return meeting_doc


# ------------------ Accept / Decline Meeting ------------------
# @app.post("/api/meetings/respond",response_model=None)
# def respond_meeting(response: RespondMeeting):
#     meeting = meetings_collection.find_one({"_id": ObjectId(response.meetingId)})
#     if not meeting:
#         raise HTTPException(status_code=404, detail="Meeting not found")

#     if response.action == "accept":
#         if check_time_conflict(meeting["founderEmail"], meeting["proposedDateTime"]) or \
#            check_time_conflict(meeting["investorEmail"], meeting["proposedDateTime"]):
#             raise HTTPException(status_code=409, detail="Meeting time conflicts with another meeting")

#         # Create Google Meet event in both users' calendars
#         founder_service = get_calendar_service(meeting["founderEmail"])
#         investor_service = get_calendar_service(meeting["investorEmail"])

#         event_body = {
#             'summary': f"Startup Meeting - {meeting['startupName']}",
#             'start': {'dateTime': meeting['proposedDateTime'].isoformat(), 'timeZone': 'Asia/Kolkata'},
#             'end': {'dateTime': (meeting['proposedDateTime'] + timedelta(hours=1)).isoformat(), 'timeZone': 'Asia/Kolkata'},
#             'attendees': [
#                 {'email': meeting['founderEmail']},
#                 {'email': meeting['investorEmail']}
#             ],
#             'conferenceData': {
#                 'createRequest': {
#                     'requestId': str(response.meetingId),
#                     'conferenceSolutionKey': {'type': 'hangoutsMeet'}
#                 }
#             }
#         }

#         created_event = founder_service.events().insert(
#             calendarId="primary", body=event_body, conferenceDataVersion=1
#         ).execute()

#         hangout_link = created_event.get('hangoutLink')

#         # Add to investor's calendar
#         investor_service.events().insert(
#             calendarId="primary", body=event_body, conferenceDataVersion=1
#         ).execute()

#         meetings_collection.update_one(
#             {"_id": ObjectId(response.meetingId)},
#             {"$set": {"status": "accepted", "hangoutLink": hangout_link}}
#         )
#         return {"message": "Meeting accepted", "hangoutLink": hangout_link}

#     elif response.action == "decline":
#         meetings_collection.update_one(
#             {"_id": ObjectId(response.meetingId)},
#             {"$set": {"status": "declined"}}
#         )
#         return {"message": "Meeting declined"}

#     raise HTTPException(status_code=400, detail="Invalid action")

@app.post("/api/meetings/respond")
def respond_meeting(response: RespondMeeting):
    # Fetch the meeting
    meeting = meetings_collection.find_one({"_id": ObjectId(response.meetingId)})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if response.action == "accept":
        # Check time conflicts
        if check_time_conflict(meeting["founderEmail"], meeting["proposedDateTime"], exclude_meeting_id=response.meetingId) or \
           check_time_conflict(meeting["investorEmail"], meeting["proposedDateTime"], exclude_meeting_id=response.meetingId):
            raise HTTPException(status_code=409, detail="Meeting time conflicts with another meeting")

        # Get calendar service for founder only (organizer)
        founder_service = get_calendar_service(meeting["founderEmail"])

         # Set 30-min duration
        start_time = meeting["proposedDateTime"]
        end_time = meeting["proposedDateTime"] + timedelta(minutes=30)
        # Prepare Google Calendar event
        event_body = {
            'summary': f"Startup Meeting - {meeting['startupName']}",
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata'
            },
            'attendees': [{'email': meeting['investorEmail']}],
            'conferenceData': {
                'createRequest': {
                    'requestId': str(response.meetingId),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        # Insert event in founder's Google Calendar
        created_event = founder_service.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="all"
        ).execute()

        hangout_link = created_event.get('hangoutLink')

        # Update Meetings table
        meetings_collection.update_one(
            {"_id": ObjectId(response.meetingId)},
            {"$set": {"status": "accepted", "hangoutLink": hangout_link, "endTime": end_time}}
        )

        # Update FounderSlots again if needed
        founder_slots_collection.update_one(
            {
                "founderEmail": meeting["founderEmail"],
                "startTime": {"$lte": start_time},
                "endTime": {"$gt": start_time}
            },
            {"$set": {"status": "booked"}}
        )

        return {"message": "✅ Meeting accepted and event added to calendar", "hangoutLink": hangout_link}

    elif response.action == "decline":
        meetings_collection.update_one(
            {"_id": ObjectId(response.meetingId)},
            {"$set": {"status": "declined"}}
        )

        # Free up the slot again
        founder_slots_collection.update_one(
            {
                "founderEmail": meeting["founderEmail"],
                "startTime": {"$lte": meeting["proposedDateTime"]},
                "endTime": {"$gt": meeting["proposedDateTime"]}
            },
            {"$set": {"status": "available"}}
        )

        return {"message": "Meeting declined and slot released"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    #     # Prepare event body
    #     event_body = {
    #         'summary': f"Startup Meeting - {meeting['startupName']}",
    #         'start': {
    #             'dateTime': meeting['proposedDateTime'].isoformat(),
    #             'timeZone': 'Asia/Kolkata'
    #         },
    #         'end': {
    #             'dateTime': (meeting['proposedDateTime'] + timedelta(hours=1)).isoformat(),
    #             'timeZone': 'Asia/Kolkata'
    #         },
    #         'attendees': [
    #             {'email': meeting['investorEmail']}  # only invite investor
    #         ],
    #         'conferenceData': {
    #             'createRequest': {
    #                 'requestId': str(response.meetingId),
    #                 'conferenceSolutionKey': {'type': 'hangoutsMeet'}
    #             }
    #         }
    #     }

    #     # Insert event in founder's calendar
    #     created_event = founder_service.events().insert(
    #         calendarId="primary",
    #         body=event_body,
    #         conferenceDataVersion=1,
    #         sendUpdates="all"  # sends invites to attendee
    #     ).execute()

    #     hangout_link = created_event.get('hangoutLink')

    #     # Update MongoDB meeting
    #     meetings_collection.update_one(
    #         {"_id": ObjectId(response.meetingId)},
    #         {"$set": {"status": "accepted", "hangoutLink": hangout_link}}
    #     )

    #     return {"message": "Meeting accepted", "hangoutLink": hangout_link}

    # elif response.action == "decline":
    #     meetings_collection.update_one(
    #         {"_id": ObjectId(response.meetingId)},
    #         {"$set": {"status": "declined"}}
    #     )
    #     return {"message": "Meeting declined"}

    # else:
    #     raise HTTPException(status_code=400, detail="Invalid action")

# ------------------ Fetch Meetings ------------------
@app.get("/api/meetings/founder/{founder_email}")
def get_founder_meetings(founder_email: str):
    meetings = list(meetings_collection.find({"founderEmail": founder_email}))
    for m in meetings:
        m["_id"] = str(m["_id"])
        m["proposedDateTime"] = m["proposedDateTime"].astimezone(pytz.UTC).isoformat()
        m["endTime"] = m["endTime"].astimezone(pytz.UTC).isoformat()
    
    return {"meetings": meetings}
    # for m in meetings:
    #     m["_id"] = str(m["_id"])
    # return meetings

@app.get("/api/meetings/investor/{investor_email}")
def get_investor_meetings(investor_email: str):
    meetings = list(meetings_collection.find({"investorEmail": investor_email}))
    for m in meetings:
        m["_id"] = str(m["_id"])
        m["proposedDateTime"] = m["proposedDateTime"].astimezone(pytz.UTC).isoformat()
        m["endTime"] = m["endTime"].astimezone(pytz.UTC).isoformat()
    
    return {"meetings": meetings}
    # for m in meetings:
    #     m["_id"] = str(m["_id"])
    # return meetings
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


@app.get("/api/chat/")
def get_chat_history(participants: List[str] = Query(...)):
    participants_sorted = sorted(participants)
    chat = chat_collection.find_one({"participants": participants_sorted})
    if chat:
        chat["_id"] = str(chat["_id"])
        for msg in chat["messages"]:
            msg["timestamp"] = msg["timestamp"].isoformat()+ "Z" # convert datetime -> string
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




@app.post("/api/interests/accept")
def accept_interest(data: AcceptInterest):
    result = interests_collection.update_one(
        {"founderEmail": data.founderEmail, "investorEmail": data.investorEmail},
        {"$set": {"status": "accepted"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Interest not found")

    return {"message": "Interest accepted"}