# Create a venv and enter it:
(Inside of the project's folder)  
python3 -m venv venv  
source venv/bin/activate

# Install dependencies:
pip3 install -r requirements.txt

# Create database and test database:
createdb doctor-calendar   
createdb doctor-calendar-test

# Run the app:
flask run  
(May need to use flask run -p 5001 if you have something running on port 5000)

# To run the tests:
python -m unittest -v tests.py