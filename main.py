from fastapi import FastAPI
from pydantic import BaseModel
import requests


db = []
app = FastAPI()

class City(BaseModel):
    name: str
    timezone: str


@app.get('/')
def index():
    return {'key': 'value'}

@app.get('/cities')
def get_cities():
    results = []
    for city in db:
        r = requests.get(f'http://worldtimeapi.org/api/timezone/{city.timezone}')
        current_time = r.json()['datetime']
        results.append({
            'name': city.name,
            'timezone': city.timezone,
            'current_time': current_time
        })
    return results

@app.get('/cities/{city_id}')
def get_city(city_id: int):
    city = db[city_id - 1] 
    r = requests.get(f'http://worldtimeapi.org/api/timezone/{city.timezone}')
    current_time = r.json()['datetime']
    city_data = {
        'name': city.name,
        'time zone': city.timezone,
        'current_time': current_time
    } 
    return city_data

@app.post('/cities')
def create_city(city: City):
    db.append(city)
    return db[-1]

@app.delete('/cities/{city_id}')
def delete_city(city_id: int):
    db.pop(city_id - 1)
    return {}   