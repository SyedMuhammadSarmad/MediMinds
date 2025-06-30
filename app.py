import chainlit as cl

@cl.on_chat_start
async def start():
    
    cl.user_session.set("role", "doctor")
    cl.user_session.set("step", "main")

    
    await cl.Message(
        content=


"""
# 🩺 AI Medical Assistant

Welcome! How can I help you today?

Please choose an option below:

- 📄 `Analyze Medical Report`
- 🧠 `Symptom Checker`  
- 📋 `View Patient Summary ` 
- 🛡️ `Do's & Don'ts Recommendations`  
- 📊 `View Test Trends`

"""
    ,
        actions=[
            cl.Action(name="AnalyzeReport", label="Analyze Medical Report" , payload={"action": "analyze_report"}),
            cl.Action(name="SymptomChecker", label="Symptom Checker", payload={"action": "symptom_checker"}),
            cl.Action(name="PatientSummary", label="View Patient Summary", payload={"action": "patient_summary"}),
            cl.Action(name="DosDonts", label="Do's & Don'ts Recommendations", payload={"action": "dos_donts"}),
            cl.Action(name="TestTrends", label="View Test Trends", payload={"action": "test_trends"})
        ]
    ).send()

@cl.action_callback("AnalyzeReport")
async def on_analyze_report(action):
    cl.user_session.set("step", "upload")
    await cl.Message(content="Please upload the medical report file (PDF/Image).").send()

@cl.action_callback("SymptomChecker")
async def on_symptom_checker(action):
    cl.user_session.set("step", "symptom")
    await cl.Message(content="Please enter symptoms (comma separated):").send()

@cl.action_callback("PatientSummary")
async def on_patient_summary(action):
    await cl.Message(content="Here's the summary of patient's past visits and conditions.").send()

@cl.action_callback("DosDonts")
async def on_dos_donts(action):
    await cl.Message(content="Based on the diagnosis, here are the Do's and Don'ts for the patient:").send()

@cl.action_callback("TestTrends")
async def on_test_trends(action):
    await cl.Message(content="Visualizing trends from lab results over time.").send()

@cl.on_message
async def handle_msg(msg: cl.Message):
    step = cl.user_session.get("step")

    if step == "symptom":
        symptoms = msg.content
        await cl.Message(content=f"Checking conditions for symptoms: {symptoms}").send()
        #backend 

    elif step == "upload":
        await cl.Message(content="Report is being analyzed... (Upload handling to be added)").send()
        # report parser 

    else:
        await cl.Message(content="Please choose one of the options above to get started.").send()