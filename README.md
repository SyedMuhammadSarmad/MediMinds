
# 🩺 MediMinds - Your AI-Powered Medical Assistant
MediMinds is an intelligent, AI-powered virtual assistant for managing and understanding medical records. It can extract information from prescriptions, interpret patient reports, store appointment and patient data, and respond to natural language queries using advanced language models.

## 🚀 Features
- 📄 **OCR + PDF Extraction**: Upload medical documents, and MediMinds reads them using `pdfplumber` and `pytesseract`.
- 🧠 **LLM-Powered Agent**: Ask questions like “What medicines are prescribed?” or “Explain this report” and get smart answers.
- 🗃 **PostgreSQL + SQLAlchemy ORM**: Store patients and appointments securely and accessibly.
- 🌐 **Chainlit UI**: Interact with MediMinds via a clean, conversational web interface.
- ☁️ **CockroachDB Support**: Easily scalable and cloud-ready database layer.


## 🏗️ Tech Stack
| Layer        | Tools Used                                          |
| ------------ | --------------------------------------------------- |
| Frontend     | Chainlit                                            |
| Backend      | Python, OpenAI                                      |
| Data Storage | SQLAlchemy ORM, PostgreSQL (CockroachDB)            |
| AI / NLP     | OpenAI, PDFPlumber, Pytesseract                     |
| Deployment   | Vultr                                               |

## 🖼️ Demo

### 🧪  Try the app at:  [MediMinds](http://140.82.12.120:8000/)

Or set it up locally ⬇️


## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/MediMinds.git
cd MediMinds
````

### 2. Set Up a Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Set Up Environment Variables

Create a `.env` file with:

```env
my_DATABASE_URL=your_postgres_cockroachdb_url
grok_cloud_api=your_grok_api_key
include a `.cert/root.crt` file 
```

### 5. Run the App

```bash
uv run chainlit run app.py 
```

Your app will be available at:
`http://localhost:8000` or `http://<your-server-ip>:8000`

---

## 🧩 Project Structure

```
MediMinds/
│
├── app.py               # Entry point with Chainlit
├── agent.py             # LLM-powered agent
├── ORM.py               # SQLAlchemy ORM models
├── db.py                # DB connection setup
├── .env                 # Environment variables
├── .cert/               # Root certificate for CockroachDB
├── pyproject.toml       # Project and dependency config
├── chainlit.toml        # Chainlit config
├── README.md
```

---

## 📚 Use Cases

* Extracting medicine names from prescriptions and anayzing medical reports
* Booking patient appointment 
* Real-time interaction for patients  

---

## 👥 Team MediMinds

* Syed Muhammad Sarmad
* Muhammad Hammad Farooqui
* Built as part of a AI hackathon arrange by lablab.ai : [Raise your Hack](https://lablab.ai/event/raise-your-hack)

---

## 📌 Future Improvements

* Integration with EHR systems
* User authentication
* Voice assistant features
* Multi-language support

