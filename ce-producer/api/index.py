import datetime
import os
import random
import time
import uuid

from flask import Flask, make_response, request
from faker import Faker
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_structured


start = datetime.datetime.now()
_type = os.getenv('TASK_TYPE', 'default')
fake = Faker()
app = Flask(__name__)


def run_task():
  time.sleep(random.randrange(2, 5))
  status = random.choice([True, True, True, True, False]) # 5:1
  return status


@app.route('/', methods=['GET'])
@app.route('/healthz', methods=['GET'])
def get_healthz():
  return {"message": f"up since {start}" }


@app.route('/ce', methods=['GET', 'POST'])
def get_ce():
  status = run_task()
  attributes = {
    "id": str(uuid.uuid4()),
    "type": "demo.tm.{}.{}".format(_type, 'pass' if status else 'fail') ,
    "source": "producer.tm.demo.{}".format(_type),
  }
  if request.method == 'POST':
    attributes['custom'] = request.values.get('input')

  data = {'message': fake.text(), 'name': fake.name(), 'email': fake.email(), 'status': run_task() }

  event = CloudEvent(attributes, data)
  headers, body = to_structured(event)

  response = make_response(body)
  response.headers = headers

  return response

