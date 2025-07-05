from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine,Date, Time
from sqlalchemy.orm import sessionmaker
import os 

from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    reports = relationship("MedicalReport", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
class MedicalReport(Base):
    __tablename__ = 'medical_reports'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    content = Column(Text)
    patient = relationship("Patient", back_populates="reports")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    date = Column(Date)
    time = Column(Time)
    reason = Column(String)
    doctor_name = Column(String)
    notes = Column(Text)
    status = Column(String, default="scheduled")
    patient = relationship("Patient", back_populates="appointments")


db_uri = os.environ['my_DATABASE_URL'].replace("postgresql://", "cockroachdb://")

here = os.path.dirname(__file__)
cert_path = os.path.join(here, ".cert", "root.crt")
engine = create_engine(

    db_uri, 
    
    connect_args={
    "sslmode": "verify-full",
    "sslrootcert": cert_path,
    "application_name": "mediminds",
}

)
try:
    Base.metadata.create_all(engine)
    # print("Database connected")
except Exception as e:
    print("Failed to connect to database.")
    print(f"{e}")

Session = sessionmaker(bind=engine)


