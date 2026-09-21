from configs import FLASK_PORT
from base_api import app
from routers import auth

app.register_blueprint(auth.bp, url_prefix="/api")

@app.route('/')
def home():
    return "OK"

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=FLASK_PORT, debug=True, threaded=True)