import chainlit as cl
from pathlib import Path
from agent import MediAssist
from agents import Runner, RunHooks, RunContextWrapper, Agent, Tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Any
class MyCustomHook(RunHooks):
    def __init__(self):
        self.tool_msgs = {}

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        if tool.name == "read_medical_report":
            msg = cl.Message(content="`Analyzing report...`")
            await msg.send()
            self.tool_msgs[tool.name] = msg

        elif tool.name == "book_appointment_with_auto_register":
            msg = cl.Message(content="`Booking appointment...`")
            await msg.send()
            self.tool_msgs[tool.name] = msg

    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str) -> None:
        await cl.sleep(0.5)
        msg = self.tool_msgs.get(tool.name)
        if msg:
            await msg.remove()
            del self.tool_msgs[tool.name]

 
 


hooks = MyCustomHook()
   

@cl.on_chat_start
async def start():
    
    cl.user_session.set("role", "doctor")
    cl.user_session.set("step", "main")
    cl.user_session.set("history", [])


    
    await cl.Message(
        content=


"""
# 🩺 AI Medical Assistant

Welcome! How can I help you today?

I can assist you with the following tasks:
- 📄 `Analyze Medical Report`
- 🧠 `Symptom Check`  
- 🛡️ `Do's & Don'ts Recommendations`  
- 📅 `Book Appointment`
"""
    ,
        actions=[
            cl.Action(name="Analyze Report", label="Analyze Medical Report" , payload={"action": "analyze_report"}),
            cl.Action(name="Medical Advice", label="Seek Medical Advice", payload={"action": "medical_advice"}),
            cl.Action(name="Book Appointment", label="Book Appointment", payload={"action": "book_appointment"}),

        ]
    ).send()

@cl.action_callback("Analyze Report")
async def on_analyze_report(action):
    cl.user_session.set("step", "upload")
    await cl.Message(content="Please upload the medical report file (PDF/Image).").send()

@cl.action_callback("Book Appointment")
async def on_book_appointment(action):
    cl.user_session.set("step", "book_appointment")
    await cl.Message(content=
                     '''
Please provide the following details to book an appointment:
- **Name**: Full name of the patient    
- **Age**: Age of the patient
- **Date**: Date of the appointment
- **Time**: Time of the appointment 
- **Reason**: Reason for the appointment
- **Doctor**: Name of the doctor 
### Here is the list of doctors available in the hospital:
| **Specialty**                     | **Description**                                                                 | **Name**         |
|-----------------------------------|---------------------------------------------------------------------------------|-------------------------|
| **General Practitioner (GP)**     | Provides primary care, diagnoses common illnesses, and refers to specialists.   | Dr. Emily Carter        |
| **Cardiologist**                  | Specializes in heart and cardiovascular system disorders.                       | Dr. Michael Patel       |
| **Dermatologist**                 | Treats skin, hair, and nail conditions.                                        | Dr. Sarah Nguyen        |
| **Pediatrician**                  | Focuses on the health of infants, children, and adolescents.                   | Dr. James Wilson       |
| **Neurologist**                   | Diagnoses and treats disorders of the nervous system, like epilepsy or stroke.  | Dr. Lisa Thompson       |
| **Orthopedic Surgeon**            | Specializes in musculoskeletal system, including bones and joints.              | Dr. Robert Kim         |
| **Oncologist**                    | Treats cancer through chemotherapy, radiation, or surgery.                     | Dr. Anna Martinez      |
| **Psychiatrist**                  | Manages mental health disorders, prescribing medication or therapy.            | Dr. David Lee          |
| **Gynecologist**                  | Focuses on women’s reproductive health and childbirth (often OB/GYN).          | Dr. Rachel Gupta       |
| **Endocrinologist**               | Treats hormonal and metabolic disorders, like diabetes or thyroid issues.      | Dr. Thomas Brown       |
| **Gastroenterologist**            | Specializes in digestive system disorders, such as IBS or liver disease.       | Dr. Maria Gonzalez     |
| **Ophthalmologist**               | Diagnoses and treats eye conditions, including surgeries like LASIK.           | Dr. Steven Clark       |
| **Anesthesiologist**              | Administers anesthesia and monitors patients during surgery.                   | Dr. Olivia Smith       |
| **Pulmonologist**                 | Treats respiratory system conditions, like asthma or COPD.                     | Dr. Henry Davis        |
| **Urologist**                     | Focuses on urinary tract and male reproductive system disorders. 

'''
                     
                     ).send()

@cl.action_callback("Medical Advice")
async def on_medical_advice(action):
    cl.user_session.set("step", "medical_advice")
    await cl.Message(content="Please describe your symptoms or medical concerns.").send()

@cl.on_message
async def handle_msg(msg: cl.Message):
    elements = msg.elements
    files = [file for file in msg.elements if hasattr(file, "path")]
    history = cl.user_session.get("history")
    history.append({
        "role": "user",
        "content": msg.content,
    })

    # elements = msg.elements
    # files = [file for file in msg.elements if hasattr(file, "path")]
    msg = cl.Message(content="")


    def format_history(history):
        formatted = []
        for entry in history:
            role = entry["role"].title()
            content = entry["content"]
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    

    if cl.user_session.get("step") == "upload":
        if not elements:
            await msg.stream_token("Please upload a medical report file (PDF/Image) to analyze.")
            return
        
        print(f"files: {files}")  # Add this line
        result = Runner.run_streamed(MediAssist,hooks=hooks, input=f'''Please analyze the medical report at {files[0].path} here is the old chat context {format_history(history)}''')
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response = event.data.delta
                if isinstance(response, str):
                    await msg.stream_token(response)
                elif isinstance(response, dict) and "content" in response:
                    await msg.stream_token(response["content"])
                else:
                    print(f"Unexpected response format: {response}")
            
            elif event.type == "final_response":
                if hasattr(event.data, "content") and isinstance(event.data.content, str):
                    await msg.stream_token(event.data.content)
                elif isinstance(event.data, dict) and "content" in event.data:
                    await msg.stream_token(event.data["content"])
                else:
                    print(f"Unexpected final response format: {event.data}")
        history.append({
            "role": "medical_assistant",
            "content": msg.content
        })
        cl.user_session.set("history", history)
        await msg.update()
        return
    if cl.user_session.get("step") == "medical_advice":
        if not files:
            details = msg.content
            result = Runner.run_streamed(MediAssist,input=f"Please provide medical advice based on the following symptoms: {details}. Here is the old chat context {format_history(history)}") 
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    response = event.data.delta
                    if isinstance(response, str):
                        await msg.stream_token(response)
                    elif isinstance(response, dict) and "content" in response:
                        await msg.stream_token(response["content"])
                    else:
                        print(f"Unexpected response format: {response}")
                
                elif event.type == "final_response":
                    if hasattr(event.data, "content") and isinstance(event.data.content, str):
                        await msg.stream_token(event.data.content)
                    elif isinstance(event.data, dict) and "content" in event.data:
                        await msg.stream_token(event.data["content"])
                    else:
                        print(f"Unexpected final response format: {event.data}")
            history.append({
                "role": "medical_assistant",
                "content": msg.content
            })
            cl.user_session.set("history", history)
            await msg.update()
        else:
            await cl.Message(content=f"Please provide symptoms or health issues for report queiries use analyze medical reports option above").send()
            return
    if cl.user_session.get("step") == "book_appointment":
        if not files:
            details = msg.content
            result =  Runner.run_streamed(MediAssist,input=f"Please book appointment for the {details} details provided. Ask for the user for any missing details. Here is the old chat context {format_history(history)}") 
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    response = event.data.delta
                    if isinstance(response, str):
                        await msg.stream_token(response)
                    elif isinstance(response, dict) and "content" in response:
                        await msg.stream_token(response["content"])
                    else:
                        print(f"Unexpected response format: {response}")
                
                elif event.type == "final_response":
                    if hasattr(event.data, "content") and isinstance(event.data.content, str):
                        await msg.stream_token(event.data.content)
                    elif isinstance(event.data, dict) and "content" in event.data:
                        await msg.stream_token(event.data["content"])
                    else:
                        print(f"Unexpected final response format: {event.data}")
            history.append({
                "role": "medical_assistant",
                "content": msg.content
            })
            cl.user_session.set("history", history)
            await msg.update()
        else:
            await cl.Message(content=f"Please provide appointment details without any files. If you want to check reports use Analyze medical reports option above").send()
        return
    #general chat
    if not files:
        result = Runner.run_streamed(MediAssist,input=format_history(history)) 
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response = event.data.delta
                if isinstance(response, str):
                    await msg.stream_token(response)
                elif isinstance(response, dict) and "content" in response:
                    await msg.stream_token(response["content"])
                else:
                    print(f"Unexpected response format: {response}")
            
            elif event.type == "final_response":
                if hasattr(event.data, "content") and isinstance(event.data.content, str):
                    await msg.stream_token(event.data.content)
                elif isinstance(event.data, dict) and "content" in event.data:
                    await msg.stream_token(event.data["content"])
                else:
                    print(f"Unexpected final response format: {event.data}")
        history.append({
            "role": "medical_assistant",
            "content": msg.content
        })
        cl.user_session.set("history", history)
        await msg.update()
    else:
        await cl.Message(content=f"Please provide text input without any files. If you want to check reports use Analyze medical reports option above").send()
        return
    


