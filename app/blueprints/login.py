from flask import Blueprint, request, redirect, jsonify
import requests
import datetime
from utils import database
from utils.id import generate_id
from utils.config import slack as config

import logging
logger = logging.getLogger("slack_logger")

login = Blueprint('login', __name__)

@login.route('/login', methods=['GET'])
def authorize_with_slack():
    logins = database.get_collection('logins')

    login_id = {"createdAt": datetime.datetime.utcnow(),
                   "state": generate_id()}

    logins.insert_one(login_state)
    logins.close()
    query_string = f'scope=identity.basic&client_id={config.client_id}&state={login_id.state}'
    return redirect(f'https://slack.com/oauth/authorize?{query_string}')

@login.route('/slack/auth', methods=['GET'])
def slack_callback():
    args = request.args

    if args.error or not args.state:
        return jsonify(error='failed-login')

    logins = database.get_collection('logins')
    if logins.count_documents({"state": args.state}):
        payload = {'client_id': config.client_id,
                   'client_secret': config.secret,
                   'code': args.code}

        r = requests.get(f'https://slack.com/api/oauth.access', params=payload)
        if not r.ok:
            logger.error(f'Error with Slack response: {r.status_code} {r.reason}')
            return jsonify(error='failed-login')

        r_json = r.json()

        if r_json['team_id'] != config.team_id:
            return jsonify(error='wrong-team')

        else:
            sessions = database.get_collection('sessions')
            session = {"createdAt": datetime.datetime.utcnow(),
                       "id": generate_id(),
                       "user": r_json['authorizing_user']['user_id'],
                       "accessToken": r_json['access_token']}

            sessions.insert_one(session)
            sessions.close()
            return jsonify(session=session.id)

