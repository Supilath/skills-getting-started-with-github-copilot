"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "static")), name="static")

# Setup MongoDB connection

client = MongoClient("mongodb://localhost:27017/")
db = client["school"]
activities_collection = db["activities"]

# Pre-populate the database if empty
if activities_collection.count_documents({}) == 0:
    activities_data = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        {
            "name": "Soccer Team",
            "description": "Join the school soccer team and compete in local leagues",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        {
            "name": "Basketball Club",
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        {
            "name": "Drama Club",
            "description": "Act in plays and participate in theater productions",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        {
            "name": "Art Workshop",
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 16,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        },
        {
            "name": "Math Olympiad",
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["elijah@mergington.edu", "charlotte@mergington.edu"]
        },
        {
            "name": "Science Club",
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu", "harper@mergington.edu"]
        }
    ]
    activities_collection.insert_many(activities_data)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    docs = activities_collection.find({})
    result = {}
    for doc in docs:
        doc.pop('_id', None)
        result[doc['name']] = doc
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email in activity.get("participants", []):
        raise HTTPException(status_code=400, detail="Student already registered")

    if len(activity.get("participants", [])) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="No spots left")

    activities_collection.update_one({"name": activity_name}, {"$push": {"participants": email}})
    return {"message": f"Successfully registered for {activity_name}"}


@app.post("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email not in activity.get("participants", []):
        raise HTTPException(status_code=400, detail="Student is not registered for this activity")

    activities_collection.update_one({"name": activity_name}, {"$pull": {"participants": email}})
    return {"message": f"Successfully unregistered from {activity_name}"}
