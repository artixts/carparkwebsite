from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

conn = mysql.connector.connect(
    host="localhost",
    user="root",      
    password="",   
    database="ccar_parking"
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
        cursor.execute("INSERT INTO slots (slot_number) VALUES (%s)", (slot_number,))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('add_slot.html')

@app.route('/park_vehicle', methods=['GET', 'POST'])
def park_vehicle():
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        vehicle_number = request.form['vehicle_number']
        slot_number = request.form['slot_number']

        cursor.execute("SELECT slot_id, status FROM slots WHERE slot_number=%s", (slot_number,))
        slot = cursor.fetchone()

        if not slot or slot['status'] == 'Occupied':
            return "Slot not available!"

        cursor.execute(
            "INSERT INTO vehicles (owner_name, vehicle_number, slot_id) VALUES (%s, %s, %s)",
            (owner_name, vehicle_number, slot['slot_id'])
        )
        cursor.execute("UPDATE slots SET status='Occupied' WHERE slot_id=%s", (slot['slot_id'],))
        conn.commit()
        return redirect(url_for('home'))

    cursor.execute("SELECT slot_number FROM slots WHERE status='Available'")
    slots = cursor.fetchall()
    return render_template('park_vehicle.html', slots=slots)

@app.route('/remove_vehicle/<vehicle_number>')
def remove_vehicle(vehicle_number):
    cursor.execute("SELECT slot_id FROM vehicles WHERE vehicle_number=%s AND exit_time IS NULL", (vehicle_number,))
    result = cursor.fetchone()
    if result:
        slot_id = result['slot_id']
        cursor.execute("UPDATE vehicles SET exit_time=%s WHERE vehicle_number=%s", (datetime.now(), vehicle_number))
        cursor.execute("UPDATE slots SET status='Available' WHERE slot_id=%s", (slot_id,))
        conn.commit()
    return redirect(url_for('home'))

@app.route('/view_slots')
def view_slots():
    cursor.execute("""
        SELECT s.slot_number, s.status, v.owner_name, v.vehicle_number, v.entry_time, v.exit_time
        FROM slots s
        LEFT JOIN vehicles v ON s.slot_id = v.slot_id AND v.exit_time IS NULL
    """)
    data = cursor.fetchall()
    return render_template('view_slots.html', data=data)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

