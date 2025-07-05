import chainlit as cl
from pathlib import Path
from agent import MediAssist
from agents import Runner
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
async def on_analyze_report(action):
    cl.user_session.set("step", "book_appointment")
    await cl.Message(content=
                     '''
Please provide the following details to book an appointment:
- **Name**: Full name of the patient    
- **Age**: Age of the patient
- **Date**: Date of the appointment
- **Time**: Time of the appointment 
- **Reason**: Reason for the appointment
- **Doctor**: Name of the doctor (optional, can be left blank)
- **Status**: Status of the appointment (default is "scheduled")

'''
                     
                     ).send()

@cl.action_callback("Medical Advice")
async def on_medical_advice(action):
    cl.user_session.set("step", "medical_advice")
    await cl.Message(content="Please describe your symptoms or medical concerns.").send()

@cl.on_message
async def handle_msg(msg: cl.Message):
    history = cl.user_session.get("history")
    history.append({
        "role": "user",
        "content": msg.content
    })

    def format_history(history):
        formatted = []
        for entry in history:
            role = entry["role"].title()
            content = entry["content"]
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    files = [el for el in msg.elements if hasattr(el, "path")]

    if cl.user_session.get("step") == "upload":
        if files:
            file = files[0]
            agent_res = await Runner.run(MediAssist, input=f"Please analyze the medical report at {file.path} here is the old chat context {format_history(history)}")
            await cl.Message(agent_res.final_output).send()
            return
    if cl.user_session.get("step") == "medical_advice":
        if not files:
            details = msg.content
            result = await Runner.run(MediAssist, input=f"Please provide medical advice based on the following symptoms: {details}. Here is the old chat context {format_history(history)}") 
            await cl.Message(content=f"{result.final_output}").send()
        else:
            await cl.Message(content=f"Please provide symptoms or health issues for report queiries use analyze medical reports option above").send()
            return
    if cl.user_session.get("step") == "book_appointment":
        if not files:
            details = msg.content
            result = await Runner.run(MediAssist,input=f"Please book appointment for the {details}. Ask for the user for any missing details. Here is the old chat context {format_history(history)}") 
            await cl.Message(content=f"{result.final_output}").send()
        else:
            await cl.Message(content=f"Please provide appointment details without any files. If you want to check reports use Analyze medical reports option above").send()
        return
    #general chat
    result = await Runner.run(MediAssist,input=format_history(history)) 
    await cl.Message(content=result.final_output).send()
    


