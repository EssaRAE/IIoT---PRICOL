from flask import Flask, request, jsonify
import pyodbc
import smtplib
from email.message import EmailMessage
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        cnxn = pyodbc.connect("Driver={SQL Server};"
                              "Server=localhost\\SQLEXPRESS03;"
                              "Database=Pricol_demo;"
                              "Trusted_Connection=yes;")
        return cnxn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/api/machine-details')
def machine_details():
    operator_id = request.args.get('operator_id')
    if not operator_id:
        return jsonify({'error': 'Operator ID is required'}), 400

    cnxn = get_db_connection()
    if cnxn:
        cursor = cnxn.cursor()
        query = ("SELECT u_id, model_id, group_no "
                 "FROM [dbo].[process_data_125] WHERE operator_id = ?")
        cursor.execute(query, (operator_id,))
        row = cursor.fetchone()
        cnxn.close()
        if row:
            return jsonify({
                'u_id': row.u_id,
                'model_id': row.model_id,
                'group_no': row.group_no,
                'machine_name': f"Machine {row.model_id}"
            })
        else:
            return jsonify({'error': 'Operator not found'}), 404
    return jsonify({'error': 'Database connection failed'}), 500


# --- Alarm Mail Endpoint ---
from email.message import EmailMessage
import smtplib

@app.route('/api/send-alarm-mail', methods=['POST'])
def send_alarm_mail():
    data = request.json
    # Example: lookup team email based on machine/alarmType/code
    team_email = '22r225@psgtech.ac.in'  # Receiver email as requested
    msg = EmailMessage()
    msg['Subject'] = f"Alarm: {data.get('alarmType')} on {data.get('machine')}"
    msg['From'] = 'essa786ez@gmail.com'  # Your Gmail address
    msg['To'] = team_email
    msg.set_content(f"""
    Machine: {data.get('machine')}
    Alarm Type: {data.get('alarmType')}
    Code: {data.get('code')}
    Time: {data.get('time')}
    Remark: {data.get('remark')}
    """)
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('essa786ez@gmail.com', 'password')  # Replace with your Gmail app password
            server.send_message(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_team_email(machine, alarmType):
    # Simple mapping, replace with your logic or database lookup
    team_map = {
        'M07': 'cnc_team@example.com',
        'M02': 'robot_team@example.com',
        '': 'control_team@example.com'
    }
    return team_map.get(machine, 'default_team@example.com')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required.'}), 400

    # Admin bypass
    if username == 'admin' and password == 'admin':
        return jsonify({'success': True})

    cnxn = get_db_connection()
    if cnxn:
        cursor = cnxn.cursor()
        query = "SELECT COUNT(*) FROM [dbo].[Users] WHERE User_Name = ? AND Password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        cnxn.close()
        if result and result[0] > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401
    return jsonify({'success': False, 'error': 'Database connection failed.'}), 500


# Checklist API endpoint
@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    opid = request.args.get('opid')
    cnxn = get_db_connection()
    if not cnxn:
        return jsonify({'items': [], 'error': 'Database connection failed'}), 500
    cursor = cnxn.cursor()
    machine_type = 'LVDT' if opid == 'OP02' else 'CNC'
    try:
        cursor.execute(f"SELECT [{machine_type}] FROM [Checks Sheet]")
        rows = cursor.fetchall()
        items = [row[0] for row in rows if row[0]]
        cnxn.close()
        return jsonify({'items': items})
    except Exception as e:
        cnxn.close()
        return jsonify({'items': [], 'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)