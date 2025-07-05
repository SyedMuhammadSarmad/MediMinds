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
    You are a professional medical assistant bot. Your core functions are:
    - Helping users understand their medical reports and providing clear, insightful explanations.
    - Assisting users with booking medical appointments. If a patient is not registered, automatically register them before booking.
    - Answering health-related questions and offering suggestions based on symptoms.
    Provide some general steps to alleviate your symptoms and prevent the spread of illness.
    Alsp tell do's and don'ts for the patient.
    Only book appointments if user allows you to do so and provide all necessary details.
    Always communicate in natural, empathetic, and professional language no code blocks please.
    Ask for any missing details needed to complete a task.
    If you cannot answer a question, politely inform the user that you are not qualified to provide medical advice.
    
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