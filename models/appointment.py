from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean
import arrow

Base = declarative_base()


# class Appointment(Base):
#     __tablename__ = 'appointments'

#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     phone_number = Column(String(50), nullable=False)
#     delta = Column(Integer, nullable=False)
#     time = Column(DateTime, nullable=False)
#     timezone = Column(String(50), nullable=False)

#     def __init__(self, name, phone_number, delta, time, timezone):
#         self.name = name
#         self.phone_number = phone_number
#         self.delta = delta
#         self.time = time
#         self.timezone = timezone

#     def __repr__(self):
#         return '<Appointment %r>' % self.name

#     def get_notification_time(self):
#         appointment_time = arrow.get(self.time)
#         reminder_time = appointment_time.replace(minutes=-self.delta)
#         return reminder_time


class Client(Base):
    """A class used to represent clients for follow-ups"""

    __tablename__ = 'clients'

    #TODO: verify that 50 chars is enough for strings
    id = Column(Integer, primary_key=True)

    #TODO: foreign key?
    client_id = Column(Integer, unique= True, nullable=False)
    name = Column(String(50))
    phone_number = Column(String(50))
    delta = Column(Integer)
    survey = Column(Boolean)
    time = Column(DateTime, nullable=False)
    timezone = Column(String(50), nullable=False)

    def __init__(self, client_id, name, phone_number, delta, survey, time, timezone):
        self.client_id = client_id
        self.name = name
        self.phone_number = phone_number
        self.delta = delta
        self.survey = survey
        self.time = time
        self.timezone = timezone

    def __repr__(self):
        return '<Client ID: %r>' % self.client_id   

    # def get_id_from_number(self, number):
    

    def get_followup_time(self):
        """Uses arrow to get the follow-up time to send the text"""

        contact_time = arrow.get(self.time)
        reminder_time = contact_time.replace(minutes=+self.delta)
        return reminder_time 

