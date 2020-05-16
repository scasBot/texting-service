from flask.views import MethodView, View
from flask import render_template, request
from models.appointment import Client
from forms.new_appointment import NewClientForm
from flask import request, redirect, url_for
import reminders
import arrow


class ClientResourceDelete(MethodView):

    def post(self, id):
        appt = reminders.db.session.query(Client).filter_by(id=id).one()
        reminders.db.session.delete(appt)
        reminders.db.session.flush()
        reminders.db.session.commit()

        return redirect(url_for('client.index'), code=303)


class ClientResourceCreate(MethodView):

    def post(self):
        form = NewClientForm(request.form)

        if form.validate():
            from tasks import send_initial_sms, send_sms_followup

            client = Client(
                client_id=form.data['client_id'],
                name=form.data['name'],
                phone_number=form.data['phone_number'],
                delta=form.data['delta'],
                survey=form.data['survey'],
                initial_contact=True,
                time=form.data['time'],
                timezone=form.data['timezone']
            )

            client.time = arrow.get(client.time, client.timezone).to('utc').naive

            reminders.db.session.add(client)
            reminders.db.session.flush()
            reminders.db.session.commit()

            send_initial_sms(client.id)

            send_sms_followup.apply_async(
                args=[client.id], eta=client.get_followup_time())

            return redirect(url_for('client.index'), code=303)
        else:
            return render_template('clients/new.html', form=form), 400


class ClientResourceIndex(MethodView):

    def get(self):
        all_clients = reminders.db.session.query(Client).all()
        return render_template('clients/index.html',
                               clients=all_clients)


class ClientFormResource(MethodView):

    def get(self):
        form = NewClientForm()
        return render_template('clients/new.html', form=form)


class ResponseResource(View):
    methods = ['GET', 'POST']

    ''' Dynamically respond to incoming messages based on state of client '''

    def dispatch_request(self):
        from tasks import response_handler
        # todo: store country code in database
        # trim the country code from the string
        from_number = request.values.get('From')[2:]
        body = request.values.get('Body', None)
        return response_handler(from_number, body)
