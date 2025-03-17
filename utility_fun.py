from crewai_tools import BaseTool
from crewai import Agent
from crewai import Task
from crewai import Crew
from fastapi import UploadFile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import PyPDF2
import smtplib

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