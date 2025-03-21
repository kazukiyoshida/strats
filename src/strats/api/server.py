import logging

import waitress
from flask import Flask

from strats.core.kernel import Kernel

from .router import router

BANNER = r"""
 _______ _______  ______ _______ _______ _______
 |______    |    |_____/ |_____|    |    |______
 ______|    |    |     \ |     |    |    ______|
"""

logger = logging.getLogger(__name__)


class Strats(Kernel):
    def serve(self, host="0.0.0.0", port=8000):
        app = Flask(__name__)
        app.config["kernel"] = self
        app.register_blueprint(router)
        logger.info(BANNER)
        waitress.serve(app, host=host, port=port)
