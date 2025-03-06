# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 17:29:25 2024

@author: A
"""

from typing import Annotated


from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form,Depends,HTTPException
from crewai_tools import BaseTool
from crewai import Agent
from crewai import Task
from crewai import Crew
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import PyPDF2

load_dotenv()

# Now you can access the variables
os.environ['GROQ_API_KEY']= os.getenv("GROQ_API_KEY")
passkey=os.getenv("PASSKEY")

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


app = FastAPI()

class user(BaseModel):
    username : str 
    full_name : str
    email : str
    disabled : bool
    
    
class userIndb(user):
    hashed_password : str
    
    
def fake_hash_password(password: str):
    return "fakehashed" + password


def getuser(db,username):
    if username in db:
        u=db[username]
        return userIndb(u)
    else:
        
        raise HTTPException(status_code=404, detail="User does not exist")
        



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username")
    user = userIndb(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"access_token": user.username, "token_type": "bearer"}



class Readertool(BaseTool):
    name: str = "PDFReader"
    description: str = "read the file pdf containing the blood report and return the blood report data  in it"
    file:UploadFile

    def _run(self) -> str:
        reader = PyPDF2.PdfReader(self.file.file)  # Use the file object correctly
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text


def crewai_function(file: UploadFile):
    reader = Readertool(file=file)  # Pass the UploadFile object directly
    analysis_agent = Agent(
        role='health expert',
        goal='you are a health expert, use the blood report data from Reader Tool output to analyze and summarize blood report .',
        backstory="An AI assistant leveraging Groq's language model to analyze and summarize blood report data from the reader tool output effectively.",
        llm='groq/llama3-70b-8192',
        tools=[reader]
    )

    analysis_task = Task(
        description='Analyze and summarize the blood report data from the reader Tool output.',
        expected_output=" write a detailed analysis and a detailed summary of the blood report data from Reader Tool output.",
        agent=analysis_agent,
        tools=[reader]
    )

    web_search_agent = Agent(
        role='you are web search expert',
        goal='search for the health related articles on internet based on the analysis and summary of blood report',
        backstory="A web searcher using Groq model for searching web articles on internet",
        llm='groq/llama3-70b-8192'
    )

    web_search_task = Task(
        description='Search the internet for health-related articles based on the analysis and summary of the blood report.',
        expected_output='Provide relevant links and the full content of articles based on analysis and summary of the blood report.',
        agent=web_search_agent
    )
    
    writer_agent = Agent(
        role='you are health recommendation writer',
        goal='write a health recommendation based on the analysis and summary and using the articles',
        backstory="A health recommender that uses Groq AI to write recommended health goals.",
        llm='groq/llama3-70b-8192'
    )

    writer_task = Task(
        description='Understand the analysis and summary of reports and using articles retrieved from the internet write a health recommendation for the patient.',
        expected_output='Provide a health recommendation for the patient including disease prevention, lifestyle changes, treatment options, and overall health management.',
        agent=writer_agent
    )

    crew = Crew(
        agents=[analysis_agent, web_search_agent, writer_agent],
        tasks=[analysis_task, web_search_task, writer_task],
        verbose=True
    )

    result = crew.kickoff()
    
    return analysis_task.output, web_search_task.output, writer_task.output

def send_email(receiver_email: str, subject: str, body: str, smtp_server: str, port: int,):
    sender_email = "tanugoyal.10102001@gmail.com"  # Change to your email
    password =passkey # Change to your email password

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        session = smtplib.SMTP(smtp_server, port)
        session.starttls()  # Secure the connection
        session.login(sender_email, password)

        session.sendmail(sender_email, receiver_email, message.as_string())
        session.quit()

        return {"message": "Email sent successfully!"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}

@app.post("/upload-report/")
async def upload_report(email: str = Form(...), file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    analysis, search, health_recommendations = crewai_function(file)
    subject = "Health Recommendation"
    smtp_server = "smtp.gmail.com"
    port = 587 
    recipient_name = email.split('@')[0]
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
    
    s= send_email(email, subject, email_body, smtp_server, port)
    return s

@app.get("/")
def read_root():
    return {"message": "Welcome to the Health Recommendation API"}