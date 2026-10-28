from shop.web import app


@app.route("/")
def index():
    return "Welcome to the shop"


@app.route("/health")
def health():
    return {"status": "ok"}
