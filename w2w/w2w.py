import logging
import random

from flask import (
    Flask,
    render_template
)

from core import Resource
from model import User

import logging

logging.basicConfig(
    format='%(levelname)s - %(name)s ln.%(lineno)d - %(message)s',
    level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def main():
    return 'lalala'

@app.route('/user/<username>')
def watch(username):

    user = User.byName(username)

    query = '''
    query ($userId: Int) {
    MediaListCollection (userId: $userId, type: ANIME) {
        statusLists {
        media {
          id
          status
        }
      }
    }
    }'''

    variables = {
        'userId': user.id
    }

    res = Resource()
    planningList = res.execute(query, variables)['data']['MediaListCollection']['statusLists']['planning']
    media = random.choice(planningList)['media']

    query = '''
    query ($id: Int) {
      Media (id: $id) {
          id
          description(asHtml: true)
          status
          coverImage {
              large
          }
          title {
            userPreferred
        }
      }
    }'''

    variables = {
        'id': media['id']
    }

    media = res.execute(query, variables)['data']['Media']

    return render_template('watch.html', username=username, media=media)
