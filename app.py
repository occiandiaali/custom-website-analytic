from flask import Flask, request, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)

CORS(app)


# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app TEXT,
        page TEXT,
        referrer TEXT,
        userAgent TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

# --- Collector Endpoint ---
@app.route("/track", methods=["POST"])
def track():
    data = request.get_json()
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (app, page, referrer, userAgent, timestamp) VALUES (?, ?, ?, ?, ?)",
              (data.get("app"), data.get("page"), data.get("referrer"),
               data.get("userAgent"), data.get("timestamp")))
    conn.commit()
    conn.close()
    return "", 204

# --- Dashboard ---
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()

    c.execute("SELECT app, COUNT(*) as visits FROM events GROUP BY app")
    visits_per_app = c.fetchall()

    c.execute("SELECT app, page, COUNT(*) as hits FROM events GROUP BY app, page ORDER BY hits DESC")
    pages_per_app = c.fetchall()

    c.execute("SELECT app, substr(timestamp,1,10) as day, COUNT(*) FROM events GROUP BY app, day ORDER BY day")
    traffic_data = c.fetchall()

    c.execute("SELECT referrer, COUNT(*) as hits FROM events WHERE referrer IS NOT NULL AND referrer != '' GROUP BY referrer ORDER BY hits DESC LIMIT 10")
    top_referrers = c.fetchall()
    conn.close()

    traffic_dict = {}
    for app_name, day, count in traffic_data:
        traffic_dict.setdefault(app_name, {})[day] = count

    return render_template("dashboard.html",
                           visits_per_app=visits_per_app,
                           pages_per_app=pages_per_app,
                           traffic_dict=traffic_dict,
                           top_referrers=top_referrers)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/partials/visits")
def visits_partial():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("SELECT app, COUNT(*) as visits FROM events GROUP BY app")
    visits_per_app = c.fetchall()
    conn.close()
    return render_template("partials/_visits.html", visits_per_app=visits_per_app)

@app.route("/partials/pages")
def pages_partial():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("SELECT app, page, COUNT(*) as hits FROM events GROUP BY app, page ORDER BY hits DESC")
    pages_per_app = c.fetchall()
    conn.close()
    return render_template("partials/_pages.html", pages_per_app=pages_per_app)

@app.route("/partials/referrers")
def referrers_partial():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("SELECT referrer, COUNT(*) as hits FROM events WHERE referrer IS NOT NULL AND referrer != '' GROUP BY referrer ORDER BY hits DESC LIMIT 10")
    top_referrers = c.fetchall()
    conn.close()
    return render_template("partials/_referrers.html", top_referrers=top_referrers)

@app.route("/partials/traffic")
def traffic_partial():
    conn = sqlite3.connect("analytics.db")
    c = conn.cursor()
    c.execute("SELECT app, substr(timestamp,1,10) as day, COUNT(*) FROM events GROUP BY app, day ORDER BY day")
    traffic_data = c.fetchall()
    conn.close()

    traffic_dict = {}
    for app_name, day, count in traffic_data:
        traffic_dict.setdefault(app_name, {})[day] = count

    return render_template("partials/_traffic.html", traffic_dict=traffic_dict)


if __name__ == "__main__":
    init_db()  # ✅ Call here before app.run()
    app.run(debug=True)
