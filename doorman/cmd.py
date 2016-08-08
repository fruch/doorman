#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import logging

from doorman import __version__

from doorman.webserver import app

__author__ = "Israel Fruchter (ifruchte)"
__copyright__ = "Israel Fruchter (ifruchte)"
__license__ = "simple-bsd"

_logger = logging.getLogger(__name__)


def main(args):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    app.run(debug=True)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
