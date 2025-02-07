from flask import Flask, request, jsonify, render_template, redirect, url_for
import random
import os
app = Flask(__name__)

# Initialize hotel rooms (1-9 floors have 10 rooms each, 10th floor has 7 rooms)
hotel = {floor: {room: 'available' for room in range(floor * 100 + 1, floor * 100 + (11 if floor < 10 else 8))} for floor in range(1, 11)}

def find_optimal_rooms(num_rooms):
    available_rooms = [(floor, room) for floor in hotel for room, status in hotel[floor].items() if status == 'available']
    if len(available_rooms) < num_rooms:
        return []
    
    # Prioritize booking on the same floor
    for floor in range(1, 11):
        floor_rooms = [room for room in hotel[floor] if hotel[floor][room] == 'available']
        if len(floor_rooms) >= num_rooms:
            return [(floor, r) for r in floor_rooms[:num_rooms]]
    
    # If not possible on one floor, minimize travel time across floors
    booked_rooms = available_rooms[:num_rooms]
    return booked_rooms

@app.route('/')
def home():
    return render_template('index.html', booked_rooms=[])

@app.route('/book', methods=['POST'])
def book_rooms():
    data = request.json
    num_rooms = data.get('num_rooms', 1)

    # Check if the number of rooms exceeds the allowed limit (5)
    if num_rooms > 5:
        return jsonify({'status': 'failed', 'message': 'You can only book up to 5 rooms at a time.'})

    # Debug: Log incoming request data
    print(f"Received booking request for {num_rooms} room(s)")

    # Find optimal rooms
    optimal_rooms = find_optimal_rooms(num_rooms)
    
    if not optimal_rooms:
        return jsonify({'status': 'failed', 'message': 'Not enough rooms available'})
    
    # Book rooms
    for floor, room in optimal_rooms:
        hotel[floor][room] = 'booked'

    # Debug: Log the booked rooms
    print(f"Booked rooms: {optimal_rooms}")
    
    # Send back the booked rooms to the frontend
    return jsonify({
        'status': 'success',
        'message': f"Successfully booked {num_rooms} room(s)",
        'booked_rooms': optimal_rooms
    })

@app.route('/reset', methods=['POST'])
def reset_rooms():
    for floor in hotel:
        for room in hotel[floor]:
            hotel[floor][room] = 'available'
    return jsonify({'status': 'success', 'message': 'All rooms reset'})

@app.route('/randomize', methods=['POST'])
def randomize_rooms():
    for floor in hotel:
        for room in hotel[floor]:
            hotel[floor][room] = 'booked' if random.random() < 0.3 else 'available'
    return jsonify({'status': 'success', 'message': 'Random occupancy generated'})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(hotel)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment, default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)

