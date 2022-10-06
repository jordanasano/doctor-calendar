from flask import Flask, request, redirect, jsonify
from models import connect_db, Doctor, db,  Appointment

app = Flask(__name__)

# Database URI needs to be changed to the name of your database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///doctor-calendar' # Here
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"

connect_db(app)
db.create_all()

############################# Doctors routes ###################################
@app.get('/')
def redirect_to_doctors():
    """Redirects to the doctors endpoint. Gives status code of 302."""

    return redirect('/doctors')

@app.get('/doctors')
def list_doctors():
    """Get's a list of all doctors and returns as JSON like:
        {"doctors": [{
            id,
            first_name,
            last_name
            }], ....
        }
    """

    doctors = Doctor.query.all()
    # Need to serialize to normal dict instead of obj if returning as JSON
    doctors = [doctor.serialize() for doctor in doctors]

    return jsonify(doctors)

@app.get('/doctors/<int:id>')
def list_doctor(id):
    """ Takes doctor's id in the pathway. gets doctor.
        If successful, returns JSON of {"doctor":{id,first_name,last_name}}
        If unsuccessful, returns a 404 status code and error message
    """

    doctor = Doctor.query.get_or_404(id)

    return jsonify({"doctor":doctor.serialize()})

@app.post('/doctors')
def create_doctor():
    """ Takes first_name and last_name sent in body of request.
        Creates a new doctor. Returns JSON of {"posted_doctor":{id,first_name,last_name}}
        with status code of 201.
    """
    print("request =",request.json)
    first_name = request.json['first_name']
    last_name = request.json['last_name']

    doctor = Doctor(
        first_name=first_name,
        last_name=last_name
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({"posted_doctor":doctor.serialize()}), 201

############################# Appointments routes ##############################
@app.get('/appointments')
def list_appointments():
    """Get's a list of all appointments and returns as JSON like:
        {"appointments": [{
            id,
            patient_first_name,
            patient_last_name,
            date_and_time,
            kind,
            doctor_id
            }], ....
        }
    """

    appointments = Appointment.query.all()
    # Need to serialize to normal dict instead of obj if returning as JSON
    appointments = [appointment.serialize() for appointment in appointments]

    return jsonify(appointments)

@app.get('/appointments/<int:doctor_id>/<month>/<day>/<year>')
def list_appointments_for_doctor_on_day(doctor_id, month, day, year):
    """ Takes doctor's id, month, day, and year in pathway.
        If successful, returns JSON of {"appointments": [{
            id,
            patient_first_name,
            patient_last_name,
            date,
            time,
            kind,
            doctor_id
            }], ....
        }
        If unsuccessful, returns a 404 status code and error message
    """
    date = f"{month}/{day}/{year}"
    print("*********************************************************************************** date =",date)
    doctor = Doctor.query.get_or_404(doctor_id)
    appointments = [appointment for appointment in doctor.appointments if appointment.date == date]

    return jsonify({"appointments":[appointment.serialize() for appointment in appointments]})

@app.post('/appointments/<int:doctor_id>')
def create_appointment(doctor_id):
    """ Takes in pathway:
            doctor_id
        Takens in body of request:
            patient_first_name,
            patient_last_name,
            date_and_time,
            kind
        If doctor exists and has openings, returns JSON like:
            {"posted_appointment": {
                id,
                patient_first_name,
                patient_last_name,
                date,
                time,
                kind,
                doctor_id 
            }}
        
        If doctor doesn't exist, returns 404 with an error message.
        If doctor has no openings or the time is not a 15 min interval or kind is invalid, 
        return 401 with an error message.
    """
    doctor = Doctor.query.get_or_404(doctor_id)

    patient_first_name = request.json['patient_first_name']
    patient_last_name = request.json['patient_last_name']
    date = request.json['date']
    time = request.json['time']
    kind = request.json['kind']

    if date[0] == '0':
        date = date[1:]

    if time[0] == '0' and time[1] != ':':
        time = time[1:]
        print("************************** time=",time)

    if kind != "New Patient" and kind != "Follow-up":
        return jsonify({"error":"Invalid kind. Must be New Patient or Follow-up."}), 401

    minutes = int(''.join((time.split(':')[1])[0:2]))
    hours  = int(''.join((time.split(':')[0])))

    if hours > 12 or hours < 1:
        return jsonify({"error":"Invalid time. Please provide valid hour."}), 401

    if minutes % 15 != 0 or minutes >= 60 or minutes < 0:
        return jsonify({"error":"Invalid time. Please ensure minutes are a 15 min interval."}), 401
   
    
    def filter_appointments(appts):
        return [appt for appt in appts if appt.date == date and appt.time == time]

    appointments_on_date_and_time = filter_appointments(doctor.appointments)

    if len(appointments_on_date_and_time) >= 3:
        return jsonify({"error":f"Doctor already has 3 appointments on {date} at {time}. Choose another day please."}), 401

    appointment = Appointment(
        patient_first_name=patient_first_name,
        patient_last_name=patient_last_name,
        date=date,
        time=time,
        kind=kind,
        doctor_id=doctor_id
    )

    doctor.appointments.append(appointment)
    db.session.commit()

    return jsonify({"posted_appointment":appointment.serialize()}), 201

@app.delete('/appointments/<int:id>')
def delete_appointment(id):
    """ Takes appointment's id in the pathway. Deletes appointment.
        If successful, returns JSON of {"deleted":id}
        If unsuccessful, returns a 404 status code and error message
    """

    appointment = Appointment.query.get_or_404(id)

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"deleted":id})