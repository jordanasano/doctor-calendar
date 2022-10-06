from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Example user model
class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    first_name = db.Column(
        db.String(40),
        nullable=False
    )
    last_name = db.Column(
        db.String(40),
        nullable=False
    )
    # doctor.appointments get's a list of appointments for the doctor
    # connected by foreign key of doctor_id in Appointment model
    appointments = db.relationship('Appointment', 
        backref='doctor')
    
    # Needed to return as JSON, can't return obj in viewer funcs, needs to be dict
    def serialize(self):
        id = self.id
        first_name = self.first_name
        last_name = self.last_name

        return {
            "id":id,
            "first_name":first_name,
            "last_name":last_name
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    patient_first_name = db.Column(
        db.String(40),
        nullable=False
    )
    patient_last_name = db.Column(
        db.String(40),
        nullable=False
    )
    date = db.Column(
        db.String(10),
        nullable=False
    )
    time = db.Column(
        db.String(7),
        nullable=False
    )
    kind = db.Column(
        db.String(20),
        nullable=False
    )
    # Connects to Doctor model using doctor.id
    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey('doctors.id')
    )

    # Needed to return as JSON, can't return obj in viewer funcs, needs to be dict
    def serialize(self):
        id = self.id
        patient_first_name = self.patient_first_name
        patient_last_name = self.patient_last_name
        date = self.date
        time = self.time
        kind = self.kind
        doctor_id = self.doctor_id

        return {
            "id":id,
            "patient_first_name":patient_first_name,
            "patient_last_name":patient_last_name,
            "date":date,
            "time":time,
            "kind":kind,
            "doctor_id":doctor_id
        }

def connect_db(app):
    """ Connects to database """
    db.app = app
    return db.init_app(app)