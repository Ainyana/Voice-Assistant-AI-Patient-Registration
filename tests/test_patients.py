import os
os.environ["DATABASE_URL"] = "sqlite:///./test_patients.db"
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def payload(): return {"first_name":"Jane","last_name":"Doe","date_of_birth":"1990-05-15","sex":"Female","phone_number":"5551234567","email":"jane@example.com","address_line_1":"123 Main Street","city":"New York","state":"NY","zip_code":"10001"}

def test_create_and_get():
    r=client.post('/patients',json=payload()); assert r.status_code==201; pid=r.json()['data']['patient_id']; r=client.get('/patients/'+pid); assert r.status_code==200; assert r.json()['data']['last_name']=='Doe'

def test_invalid_phone():
    p=payload();p['phone_number']='123'; assert client.post('/patients',json=p).status_code==422

def test_future_dob():
    p=payload();p['date_of_birth']='2099-01-01'; assert client.post('/patients',json=p).status_code==422
