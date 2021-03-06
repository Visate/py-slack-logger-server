from flask import Blueprint, request
from utils import database
from utils.config import slack as config
import logging
import time
import hmac
import hashlib

logger = logging.getLogger("slack_logger")

log_message = Blueprint('log_message', __name__)

@log_message.route('/log', methods=['POST'])
def log():
    if not from_slack(request):
        abort(401)

    req = request.get_json(force=True, silent=True)
    if req is None:
        logger.warn("Received unknown request.")
        return

    logger.info("Received call from Slack Events API.")
    logger.info(req)
    req_type = req.get('type')
    if req_type == 'url_verification':
        logger.debug('Responding to Slack Events URL verification.')
        return req.get('challenge')

    elif req_type == 'event_callback':
        event = req.get('event')
        event_type = event.get('type')
        event_subtype = event.get('subtype')
        logger.debug(f'Received {event_type} event.')

        if event_type == 'message':
            if event.get('thread_ts'):
                update_thread(event)

            elif event_subtype == 'message_changed':
                update_edited(event)

            elif event_subtype == 'message_deleted':
                update_deleted(event)

            else:
                old_msg = database.find_document({'channel': event.get('channel'),
                                                  'ts':      event.get('ts')},
                                                 'messages')

                if old_msg:
                    logger.warn('Event already exists in database, added to duplicates collection.')
                    database.insert_document(event, 'duplicates')

                else:
                    insert_message(event)

            return "OK"

# Verify event is from Slack
def from_slack(request):
    request_body = request.get_data(as_text=True)
    timestamp = request.headers['X-Slack-Request-Timestamp']
    if abs(time.time() - timestamp) > 5 * 60:
        logger.warn("Timestamp is older than expected time delta.")
        return False
    signature_base = f'v0:{timestamp}:{request_body}'
    generated_sig = 'v0=' + hmac.digest(bytes(config['signature'], 'utf-8'), bytes(signature_base, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
    slack_sig = request.headers['X-Slack-Signature']
    return hmac.compare(generated_sig, slack_sig)

# DB helpers
def update_edited(edited_msg):
    new_msg = edited_msg['message']
    old_msg = edited_msg['previous_message']

    search = {'channel': edited_msg['channel'],
              'ts':      new_msg['ts']}

    update = {'$set': {'text': new_msg['text'],
                       'edited_ts': new_msg['edited']['ts']}}

    if old_msg.get('edited'):
        old_ts = old_msg['edited']['ts']
    else:
        old_ts = old_msg['ts']

    update['$push'] = {'edited': {'user': old_msg['user'],
                                  'text': old_msg['text'],
                                  'ts':   old_ts}}

    database.update_document(search, update, 'messages')

def update_thread(thread_msg):
    search = {'channel': thread_msg['channel'],
              'ts':      thread_msg['thread_ts']}

    update = {'$push': {'thread': {'user': thread_msg['user'],
                                   'ts':   thread_msg['ts']}}}

    database.update_document(search, update, 'messages')
    database.insert_document(thread_msg, 'messages')

def update_deleted(deleted_msg):
    search = {'channel': deleted_msg['channel'],
              'ts':      deleted_msg['deleted_ts']}

    update = {'$set': {'deleted': true,
                       'deleted_ts': deleted_msg['ts']}}

    database.update_document(search, update, 'messages')

def insert_message(message):
    database.insert_document(message, 'messages')

