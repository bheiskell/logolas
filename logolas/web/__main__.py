"""Logolas web process."""

from logolas.web.app import application

def main():
    """Launch web server."""
    application().run(debug=True)

if __name__ == '__main__':
    main()
