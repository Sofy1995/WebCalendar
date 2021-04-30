from flask import Flask, abort
import sys
import datetime
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()

parser = reqparse.RequestParser()
other_parser = reqparse.RequestParser()
parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)

other_parser.add_argument(
    'start_time',
    type=inputs.date,
    required=False
)

other_parser.add_argument(
    'end_time',
    type=inputs.date,
    required=False
)

class MakeDict(object):
    def __init__(self, id, event, date):
        self.id = id
        self.event = event
        self.date = date

    def give_dict(self):
        return {'id': self.id, 'event': self.event, 'date': str(self.date)}


class TodayEvents(Resource):
    def get(self):
        all_events = list()
        for item in Event.query.filter(Event.date == datetime.date.today()).all():
            ev = MakeDict(item.id, item.event, item.date)
            all_events.append(ev.give_dict())
        return all_events


class AddEvent(Resource):
    def post(self):
        args = parser.parse_args()
        if args['event'] and args['date']:
            event = Event(event=args['event'], date=args['date'])
            db.session.add(event)
            db.session.commit()

        return {
                "message": "The event has been added!",
                "event": args['event'],
                "date": str(args["date"].date())
                }

    def get(self):
        args = other_parser.parse_args()
        if args['start_time'] and args['end_time']:
            question = Event.query.filter(Event.date >= args['start_time'].date(), Event.date <= args['end_time'].date()).all()
            # question = Event.query.all()
        else:
            question = Event.query.all()
        all_events = list()
        for item in question:
            ev = MakeDict(item.id, item.event, item.date)
            all_events.append(ev.give_dict())
        return all_events


class EventByID(Resource):

    def get(self, id):
        event = Event.query.filter(Event.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        ev = MakeDict(event.id, event.event, event.date)
        return ev.give_dict()

    def delete(self, id):
        event = Event.query.filter(Event.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {"message": "The event has been deleted!"}



api.add_resource(TodayEvents, '/event/today')
api.add_resource(AddEvent, '/event')
api.add_resource(EventByID, '/event/<int:id>')






# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
