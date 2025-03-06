
# **Health Recommendation API**

  

## **Overview**

  

This API is designed to process blood test reports, analyze them using Agents AI, search for relevant health articles, and generate personalized health recommendations. The final analysis and recommendations are sent via email to the user.

  

## **Features**

  

Secure user authentication

  

PDF blood report processing

  

AI-driven health analysis

  

Web search for relevant health articles

  

Personalized health recommendations

  

Email delivery of results

  

## **Technologies Used**

  

**FastAPI** (Backend framework)

  

**CrewAI** (Multi-agent AI workflow)

  

**PyPDF2** (PDF reading)

  

**OAuth2** (Authentication)

  

**SMTP** (Email sending)

  

**Groq LLM** (AI processing)

  

## **Installation**

  

Prerequisites

  

Ensure you have the following installed:

  

Python 3.10+

  

Pip (Python package manager)

  

Virtual environment (recommended)

  

## **Steps**

  

1. Clone the repository:

```bash

git  clone  https://github.com/tanugoyal123/Health_recommendation_system.git

```

  

2. Navigate to the project directory:

```bash

cd  Health_recommendation_system

```

  

3. Create and activate a virtual environment:

```bash

python  -m  venv  venv

source  venv/Scripts/activate

```

  

4. Install dependencies:

  

```bash

pip  install  -r  requirements.txt

```

  

5. Set up environment variables in a .env file:

```bash

GROQ_API_KEY=your_groq_api_key

PASSKEY=your_email_password

```

## **Usage**

  

### Running the API

  

Start the FastAPI server:

```bash

uvicorn  test:app  --reload

```

  

### API Endpoints

  

1. User Authentication

  

   - POST /token

  

   - Request: Username & password

  

    - Response: JWT access token

  

2. Upload Blood Report

  

      -  POST /upload-report/

  

      - Request: PDF file & email

  

      - Response: Sends an email with analysis, articles, and recommendations

  

3. Health Recommendation Analysis

  

    Uses CrewAI agents:

  

     - Health Expert: Analyzes blood report

  

    - Web Search Agent: Finds relevant articles

  

   - Recommendation Agent: Generates health advice

  

### Example Request

```bash

curl  -X  'POST'  \

'http://127.0.0.1:8000/upload-report/' \

-H  'Authorization: Bearer YOUR_ACCESS_TOKEN'  \

-F 'file=@path/to/report.pdf' \

-F  'email=user@example.com'

  

```