"""
This server mimics GlobalSportsMedia error "server overloaded".

Start the server:

    uwsgi --module apps.gsm.server_overloaded --http 127.0.0.1:8000 --venv=../env
"""
def application(env, sr):
    sr('200 OK', [('Content-Type','text/html')])
    return 'Servers are overloaded. Please try again later.'
