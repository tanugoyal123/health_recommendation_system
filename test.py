

from typing import Annotated

from utility_fun import crewai_function, send_email
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form,Depends,HTTPException
import os
from dotenv import load_dotenv


load_dotenv()

#setting the environment variables
os.environ['GROQ_API_KEY']= os.getenv("GROQ_API_KEY")
passkey=os.getenv("PASSKEY")

# defining a fakeuserdb for authentication
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

# Initialising FastAPI app
app = FastAPI()

# Define a base user model using Pydantic
class user(BaseModel):
    username : str 
    full_name : str
    email : str
    disabled : bool
    

# Extend the user model to include hashed password for authentication    
class userIndb(user):
    hashed_password : str
    
#password hashing
def fake_hash_password(password: str):
    return "fakehashed" 

#Function to retrieve user details from the database
def getuser(db,username):
    if username in db:
        u=db[username]
        return userIndb(u)
    else:
        
        raise HTTPException(status_code=404, detail="User does not exist")
        


# OAuth2 token-based authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint to authenticate user and issue a token
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Get user details from the fake database
    user_dict = fake_users_db.get(form_data.username)
    # Raise error if user does not exist
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username")
    # Create a user object using the user details
    user = userIndb(**user_dict)

    # Hash the entered password and compare with stored password
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        # Raise error if password is incorrect
        raise HTTPException(status_code=400, detail="Incorrect password")
    # Return the token upon successful authentication
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoint to upload a blood test report and process it
@app.post("/upload-report/")
async def upload_report(email: str = Form(...), file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    # Process the PDF using the CrewAI pipeline
    analysis, search, health_recommendations = crewai_function(file)
    # Define the email subject and server details
    subject = "Health Recommendation"
    smtp_server = "smtp.gmail.com"
    port = 587 
    # Extract recipient name from the email address
    recipient_name = email.split('@')[0]
    # Format the email content
    email_body = f"""
        Dear {recipient_name},

        I hope this email finds you well.

        I wanted to reach out to inform you about the latest updates regarding your blood test report.
         
        ANALYSIS AND SUMMARY OF THE REPORT
        {analysis}
        
        WEBSITES AND ARTICLES RELATED TO YOUR HEALTH CONDITION
        {search}
        
        HEALTH RECOMMENDATION ACCORDING TO YOUR HEALTH
        {health_recommendations}
        
        Thank you.
    """
    # Send the email with the health recommendations
    s= send_email(email, subject, email_body, smtp_server, port)
    return s

# Root endpoint to check if the API is running
@app.get("/")
def read_root():
    return {"message": "Welcome to the Health Recommendation API"}