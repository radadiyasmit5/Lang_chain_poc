import os
import pickle
from typing import Dict

# LangChain (new approach)
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable, RunnableConfig, RunnableSequence
from langchain.schema import LLMResult

# Example of a built-in LLM that implements Runnable:
# from langchain.chat_models import ChatOpenAI

# Google Auth & Gmail
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

########################
# 1. GMAIL INTEGRATION
########################

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service(credentials_path='credentials.json', token_path='token.json'):
    creds = None

    # Check if token.json exists (stored credentials)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    # If no valid creds are found, go through the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_email_message(to, subject, body):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import base64

    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_gmail(to, subject, body, credentials_path='credentials.json', token_path='token.json'):
    service = get_gmail_service(credentials_path, token_path)
    message = create_email_message(to, subject, body)
    sent = service.users().messages().send(userId='me', body=message).execute()
    return sent

def send_email_tool(to: str, subject: str, body: str):
    """A wrapper that can be used inside a LangChain Tool or simply called directly."""
    result = send_gmail(to, subject, body)
    return f"Email sent successfully: {result}"

###############################
# 2. DEFINE A (FAKE) GEMINI LLM
###############################
class GeminiLLM(Runnable):
    """
    A minimal example of a custom Runnable "LLM". 
    In reality, you'd integrate with Gemini's actual API once it's available.
    """

    def __init__(self, temperature=0.7):
        self.temperature = temperature
    
    def invoke(self, 
               input_str: str, 
               config: RunnableConfig = None) -> str:
        """
        This method is called when we pipe a string into the LLM.
        `invoke` should return the LLM's string response.
        """
        # For demonstration, we'll return a canned text plus the input_str
        return (
            f"(Pretending to be Gemini with temperature={self.temperature}.)\n\n"
            f"Here is a draft email based on your prompt:\n\n"
            f"Hello! This is your requested draft.\n\nOriginal prompt: {input_str}"
        )

    # Optionally, you can implement other methods like batch, stream, etc.
    # But for a simple use case, `invoke` alone might suffice.

###############################
# 3. PROMPT TEMPLATE
###############################
email_prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template=(
        "You are an AI that writes professional emails.\n"
        "Given the user prompt, draft a complete email body.\n\n"
        "User prompt: {prompt}"
    ),
)

###############################
# 4. BUILD THE NEW CHAIN
###############################
# We do NOT use LLMChain anymore. Instead, we create a Runnable "sequence."
# The typical usage: prompt_template | llm
llm = GeminiLLM(temperature=0.7)

# Using RunnableSequence explicitly (useful if you have multiple steps):
email_chain = email_prompt_template | llm


# Alternatively, you can do the simpler pipe:
# email_chain = email_prompt_template | llm

###############################
# 5. USAGE / AGENT-LIKE FLOW
###############################
def ai_gmail_agent_run(user_input: str):
    """
    1. Accepts user prompt (what they want to email).
    2. Uses the new chain to draft an email body.
    3. Shows the user the draft & asks for confirmation.
    4. If confirmed, sends the email.
    """

    # For demonstration, let's parse a fictional "to" and "subject":
    to = "user@example.com"
    subject = "Regarding scheduling a meeting"

    # Step 1: Generate the draft email body
    # Instead of chain.run(), we do chain.invoke():
    draft_email = email_chain.invoke({"prompt": user_input})

    print("\n### AI-Generated Draft Email ###")
    print(f"Subject: {subject}")
    print(draft_email)

    confirm = input("\nDo you want to send this email? (yes/no) ")
    if confirm.lower() == "yes":
        # Step 2: Send email
        send_email_tool(to, subject, draft_email)
        print("Email was sent!")
    else:
        print("Email sending cancelled.")


if __name__ == "__main__":
    user_prompt = input("What would you like to do? ")
    ai_gmail_agent_run(user_prompt)
