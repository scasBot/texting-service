from flask.views import MethodView, View
from flask import render_template, request
from models.appointment import Client
from forms.new_appointment import NewAppointmentForm
from twilio.twiml.messaging_response import MessagingResponse
from flask import request, redirect, url_for
import reminders
import arrow



class AppointmentResourceDelete(MethodView):

    def post(self, id):
        appt = reminders.db.session.query(Client).filter_by(id=id).one()
        reminders.db.session.delete(appt)
        reminders.db.session.flush()
        reminders.db.session.commit()

        return redirect(url_for('appointment.index'), code=303)


class AppointmentResourceCreate(MethodView):

    def post(self):
        form = NewAppointmentForm(request.form)

        if form.validate():
            from tasks import send_sms_followup

            # appt = Appointment(
            #     name=form.data['name'],
            #     phone_number=form.data['phone_number'],
            #     delta=form.data['delta'],
            #     time=form.data['time'],
            #     timezone=form.data['timezone']
            # )

            client = Client(
                client_id = form.data['client_id'],
                name=form.data['name'],
                phone_number=form.data['phone_number'],
                delta=form.data['delta'],
                survey = form.data['survey'],
                time=form.data['time'],
                timezone=form.data['timezone']
            )

            # appt.time = arrow.get(appt.time, appt.timezone).to('utc').naive

            # for attr in dir(client):
            #     if hasattr( client, attr ):
            #         print( "client.%s = %s" % (attr, getattr(client, attr)))

            # print(client.clientId)

            reminders.db.session.add(client)
            reminders.db.session.flush()
            reminders.db.session.commit()
            # send_sms_reminder.apply_async(
            #     args=[appt.id], eta=appt.get_notification_time())

            send_sms_followup(client.id)
            return redirect(url_for('appointment.index'), code=303)
        else:
            return render_template('appointments/new.html', form=form), 400


class AppointmentResourceIndex(MethodView):

    def get(self):
        all_clients = reminders.db.session.query(Client).all()
        return render_template('appointments/index.html',
                               clients=all_clients)


class AppointmentFormResource(MethodView):

    def get(self):
        form = NewAppointmentForm()
        return render_template('appointments/new.html', form=form)

class ResponseResource(View):
    
    methods = ['GET', 'POST']

    ''' Dynamically respond to incoming messages based on state of client '''
    def dispatch_request(self):
        body = request.values.get('Body', None)
        from_number = request.values.get('From')

        yes_message = "Okay, we'll follow up in 1 week! In the meantime, please feel free to contact us by phone or email (617-497-5690/masmallclaims@gmail.com) with any questions or updates."
        no_message = "send survey, thanks"
        other_message = "please respond with Y/N"

        resp = MessagingResponse()

        if body and (body.lower()=='y' or body.lower()=='yes'):
            resp.message(yes_message)
            # set survey to no

        elif body and (body.lower()=='n' or body.lower()=='no'):
            resp.message(no_message)
            # set survey to yes and in future call method to administer survey

        else:
            resp.message(other_message)
            # only do this twice, then ask them to call (put in spanish and englishN)

        return str(resp)