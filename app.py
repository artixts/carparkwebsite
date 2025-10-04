from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)

# MySQL connection using environment variables
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "ccar_parking")
)
cursor = conn.cursor(dictionary=True)

@app.route('/')
def home():
    cursor.execute("SELECT * FROM slots")
    slots = cursor.fetchall()
    return render_template('index.html', slots=slots)

@app.route('/add_slot', methods=['GET', 'POST'])
def add_slot():
    if request.method == 'POST':
        slot_number = request.form['slot_number']
        status = request.form['status']
        cursor.execute("INSERT INTO slots (slot_number, status) VALUES (%s, %s)", (slot_number, status))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('add_slot.html')

@app.route('/park_vehicle', methods=['GET', 'POST'])
def park_vehicle():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        slot_id = request.form['slot_id']
        time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO parked_vehicles (vehicle_number, slot_id, time_in) VALUES (%s, %s, %s)",
            (vehicle_number, slot_id, time_in)
        )
        cursor.execute("UPDATE slots SET status='Occupied' WHERE id=%s", (slot_id,))
        conn.commit()
        return redirect(url_for('home'))
    cursor.execute("SELECT * FROM slots WHERE status='Available'")
    slots = cursor.fetchall()
    return render_template('park_vehicle.html', slots=slots)

@app.route('/view_slots')
def view_slots():
    cursor.execute("SELECT * FROM slots")
    slots = cursor.fetchall()
    return render_template('view_slots.html', slots=slots)

@app.route('/edit_slot/<int:id>', methods=['GET', 'POST'])
def edit_slot(id):
    cursor.execute("SELECT * FROM slots WHERE id=%s", (id,))
    slot = cursor.fetchone()
    if request.method == 'POST':
        slot_number = request.form['slot_number']
        status = request.form['status']
        cursor.execute("UPDATE slots SET slot_number=%s, status=%s WHERE id=%s", (slot_number, status, id))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('add_slot.html', slot=slot)

@app.route('/delete_slot/<int:id>')
def delete_slot(id):
    cursor.execute("DELETE FROM slots WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('home'))

# For Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
