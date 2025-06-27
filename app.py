import chainlit as cl

@cl.on_chat_start
def start():
    cl.user_session.set("step", "main")
   # cl.chat_settings.set({"role": "doctor"})

    cl.send_message(
        content="""
        # 🧠 AI Medical Assistant

        Welcome! How can I help you today?
        
        Please choose an option below:
        
        - 📄 Analyze Medical Report
        - 🩺 Symptom Checker
        - 📋 View Patient Summary
        - 🛡️ Do's & Don'ts Recommendations
        - 📊 View Test Trends
        """,
        buttons=[
            cl.Button(name="Analyze Report", value="analyze_report"),
            cl.Button(name="Symptom Checker", value="symptom_checker"),
            cl.Button(name="Patient Summary", value="patient_summary"),
            cl.Button(name="Do's & Don'ts", value="dos_donts"),
            cl.Button(name="Test Trends", value="test_trends")
        ]
    )

@cl.on_message
def handle_msg(msg: cl.Message):
    step = cl.user_session.get("step")

    if msg.content == "analyze_report":
        cl.user_session.set("step", "upload")
        cl.send_message("Please upload the medical report file (PDF/Image).")

    elif msg.content == "symptom_checker":
        cl.user_session.set("step", "symptom")
        cl.send_message("Please enter symptoms (comma separated):")

    elif msg.content == "patient_summary":
        cl.send_message("Here's the summary of patient's past visits and conditions.")

    elif msg.content == "dos_donts":
        cl.send_message("Based on the diagnosis, here are the Do's and Don'ts for the patient:")

    elif msg.content == "test_trends":
        cl.send_message("Visualizing trends from lab results over time.")

    elif step == "symptom":
        symptoms = msg.content
        cl.send_message(f"Checking conditions for symptoms: {symptoms}")
        # Optionally call your backend model here

    elif step == "upload":
        cl.send_message("Report is being analyzed... (Upload handling to be added)")
        # Optionally call your report parser backend here

    else:
        cl.send_message("Please choose one of the options above to get started.")
