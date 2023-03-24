import datetime
import humanize
import json
import random
import time
import uuid

from flask import Flask, make_response, request
from faker import Faker
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_structured


start = datetime.datetime.now()
fake = Faker()
app = Flask(__name__)

#-----
def run_task():
  time.sleep(random.randrange(2, 5))
  status = random.choice([True, True, True, True, False]) # 5:1
  return status


def get_response(request, method='build'):
  status = run_task()
  attributes = {
    "id": str(uuid.uuid4()),
    "type": "kn.{}.{}".format(method, 'pass' if status else 'fail') ,
    "source": "kn.demo.{}".format(method),
  }
  data = {'message': fake.text(), 'name': fake.name(), 'email': fake.email(), 'status': run_task() }

  if request.method == 'POST':
    try:
      data['input_json'] = request.get_json()
    except:
      data['input_json'] = {}

    try:
      data['input_headers'] = { i: request.headers[i] for i in request.headers.keys() if i.startswith('Ce') }
    except:
      data['input_headers'] = {}

  event = CloudEvent(attributes, data)
  headers, body = to_structured(event)

  response = make_response(body)
  response.headers = headers

  return response

#-----
@app.route('/', methods=['GET'])
@app.route('/healthz', methods=['GET'])
def get_healthz():
  now = datetime.datetime.now()
  return {"message": f"ce-demo: up since {humanize.naturaltime(now - start)}" }


@app.route('/task/<kind>', methods=['GET', 'POST'])
def do_task(kind):
  return get_response(request=request, method=kind)


#@app.route('/commit', methods=['GET', 'POST'])
#def do_commit():
#  return get_response(request=request, method='commit')


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
