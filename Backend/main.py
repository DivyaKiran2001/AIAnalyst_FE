from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.middleware.cors import CORSMiddleware

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

users_collection = db["Users"]

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("aianalyst-61509-firebase-adminsdk-fbsvc-ae129ed19c.json")  # download from Firebase console
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
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "uid": decoded_token["uid"],
        "email": email,
        "password": password or "",
        "role": role
    })

    print(f"Inserted user: {email} as {role}")

    return {"status": "success", "user": {"email": email, "role": role}}
