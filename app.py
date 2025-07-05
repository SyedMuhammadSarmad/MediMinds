import chainlit as cl
from pathlib import Path
from agent import MediAssist
from agents import Runner
@cl.on_chat_start
async def start():
    
    cl.user_session.set("role", "doctor")
    cl.user_session.set("step", "main")

    
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


# @cl.action_callback("SymptomChecker")
# async def on_symptom_checker(action):
#     cl.user_session.set("step", "symptom")
#     await cl.Message(content="Please enter symptoms (comma separated):").send()

# @cl.action_callback("PatientSummary")
# async def on_patient_summary(action):
#     await cl.Message(content="Here's the summary of patient's past visits and conditions.").send()

# @cl.action_callback("DosDonts")
# async def on_dos_donts(action):
#     await cl.Message(content="Based on the diagnosis, here are the Do's and Don'ts for the patient:").send()

# @cl.action_callback("TestTrends")
# async def on_test_trends(action):
#     await cl.Message(content="Visualizing trends from lab results over time.").send()

@cl.on_message
async def handle_msg(msg: cl.Message):
    files = [el for el in msg.elements if hasattr(el, "path")]
    if files:
        file = files[0]
        agent_res = await Runner.run(MediAssist, input=f"Please analyze the medical report at {file.path}")
        await cl.Message(agent_res.final_output).send()
        return
    
    user_text = msg.content
    result = await Runner.run(MediAssist,input=user_text) 
    # print(result.final_output)
    await cl.Message(content=result.final_output).send()
    
    # step = cl.user_session.get("step")

    # if step == "symptom":
    #     symptoms = msg.content
    #     symptoms_result = await Runner.run(MediAssist,input=f"Please check the conditions for the following symptoms: {symptoms}" ) 
    #     await cl.Message(content=symptoms_result.final_output).send()

    # elif step == "upload":
    #     await cl.Message(content="Report is being analyzed... (Upload handling to be added)").send()
        # report parser 

    # else:
    #     await cl.Message(content="Please choose one of the options above to get started.").send()