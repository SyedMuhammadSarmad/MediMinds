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
- 📋 `View Patient Summary ` 
- 🛡️ `Do's & Don'ts Recommendations`  
- 📅 `Book Appointment`
"""
    ,
        actions=[
            cl.Action(name="Analyze Report", label="Analyze Medical Report" , payload={"action": "analyze_report"}),
            cl.Action(name="Patient Summary", label="View Patient Summary", payload={"action": "patient_summary"}),
            cl.Action(name="Book Appointment", label="Book Appointment", payload={"action": "test_trends"})

        ]
    ).send()

@cl.action_callback("AnalyzeReport")
async def on_analyze_report(action):
    cl.user_session.set("step", "upload")
    await cl.Message(content="Please upload the medical report file (PDF/Image).").send()




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
    if files:
        file = files[0]
        agent_res = await Runner.run(MediAssist, input=f"Please analyze the medical report at {file.path} with context {format_history(history)}")
        await cl.Message(agent_res.final_output).send()
        return
    
    result = await Runner.run(MediAssist,input=format_history(history)) 
    await cl.Message(content=result.final_output).send()
    


