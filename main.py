from fastapi import FastAPI
from pydantic import BaseModel
import requests
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

db = []
app = FastAPI()


class City(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50, unique=True)
    timezone = fields.CharField(50)


city_pydantic = pydantic_model_creator(City, name='City')
cityin_pydantic = pydantic_model_creator(City, name="CityIn", exclude_readonly=True)


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
async def create_city(city: cityin_pydantic):
    city_obj = await City.create(**city.dict(exclude_unset=True))
    return await city_pydantic.from_tortoise_orm(city_obj)


@app.delete('/cities/{city_id}')
def delete_city(city_id: int):
    db.pop(city_id - 1)
    return {}


register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
