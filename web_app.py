from flask import Flask, request, render_template_string
from supabase import create_client
import os
import ssl

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# HTML Form Template
onboarding_form = '''
<!doctype html>
<title>Sofi AI Onboarding</title>
<h2>🧠 Sofi AI - Open Your Virtual Account</h2>
<form method=post>
  First Name: <input type=text name=first_name required><br><br>
  Last Name: <input type=text name=last_name required><br><br>
  Address: <input type=text name=address required><br><br>
  City: <input type=text name=city required><br><br>
  State: <input type=text name=state required><br><br>
  BVN: <input type=text name=bvn required><br><br>
  Telegram Chat ID: <input type=text name=telegram_chat_id required><br><br>
  Choose Transaction PIN: <input type=password name=pin required><br><br>
  <input type=submit value=Submit>
</form>
'''

@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        bvn = request.form["bvn"]
        telegram_chat_id = request.form["telegram_chat_id"]
        pin = request.form["pin"]

        # Insert user data into Supabase
        try:
            supabase.table("users").insert({
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "city": city,
                "state": state,
                "bvn": bvn,
                "telegram_chat_id": telegram_chat_id,
                "pin": pin
            }).execute()
            return "<h3>🎉 Onboarding Successful!</h3><p>Your profile has been created.</p>"
        except Exception as e:
            return f"<h3>❌ Onboarding Failed!</h3><p>Error: {e}</p>"

    return render_template_string(onboarding_form)

if __name__ == "__main__":
    # Path to your SSL certificate and key files
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile="path/to/certificate.crt", keyfile="path/to/private.key")

    app.run(port=5001, ssl_context=ssl_context)
