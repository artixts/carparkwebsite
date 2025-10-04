from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

# ------------------------------
# Database Configuration
# ------------------------------
# These values can come from environment variables (Render/Vercel)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "car_parking")

def get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# ------------------------------
# Routes
# ------------------------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add_slot', methods=['GET', 'POST'])
def add_slot():
    if request.method == 'POST':
        slot_no = request.form['slot_no']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO slots (slot_no, status) VALUES (%s, %s)", (slot_no, status))
        conn.commit()
        conn.close()
        return redirect(url_for('view_slots'))

    return render_template('add_slot.html')


@app.route('/park_vehicle', methods=['GET', 'POST'])
def park_vehicle():
    if request.method == 'POST':
        vehicle_no = request.form['vehicle_no']
        slot_no = request.form['slot_no']
        entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if slot exists and is free
        cursor.execute("SELECT status FROM slots WHERE slot_no = %s", (slot_no,))
        result = cursor.fetchone()

        if result and result[0] == 'Available':
            cursor.execute(
                "INSERT INTO parked_vehicles (vehicle_no, slot_no, entry_time) VALUES (%s, %s, %s)",
                (vehicle_no, slot_no, entry_time)
            )
            cursor.execute("UPDATE slots SET status = 'Occupied' WHERE slot_no = %s", (slot_no,))
            conn.commit()

        conn.close()
        return redirect(url_for('view_slots'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_no FROM slots WHERE status = 'Available'")
    available_slots = cursor.fetchall()
    conn.close()

    return render_template('park_vehicle.html', slots=available_slots)


@app.route('/view_slots')
def view_slots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM slots")
    slots = cursor.fetchall()
    conn.close()
    return render_template('view_slots.html', slots=slots)


@app.route('/delete_slot/<int:slot_id>')
def delete_slot(slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM slots WHERE id = %s", (slot_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_slots'))


@app.route('/edit_slot/<int:slot_id>', methods=['GET', 'POST'])
def edit_slot(slot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        slot_no = request.form['slot_no']
        status = request.form['status']
        cursor.execute(
            "UPDATE slots SET slot_no = %s, status = %s WHERE id = %s",
            (slot_no, status, slot_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('view_slots'))

    cursor.execute("SELECT * FROM slots WHERE id = %s", (slot_id,))
    slot = cursor.fetchone()
    conn.close()
    return render_template('add_slot.html', slot=slot)


# ------------------------------
# Main entry point
# ------------------------------
if __name__ == "__main__":
    # Local development mode
    app.run(host="0.0.0.0", port=5000)
