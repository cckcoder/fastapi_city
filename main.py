from fastapi import FastAPI
from pydantic import BaseModel
import requests
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

app = FastAPI()


class City(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50, unique=True)
    timezone = fields.CharField(50)

    def current_time(self) -> str:
        r = requests.get(f'http://worldtimeapi.org/api/timezone/{self.timezone}')
        current_time = r.json()['datetime']
        return current_time

    class PydanticMeta:
        computed = ('current_time', )


city_pydantic = pydantic_model_creator(City, name='City')
cityin_pydantic = pydantic_model_creator(City, name="CityIn", exclude_readonly=True)


@app.get('/')
def index():
    return {'key': 'value'}


@app.get('/cities')
async def get_cities():
    return await city_pydantic.from_queryset(City.all())


@app.get('/cities/{city_id}')
async def get_city(city_id: int):
    return await city_pydantic.from_queryset_single(City.get(id=city_id))


@app.post('/cities')
async def create_city(city: cityin_pydantic):
    city_obj = await City.create(**city.dict(exclude_unset=True))
    return await city_pydantic.from_tortoise_orm(city_obj)


@app.put('/cities/{city_id}')
async def update_city(city_id: int, city: cityin_pydantic):
    await City.filter(id=city_id).update(**city.dict(exclude_unset=True))
    return await city_pydantic.from_queryset_single(City.get(id=city_id))


@app.delete('/cities/{city_id}')
async def delete_city(city_id: int):
    delete_count = await City.filter(id=city_id).delete()
    return {}


register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
