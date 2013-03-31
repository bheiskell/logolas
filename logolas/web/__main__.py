"""Execute the web application."""

from logolas.configuration import Configuration
from logolas.web.app import application

import os

def main():
    """Launch web application."""

    configuration = Configuration()
    configuration.load_yaml(os.environ['LOGOLAS_CONFIG'])

    debug = 'LOGOLAS_DEBUG' in os.environ

    application(configuration).run(debug=debug)

if __name__ == '__main__':
    main()
