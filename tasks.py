from reminders import celery, db, app
from models.appointment import Client as c
from sqlalchemy.orm.exc import NoResultFound
from twilio.rest import Client
import arrow

twilio_account_sid = app.flask_app.config['TWILIO_ACCOUNT_SID']
twilio_auth_token = app.flask_app.config['TWILIO_AUTH_TOKEN']
twilio_number = app.flask_app.config['TWILIO_NUMBER']

client = Client(twilio_account_sid, twilio_auth_token)


@celery.task()
def send_sms_reminder(appointment_id):
    try:
        appointment = db.session.query(
            Client).filter_by(id=appointment_id).one()
    except NoResultFound:
        return

    time = arrow.get(appointment.time).to(appointment.timezone)
    body = "Hello {0}. You have an appointment at {1}!".format(
        appointment.name,
        time.format('h:mm a')
    )

    to = appointment.phone_number,
    client.messages.create(
        to,
        from_=twilio_number,
        body=body)

def send_sms_followup(appointment_id):
    try:
        appointment = db.session.query(
            c).filter_by(id=appointment_id).one()
    except NoResultFound:
        return

    body = ("Hello {0}. Thank you for reaching out to SCAS!"
        " We are happy to provide further help with your case."
        " Would you like us to follow up in a week? (Y/N)").format(
        appointment.name
    )

    to = appointment.phone_number,
    client.messages.create(
        to,
        from_=twilio_number,
        body=body)