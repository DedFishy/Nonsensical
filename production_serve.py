import waitress
import main

waitress.serve(main.app, port=8041, url_scheme='https')