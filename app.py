from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

DATA_STORE = {
    'user': {},
    'medicines': []
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/save_user', methods=['POST'])
def save_user():
    profile = request.get_json() or {}
    DATA_STORE['user'] = {
        'fullName': profile.get('fullName', ''),
        'age': profile.get('age', ''),
        'email': profile.get('email', ''),
        'caregiverEmail': profile.get('caregiverEmail', '')
    }
    return jsonify({'status': 'success', 'message': 'User profile saved'}), 200

@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    medicine = request.get_json() or {}
    required_fields = ['id', 'name', 'dosage', 'time', 'food', 'duration', 'startDate']
    if not all(field in medicine for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing medicine fields'}), 400

    existing = next((item for item in DATA_STORE['medicines'] if item['id'] == medicine['id']), None)
    if existing:
        existing.update(medicine)
        existing['updatedAt'] = datetime.utcnow().isoformat()
    else:
        medicine['missedCount'] = medicine.get('missedCount', 0)
        medicine['consecutiveMissed'] = medicine.get('consecutiveMissed', 0)
        medicine['status'] = medicine.get('status', 'pending')
        medicine['reminderActive'] = medicine.get('reminderActive', False)
        medicine['updatedAt'] = datetime.utcnow().isoformat()
        DATA_STORE['medicines'].append(medicine)

    return jsonify({'status': 'success', 'medicine': medicine}), 200

@app.route('/get_medicines', methods=['GET'])
def get_medicines():
    return jsonify(DATA_STORE['medicines']), 200

@app.route('/mark_taken', methods=['PUT'])
def mark_taken():
    payload = request.get_json() or {}
    medicine_id = payload.get('id')
    medicine = next((item for item in DATA_STORE['medicines'] if item['id'] == medicine_id), None)
    if not medicine:
        return jsonify({'status': 'error', 'message': 'Medicine not found'}), 404

    medicine['status'] = 'taken'
    medicine['consecutiveMissed'] = 0
    medicine['lastActionDate'] = datetime.utcnow().date().isoformat()
    medicine['updatedAt'] = datetime.utcnow().isoformat()
    return jsonify({'status': 'success', 'medicine': medicine}), 200

@app.route('/mark_missed', methods=['PUT'])
def mark_missed():
    payload = request.get_json() or {}
    medicine_id = payload.get('id')
    medicine = next((item for item in DATA_STORE['medicines'] if item['id'] == medicine_id), None)
    if not medicine:
        return jsonify({'status': 'error', 'message': 'Medicine not found'}), 404

    medicine['status'] = 'missed'
    medicine['missedCount'] = medicine.get('missedCount', 0) + 1
    medicine['consecutiveMissed'] = medicine.get('consecutiveMissed', 0) + 1
    medicine['lastActionDate'] = datetime.utcnow().date().isoformat()
    medicine['updatedAt'] = datetime.utcnow().isoformat()
    return jsonify({'status': 'success', 'medicine': medicine}), 200

@app.route('/delete_medicine', methods=['DELETE'])
def delete_medicine():
    medicine_id = request.args.get('id')
    if not medicine_id:
        return jsonify({'status': 'error', 'message': 'Missing medicine id'}), 400

    DATA_STORE['medicines'] = [item for item in DATA_STORE['medicines'] if item['id'] != medicine_id]
    return jsonify({'status': 'success', 'message': 'Medicine deleted'}), 200

@app.route('/send_email', methods=['POST'])
def send_email():
    payload = request.get_json() or {}
    return jsonify({'status': 'success', 'message': 'Email call recorded', 'payload': payload}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
