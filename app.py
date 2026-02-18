from flask import Flask, flash, redirect, render_template, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")


# PNG logos for companies
logos = { 
    "GE Aerospace": "/static/logos/ge.png",
    "Zeigler": "/static/logos/zeig.png",
    "City of Lafayette": "/static/logos/cityoflaf_logo.png",
    "Tipmont": "/static/logos/tipmont_logo.png",
    "Kirby Risk": "/static/logos/kirbyrisk_logo.png",
    "Azzip Pizza": "/static/logos/azzip_logo.png",
    "State Farm": "/static/logos/statefarm_logo.png",
    "Caterpillar": "/static/logos/caterpillar_logo.png",
    "Wabash": "/static/logos/wabash_logo.png",
    "Anderson Heating & Cooling": "/static/logos/anderson_logo.png",
    "IU Health": "/static/logos/iu_logo.png",
    "Freckles Graphics": "/static/logos/freckles_logo.png",
    "Purdue University": "/static/logos/purdue_logo.png",
    "Purdue Federal Credit Union": "/static/logos/purduefed_logo.png"
}


def get_db():
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable not set.")

        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Render requires SSL
        if "render.com" in database_url:
            g.db = psycopg2.connect(database_url, sslmode="require")
        else:
            g.db = psycopg2.connect(database_url)

    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                loan_amount DOUBLE PRECISION DEFAULT 0,
                balance DOUBLE PRECISION DEFAULT 0,
                company_name TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) AS count FROM users")
        if cursor.fetchone()["count"] == 0:
            initial_users = [
                ("zeigler", generate_password_hash("zeiglercfo"), 0, 0, "Zeigler"),
                ("city", generate_password_hash("citycfo"), 0, 0, "City of Lafayette"),
                ("purduefederal", generate_password_hash("purduefederalcfo"), 0, 0, "Purdue Federal Credit Union"),
                ("purdue", generate_password_hash("purduecfo"), 0, 0, "Purdue University"),
                ("freckles", generate_password_hash("frecklescfo"), 0, 0, "Freckles Graphics"),
                ("iuhealth", generate_password_hash("iuhealthcfo"), 0, 0, "IU Health"),
                ("anderson", generate_password_hash("andersoncfo"), 0, 0, "Anderson Heating & Cooling"),
                ("wabash", generate_password_hash("wabashcfo"), 0, 0, "Wabash"),
                ("caterpillar", generate_password_hash("caterpillarcfo"), 0, 0, "Caterpillar"),
                ("statefarm", generate_password_hash("statefarmcfo"), 0, 0, "State Farm"),
                ("azzip", generate_password_hash("azzipcfo"), 0, 0, "Azzip Pizza"),
                ("kirbyrisk", generate_password_hash("kirbyriskcfo"), 0, 0, "Kirby Risk"),
                ("tipmont", generate_password_hash("tipmontcfo"), 0, 0, "Tipmont"),
                ("generalelectric", generate_password_hash("generalelectriccfo"), 0, 0 , "GE Aerospace"),
                ("admin", generate_password_hash("JArocks"), 0, 0, "JA Admin")
            ]

            cursor.executemany(
                "INSERT INTO users (username, password, loan_amount, balance, company_name) VALUES (%s, %s, %s, %s, %s)",
                initial_users
            )

        db.commit()

def validate_user_session():
    if "username" not in session:
        flash("Please log in first.")
        return redirect("/")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["username"] = username

            if username == "admin":
                return redirect("/leaderboard")

            if user["loan_amount"] == 0:
                return redirect("/initial")
            else:
                return redirect("/paybalance")

        flash("Invalid credentials.")
        return redirect("/")

    return render_template("login.html")


@app.route("/initial", methods=["GET", "POST"])
def initial():
    if (res := validate_user_session()):
        return res

    if request.method == "POST":
        username = session["username"]
        loan_amount = float(request.form["loan"])

        if loan_amount > 300:
            return render_template("initial.html")

        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "UPDATE users SET loan_amount = %s, balance = %s WHERE username = %s",
            (loan_amount, loan_amount, username)
        )
        db.commit()

        flash(f"Loan amount of {loan_amount} received.")
        return redirect("/paybalance")

    return render_template("initial.html")


@app.route("/paybalance", methods=["GET", "POST"])
def paybalance():
    if (res := validate_user_session()):
        return res

    username = session["username"]
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == "POST":
        paid = float(request.form["amountpaid"])

        cursor.execute("SELECT loan_amount, balance FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        balance = float(user["balance"]) - paid
        initial_loan = float(user["loan_amount"])
        amount_paid = initial_loan - balance

        cursor.execute(
            "UPDATE users SET balance = %s WHERE username = %s",
            (balance, username)
        )
        db.commit()

        flash(f"Current balance: {balance}")
        return render_template(
            "paybalance.html",
            amount=amount_paid,
            initial=initial_loan,
            balance=balance
        )

    cursor.execute("SELECT loan_amount, balance FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    return render_template(
        "paybalance.html",
        amount=(float(user["loan_amount"]) - float(user["balance"])),
        initial=float(user["loan_amount"]),
        balance=float(user["balance"])
    )


@app.route("/leaderboard")
def leaderboard():
    if (res := validate_user_session()):
        return res

    is_admin = session.get("username") == "admin"

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT company_name, loan_amount, balance FROM users")
    users = cursor.fetchall()

    leaderboard_data = {}

    for user in users:
        if user["company_name"] == "JA Admin":
            continue

        loan = float(user["loan_amount"])
        balance = float(user["balance"])

        progress = 0 if loan == 0 else ((loan - balance) / loan) * 100
        leaderboard_data[user["company_name"]] = round(progress, 2)

    sorted_leaderboard = dict(
        sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)
    )

    return render_template(
        "leaderboard.html",
        leaderboard=sorted_leaderboard,
        is_admin=is_admin,
        logos=logos
    )


@app.route("/reset", methods=["POST"])
def reset():
    if session.get("username") != "admin":
        flash("Unauthorized access.")
        return redirect("/")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("UPDATE users SET loan_amount = 0, balance = 0")
    db.commit()

    flash("Database reset complete.")
    return redirect("/leaderboard")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
