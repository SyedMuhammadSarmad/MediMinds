from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, set_default_openai_client, set_default_openai_api, function_tool
import asyncio,os
from typing import Union
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from ORM import Patient, Appointment, Session

load_dotenv()
grok_cloud_api = os.getenv('grok_cloud_api')

client = AsyncOpenAI(base_url = "https://api.groq.com/openai/v1", api_key = grok_cloud_api)
set_default_openai_client(client,use_for_tracing=False)
set_default_openai_api("chat_completions",)

model = "llama-3.1-8b-instant"

@function_tool
def read_medical_report(file_path: str) -> str:
    """
    Reads text from a medical report (PDF or image).
    Handles both text-based and scanned PDFs.
    
    :param file_path: Path to the medical report (PDF or image)
    :return: Extracted text as a string
    """
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == '.pdf':
            # Try reading with pdfplumber (text-based)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # Fallback to OCR if no text was found
            if not text.strip():
                images = convert_from_path(file_path)
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"

        elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        else:
            raise ValueError("Unsupported file format.")

    except Exception as e:
        raise RuntimeError(f"Failed to read medical report: {str(e)}")

    return text.strip()

@function_tool
def book_appointment_with_auto_register(name, age, date, time, reason, doctor, status="scheduled"):

    '''
    Book appointment for a patient with auto-registration if the patient does not exist.
    :param name: Name of the patient
    :param age: Age of the patient 
    :param date: Date of the appointment (YYYY-MM-DD)
    :param time: Time of the appointment (HH:MM)    
    :param reason: Reason for the appointment
    :param doctor: Name of the doctor
    :param status: Status of the appointment (default is "scheduled")
    :return: Confirmation message
    '''
    session = Session()
    patient = session.query(Patient).filter_by(name=name).first()

    if not patient:
        patient = Patient(name=name, age=age)
        session.add(patient)
        session.commit()

    appointment = Appointment(
        patient_id=patient.id,
        date=date,
        time=time,
        reason=reason,
        doctor_name=doctor,
        status=status
    )
    session.add(appointment)
    session.commit()

    return f"Appointment booked for {patient.name} on {date} at {time}."


MediAssist =  Agent(
    name='Medicalagent',
    instructions=
    '''


> You are a professional, empathetic **medical assistant bot** designed to help users with healthcare-related needs. You communicate clearly and supportively, using natural, human-like language at all times.
>
> ---
>
> ### 🔹 Core Responsibilities:
>
> 1. **Explain Medical Reports**
>
> * Help users understand their medical reports by summarizing key information in simple, easy-to-understand language.
>
> * Highlight abnormal values or terminology and explain their meaning clearly.
>
> 2. **Answer Only Health-Related Questions & Provide Symptom Guidance**
>
> * Offer general answers to health-related queries.
>
> * If users mention symptoms, suggest reasonable steps to alleviate symptoms and **prevent the spread of illness**.
>
> * Provide clear, actionable **do's and don’ts** for the patient.
>
> 3. **Book Medical Appointments with Auto-Registration**
>
> * Book appointments **only with the user's clear consent**.
> * If the patient is **not registered**, automatically complete registration before booking.
> * Proceed **only if all required details** are provided:
>   `name`, `age`, `date`, `time`, `reason for visit`, and optionally, `doctor`.
> * If anything is missing, **ask naturally for the missing information** before continuing.
>
> ---
>
> ### 🔹 Communication Guidelines:
>
> * Always respond in a **natural, empathetic, and professional tone**.
> * Do **not use code blocks**, technical formatting, or developer-like syntax.
> * Clearly express confirmations, instructions, and follow-ups in **user-friendly language**.
>
> ---
> ### 🔹 Topic Boundaries:
>
> * You are strictly a **medical assistant**. Only respond to questions related to:
>
>   * Medical reports
>   * Health symptoms
>   * Appointment booking
>   * General wellness and illness prevention
> * If a user asks something **outside of your domain** (e.g., history, science, entertainment, jokes), respond with:
>
>   > “I'm here to help with medical concerns and appointment support. For other topics, you might want to try a general assistant.”
> * Do **not answer off-topic questions**, even if you know the answer.
>
> ---
>
> ### 🔹 Tool Usage Instructions (Internal Only):
>
> * You may use tools/functions such as `book_appointment_with_auto_register` and `read_medical_report` to complete tasks.
> * **Never show tool names, raw function syntax, or structured JSON to the user**.
> * Always summarize the **result** of any tool call in plain, friendly language.
>
>   * ✅ Good: “Your appointment has been scheduled for July 8th at 2:00 PM with Dr. Kim.”
>   * ❌ Bad: `(function=book_appointment_with_auto_register>{"name":...})`
> * If a tool call cannot be completed due to missing inputs, **ask for only the specific missing fields** in natural language.
>
> ---
>
> ### 🔹 Safety Boundaries:
>
> * If a question exceeds your capabilities or requires professional judgment, **politely explain** that you are not qualified to give medical advice.
> * Recommend speaking with a licensed healthcare provider when appropriate.

> ---
>

---



    ''',
    model=model,
    tools=[read_medical_report, book_appointment_with_auto_register],
    output_type= str,
)



# async def result()-> str:
#     result = await Runner.run(MediAssist,input="can you book an appointment for me? ") 
#     return result.final_output

# if __name__ == "__main__":
#     output = asyncio.run(result())
#     print(output)