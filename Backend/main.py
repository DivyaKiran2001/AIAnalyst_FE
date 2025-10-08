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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
users_collection = db["Users"]

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


# # Store OTPs temporarily: {email: {"otp": "123456", "expires": datetime}}
# otp_store = {}

# SMTP_SERVER = "smtp.gmail.com"  # or your SMTP server
# SMTP_PORT = 587
# SMTP_EMAIL = "genaihackathon4@gmail.com"
# SMTP_PASSWORD = "hbkiyzjtvmcdgvin"  # Use App Password if Gmail

# try:
#     server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#     server.starttls()
#     server.login(SMTP_EMAIL, SMTP_PASSWORD)
#     print("Login successful")
#     server.quit()
# except Exception as e:
#     print("Error:", e)

# class EmailRequest(BaseModel):
#     email: EmailStr

# class OTPRequest(BaseModel):
#     email: EmailStr
#     otp: str

# def generate_otp(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# def send_email(to_email, otp):
#     subject = "Your OTP for Startup Registration"
#     body = f"Your OTP is: {otp}\nIt will expire in 5 minutes."
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = SMTP_EMAIL
#     msg['To'] = to_email

#     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_EMAIL, SMTP_PASSWORD)
#         server.send_message(msg)


# @app.post("/send-otp")
# def send_otp(request: EmailRequest):
#     """Generate and send OTP to user's email."""
#     try:
#         otp = generate_otp()
#         otp_store[request.email] = {
#             "otp": otp,
#             "expires": datetime.utcnow() + timedelta(minutes=5)
#         }

#         print(f"📧 Sending OTP to: {request.email}, OTP: {otp}")

#         send_email(request.email, otp)

#         print("✅ OTP sent successfully")
#         return {"message": "OTP sent successfully"}
    
#     except Exception as e:
#         print("❌ ERROR sending OTP:", e)
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/verify-otp")
# def verify_otp(request: OTPRequest):
#     record = otp_store.get(request.email)
#     if not record:
#         raise HTTPException(status_code=400, detail="No OTP sent for this email")
#     if datetime.utcnow() > record["expires"]:
#         del otp_store[request.email]
#         raise HTTPException(status_code=400, detail="OTP expired")
#     if record["otp"] != request.otp:
#         raise HTTPException(status_code=400, detail="Invalid OTP")
    
#     # OTP verified, delete it
#     del otp_store[request.email]
#     return {"message": "OTP verified successfully"}

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("aianalyst-61509-firebase-adminsdk-fbsvc-b559389ff7.json")  # download from Firebase console
firebase_admin.initialize_app(cred)

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