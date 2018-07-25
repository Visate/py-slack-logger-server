from flask import Flask
from blueprints.log_message import log_message
from blueprints.login import login
import logging
import sys

# Logging setup
logger = logging.getLogger("slack_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Initialize app
app = Flask(__name__)
logger.info("Starting slack logger application.")
app.register_blueprint(log_message)
app.register_blueprint(login)

# Debug start
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)

