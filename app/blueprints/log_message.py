from flask import Blueprint, request
from utils import database
from utils.config import slack as config
import logging

logger = logging.getLogger(__name__)

log_message = Blueprint('log_message', __name__)

@log_message.route('/log', methods=['POST'])
def log():
    form = request.form
    logger.info("Received call from Slack Events API.")
    logger.info(form)
    req_type = form.get('type')
    if req_type == 'url_verification':
        logger.debug('Responding to Slack Events URL verification.')
        return form.get('challenge')

    elif req_type == 'event_callback':
        event = form.get('event')
        event_type = event.get('type')
        event_subtype = event.get('subtype')
        logger.debug(f'Received {event_type} event.')

        if event_type == 'message':
            if event.get('thread_ts'):
                pass

            elif event_subtype == 'message_changed':
                pass

            elif event_subtype == 'message_deleted':
                pass

            else:
                pass

# Verify event is from Slack
def verify_event(secret):
    return config['signature'] == secret

# DB helpers
def update_edited(edited_msg):
    original_msg = edited_msg['message']

    search = {'channel': original_msg['channel'],
              'ts':      original_msg['ts']}

    update = {'$push': {'edited': {'$each': [{'user': original_msg['edited']['user'],
                                   'text': original_msg['text'],
                                   'ts':   original_msg['edited']['ts']}],
                                   '$position': 0}}}

    database.find_and_update_document(search, update, 'messages')

def update_thread(thread_msg):
    search = {'channel': thread_msg['channel'],
              'ts':      thread_msg['thread_ts']}

    update = {'$push': {'thread': {'user': thread_msg['user'],
                                   'ts':   thread_msg['ts']}}}

    database.find_and_update_document(search, update, 'messages')
    database.insert_document(thread_msg, 'messages')

def update_deleted(deleted_msg):
    search = {'channel': deleted_msg['channel'],
              'ts':      deleted_msg['deleted_ts']}

    update = {'$set': {'deleted': true,
                       'deleted_ts': deleted_msg['ts']}}

    database.find_and_update_document(search, update, 'messages')

def insert_message(message):
    database.insert_document(message, 'messages')

