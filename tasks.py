from reminders import celery, db, app
from models.appointment import Client as c
from sqlalchemy.orm.exc import NoResultFound
from twilio.rest import Client
import arrow
from twilio.twiml.messaging_response import MessagingResponse

twilio_account_sid = app.flask_app.config['TWILIO_ACCOUNT_SID']
twilio_auth_token = app.flask_app.config['TWILIO_AUTH_TOKEN']
twilio_number = app.flask_app.config['TWILIO_NUMBER']

twilio_client = Client(twilio_account_sid, twilio_auth_token)


def response_handler(client_number, body):
    client = db.session.query(
        c).filter_by(phone_number=client_number).first()

    yes_message = "Okay, we'll follow up in 1 week! In the meantime, please feel free to contact us by phone or email" \
                  " (617-497-5690 or masmallclaims@gmail.com) with any questions or updates."

    no_message = "No problem! In order to help us improve our services, we would appreciate your response to this " \
                 "survey: https://forms.gle/yvBnmuomKigivxnW7. If you do need additional help, please contact us by " \
                 "phone or email (617-497-5690 or masmallclaims@gmail.com)."

    other_message = "Please respond with yes or no."

    followup_message = "Thank you for your response. Please contact us by phone or email to provide us an update on " \
                       "the status of your case, and a volunteer will be in touch shortly to provide help. "

    survey_message = "In order to help us improve our services, we would appreciate your response to this survey: " \
                     "https://forms.gle/yvBnmuomKigivxnW7. If you do need additional help, please contact us by " \
                     "phone or email (617-497-5690 or masmallclaims@gmail.com)."

    resp = MessagingResponse()

    if body and (body.lower() == 'y' or body.lower() == 'yes'):
        if client.initial_contact:
            resp.message(yes_message)
            client.initial_contact = False
        else:
            resp.message(followup_message)
        client.survey = False
        db.session.flush()
        db.session.commit()
        # todo: delta should be 2 weeks from now

    elif body and (body.lower() == 'n' or body.lower() == 'no'):
        if client.initial_contact:
            resp.message(no_message)
            client.initial_contact = False
        else:
            resp.message(survey_message)
        client.survey = True
        db.session.flush()
        db.session.commit()

    else:
        resp.message(other_message)
        # todo: only do this twice, then ask them to call (put in spanish and english)

    return str(resp)


@celery.task()
def send_sms_followup(client_id):
    try:
        client = db.session.query(
            c).filter_by(id=client_id).one()
    except NoResultFound:
        return

    # for now assume everyone is Eastern time
    # time = arrow.get(client.time).to(client.timezone)
    if client.survey:
        body = "Hello {0}. This is the Massachusetts Small Claims Advisory Service. In order to help us improve our " \
               "services, we would appreciate your response to this survey: https://forms.gle/yvBnmuomKigivxnW7. If " \
               "need any additional help, please contact us by phone or email (617-497-5690 or " \
               "masmallclaims@gmail.com).".format(client.name)
    else:
        body = "Hello {0}. This is the Massachusetts Small Claims Advisory Service. We are checking in on your case. " \
               "Do you still need information about the case? (Y/N)".format(client.name)

    to = client.phone_number,
    twilio_client.messages.create(
        to,
        from_=twilio_number,
        body=body)


def send_initial_sms(client_id):
    try:
        curr_client = db.session.query(
            c).filter_by(id=client_id).one()
    except NoResultFound:
        return

    body = ("Hello {0}. Thank you for reaching out to SCAS!"
            " We are happy to provide further help with your case."
            " Would you like us to follow up in a week? (Y/N)").format(
        curr_client.name
    )

    to = curr_client.phone_number,
    twilio_client.messages.create(
        to,
        from_=twilio_number,
        body=body)
