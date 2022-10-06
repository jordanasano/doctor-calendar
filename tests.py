from unittest import TestCase

from app import app, db
from models import Doctor, Appointment
from flask import json

# Database URI needs to be changed to the name of your test database
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///doctor-calendar-test" # Here

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.create_all()


class DoctorViewTestCase(TestCase):
    """Test views for doctors."""

    def setUp(self):
        """Create test client, add sample data."""

        Appointment.query.delete()
        Doctor.query.delete()

        self.client = app.test_client()

        test_doctor = Doctor(
            first_name="test_first",
            last_name="test_last"
        )

        second_doctor = Doctor(
            first_name="test_first_two", 
            last_name="test_last_two"
        )

        db.session.add_all([test_doctor, second_doctor])
        db.session.commit()

        self.doctor_id = test_doctor.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_redirect(self):
        with self.client as c:
            resp = c.get("/")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/doctors")

    def test_list_doctors(self):
        with self.client as c:
            resp = c.get("/doctors")

            self.assertEqual(resp.status_code, 200)

            doctorJSON = resp.get_data(as_text=True)
            doctor = json.loads(doctorJSON)

            self.assertIn({
                "first_name":"test_first",
                "last_name":"test_last", 
                "id":self.doctor_id
            }, doctor)
    
    def test_list_doctor(self):
        with self.client as c:
            resp = c.get(f"/doctors/{self.doctor_id}")

            self.assertEqual(resp.status_code, 200)

            doctorJSON = resp.get_data(as_text=True)
            doctor = json.loads(doctorJSON)

            self.assertEqual({
                "doctor": {
                "first_name":"test_first",
                "last_name":"test_last", 
                "id":self.doctor_id
                }
            }, doctor)
            
            resp2 = c.get("/doctors/1000000")

            self.assertEqual(resp2.status_code, 404)

    def test_create_doctor(self):
        with self.client as c:
            resp = c.post("/doctors", 
            json={
                "first_name":"new_first", 
                "last_name":"new_last"
            })

            self.assertEqual(resp.status_code, 201)

            responseJSON = resp.get_data(as_text=True)
            response = json.loads(responseJSON)

            self.assertIsInstance(response['posted_doctor']['id'], int)
            del response['posted_doctor']['id']

            self.assertEqual({
                "posted_doctor":{
                    "first_name":"new_first", 
                    "last_name":"new_last"
                    }
                }, response)

class AppointmentViewTestCase(TestCase):
    """Test views for appointments."""

    def setUp(self):
        """Create test client, add sample data."""

        Appointment.query.delete()
        Doctor.query.delete()

        self.client = app.test_client()

        test_doctor = Doctor(
            first_name="test_first",
            last_name="test_last"
        )

        second_doctor = Doctor(
            first_name="test_first_two", 
            last_name="test_last_two"
        )

        db.session.add_all([test_doctor, second_doctor])
        db.session.commit()

        test_appointment = Appointment(
            patient_first_name="test_fn",
            patient_last_name="test_ln",
            date="1/11/2000",
            time="8:00AM",
            kind="New Patient",
            doctor_id=test_doctor.id
        )

        second_test_appointment = Appointment(
            patient_first_name="test_fn_2",
            patient_last_name="test_ln_2",
            date="1/11/2000",
            time="8:00AM",
            kind="New Patient",
            doctor_id=test_doctor.id
        )

        third_test_appointment = Appointment(
            patient_first_name="test_fn_3",
            patient_last_name="test_ln_3",
            date="1/11/2000",
            time="8:00AM",
            kind="New Patient",
            doctor_id=second_doctor.id
        )

        db.session.add_all([test_appointment, second_test_appointment, third_test_appointment])
        db.session.commit()

        self.doctor_id = test_doctor.id
        self.second_doctor_id = second_doctor.id
        self.test_appointment_id = test_appointment.id
        self.second_test_appointment_id = second_test_appointment.id
        self.third_test_appointment_id = third_test_appointment.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_appointments(self):
        with self.client as c:
            resp = c.get("/appointments")

            self.assertEqual(resp.status_code, 200)

            appointmentsJSON = resp.get_data(as_text=True)
            appointments = json.loads(appointmentsJSON)

            self.assertIn({
                "patient_first_name":"test_fn",
                "patient_last_name":"test_ln",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.doctor_id,
                "id":self.test_appointment_id
            }, appointments)

            self.assertIn({
                "patient_first_name":"test_fn_2",
                "patient_last_name":"test_ln_2",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.doctor_id,
                "id":self.second_test_appointment_id
            }, appointments)

            self.assertIn({
                "patient_first_name":"test_fn_3",
                "patient_last_name":"test_ln_3",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.second_doctor_id,
                "id":self.third_test_appointment_id
            }, appointments)
    
    def test_list_appointments_for_doctor_on_day(self):
        with self.client as c:
            # Tests to make sure only appointments on day are received
            test_appointment = Appointment(
                patient_first_name="bad_test_fn",
                patient_last_name="bad_test_ln",
                date="1/12/2000",
                time="8:00AM",
                kind="New Patient",
                doctor_id=self.doctor_id
            )
            
            db.session.add(test_appointment)
            db.session.commit()

            resp = c.get(f"/appointments/{self.doctor_id}/1/11/2000")

            self.assertEqual(resp.status_code, 200)

            appointmentsJSON = resp.get_data(as_text=True)
            appointments = json.loads(appointmentsJSON)['appointments']

            self.assertIn({
                "patient_first_name":"test_fn",
                "patient_last_name":"test_ln",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.doctor_id,
                "id":self.test_appointment_id
            }, appointments)

            self.assertIn({
                "patient_first_name":"test_fn_2",
                "patient_last_name":"test_ln_2",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.doctor_id,
                "id":self.second_test_appointment_id
            }, appointments)

            self.assertNotIn({
                "patient_first_name":"test_fn_3",
                "patient_last_name":"test_ln_3",
                "date":"1/11/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.second_doctor_id,
                "id":self.third_test_appointment_id
            }, appointments)

            self.assertNotIn({
                "patient_first_name":"bad_test_fn",
                "patient_last_name":"bad_test_ln",
                "date":"1/12/2000",
                "time":"8:00AM",
                "kind":"New Patient",
                "doctor_id":self.doctor_id,
                "id":self.test_appointment_id
            }, appointments)

            # Tests for invalid doctor_id
            resp2 = c.get("/appointments/1000000/1/11/2000")

            self.assertEqual(resp2.status_code, 404)

    def test_create_appointment(self):
        with self.client as c:
            resp = c.post(f"/appointments/{self.doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"1/11/2000",
                    "time":"8:00AM",
                    "kind":"New Patient"
            })

            self.assertEqual(resp.status_code, 201)

            responseJSON = resp.get_data(as_text=True)
            response = json.loads(responseJSON)

            self.assertIsInstance(response['posted_appointment']['id'], int)
            del response['posted_appointment']['id']

            self.assertEqual({
                "posted_appointment":{
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"1/11/2000",
                    "time":"8:00AM",
                    "kind":"New Patient",
                    "doctor_id":self.doctor_id
                    }
                }, response)

            # Tests if doctor can have more than 3 appointments on a date, as long
            # as one time only has 3 appointments.
            resp2 = c.post(f"/appointments/{self.doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"1/11/2000",
                    "time":"10:00AM",
                    "kind":"New Patient"
            })

            self.assertEqual(resp2.status_code, 201)

            

    def test_create_appointment_bad_input(self):
        with self.client as c:
            # Test minutes higher than 59
            resp = c.post(f"/appointments/{self.second_doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"01/11/2999",
                    "time":"08:60AM",
                    "kind":"New Patient"
            })

            self.assertEqual(resp.status_code, 401)

            responseJSON = resp.get_data(as_text=True)
            response = json.loads(responseJSON)
            
            self.assertEqual({"error":"Invalid time. Please ensure minutes are a 15 min interval."}, response)

            # Tests minutes lower than 0
            resp2 = c.post(f"/appointments/{self.second_doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"01/11/2999",
                    "time":"08:-10AM",
                    "kind":"New Patient"
            })

            self.assertEqual(resp2.status_code, 401)

            responseJSON2 = resp2.get_data(as_text=True)
            response2 = json.loads(responseJSON2)
            
            self.assertEqual({"error":"Invalid time. Please ensure minutes are a 15 min interval."}, response2)

            # Tests invalid kind
            resp3 = c.post(f"/appointments/{self.second_doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"01/11/2999",
                    "time":"08:00AM",
                    "kind":"Invalid"
            })

            self.assertEqual(resp3.status_code, 401)

            responseJSON3 = resp3.get_data(as_text=True)
            response3 = json.loads(responseJSON3)
            
            self.assertEqual({"error":"Invalid kind. Must be New Patient or Follow-up."}, response3)

            # Tests doctor already has 3 appointments at that time
            third_appointment = Appointment(
                patient_first_name="test_fn",
                patient_last_name="test_ln",
                date="1/11/2000",
                time="8:00AM",
                kind="New Patient",
                doctor_id=self.doctor_id
            )

            db.session.add(third_appointment)
            db.session.commit()

            resp4 = c.post(f"/appointments/{self.doctor_id}", 
            json={
                    "patient_first_name":"Test_fn",
                    "patient_last_name":"Test_ln",
                    "date":"1/11/2000",
                    "time":"8:00AM",
                    "kind":"New Patient"
            })

            self.assertEqual(resp4.status_code, 401)

            responseJSON4 = resp4.get_data(as_text=True)
            response4 = json.loads(responseJSON4)
            
            self.assertEqual({"error":f"Doctor already has 3 appointments on 1/11/2000 at 8:00AM. Choose another day please."}, response4)
