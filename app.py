import sys
import sqlite3
import folium
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTextEdit, QDialog, QDialogButtonBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from io import BytesIO
from datetime import datetime, time
import uuid
from geopy.distance import geodesic
import core.config as config

MAPBOX_TOKEN = config.MAPBOX_ACCESS_TOKEN or ''

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('carpooling.db')
    c = conn.cursor()
    # Drop tables to ensure clean state
    c.execute('DROP TABLE IF EXISTS ride_passengers')
    c.execute('DROP TABLE IF EXISTS rides')
    c.execute('DROP TABLE IF EXISTS schedule_entries')
    c.execute('DROP TABLE IF EXISTS users')
    # Create tables
    c.execute('''CREATE TABLE users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        home_address TEXT,
        work_address TEXT,
        max_delay INTEGER,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE schedule_entries (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        day_of_week TEXT,
        start_time TEXT,
        end_time TEXT,
        role TEXT,
        pickup_location TEXT,
        dropoff_location TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE rides (
        id TEXT PRIMARY KEY,
        schedule_entry_id TEXT,
        user_id TEXT,
        max_riders INTEGER,
        current_riders INTEGER,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY (schedule_entry_id) REFERENCES schedule_entries(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE ride_passengers (
        id TEXT PRIMARY KEY,
        ride_id TEXT,
        user_id TEXT,
        status TEXT,
        joined_at TEXT,
        FOREIGN KEY (ride_id) REFERENCES rides(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    return conn

# Sample data: 5 users, same workplace, multiple schedule entries
def insert_sample_data(conn):
    c = conn.cursor()
    workplace = '40.7589,-73.9851'  # Times Square, NYC
    users = [
        (str(uuid.uuid4()), 'Alice', 'alice@example.com', '40.7128,-74.0060', workplace, 15),
        (str(uuid.uuid4()), 'Bob', 'bob@example.com', '40.7306,-73.9352', workplace, 10),
        (str(uuid.uuid4()), 'Charlie', 'charlie@example.com', '40.7484,-73.9857', workplace, 20),
        (str(uuid.uuid4()), 'Diana', 'diana@example.com', '40.7021,-74.0122', workplace, 12),
        (str(uuid.uuid4()), 'Eve', 'eve@example.com', '40.7769,-73.9637', workplace, 18)
    ]
    c.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)', 
        [(u[0], u[1], u[2], u[3], u[4], u[5], datetime.now().isoformat()) for u in users])
    
    schedule_entries = [
        (str(uuid.uuid4()), users[0][0], 'Monday', '08:00:00', '09:00:00', 'driver', users[0][3], workplace),
        (str(uuid.uuid4()), users[0][0], 'Wednesday', '08:30:00', '09:30:00', 'rider', users[0][3], workplace),
        (str(uuid.uuid4()), users[0][0], 'Friday', '07:45:00', '08:45:00', 'driver', users[0][3], workplace),
        (str(uuid.uuid4()), users[1][0], 'Monday', '08:15:00', '09:15:00', 'rider', users[1][3], workplace),
        (str(uuid.uuid4()), users[1][0], 'Tuesday', '08:00:00', '09:00:00', 'rider', users[1][3], workplace),
        (str(uuid.uuid4()), users[2][0], 'Monday', '08:00:00', '09:00:00', 'driver', users[2][3], workplace),
        (str(uuid.uuid4()), users[2][0], 'Thursday', '08:30:00', '09:30:00', 'rider', users[2][3], workplace),
        (str(uuid.uuid4()), users[2][0], 'Friday', '08:15:00', '09:15:00', 'driver', users[2][3], workplace),
        (str(uuid.uuid4()), users[3][0], 'Tuesday', '07:45:00', '08:45:00', 'driver', users[3][3], workplace),
        (str(uuid.uuid4()), users[3][0], 'Thursday', '08:00:00', '09:00:00', 'rider', users[3][3], workplace),
        (str(uuid.uuid4()), users[4][0], 'Monday', '08:30:00', '09:30:00', 'rider', users[4][3], workplace),
        (str(uuid.uuid4()), users[4][0], 'Wednesday', '08:15:00', '09:15:00', 'rider', users[4][3], workplace)
    ]
    c.executemany('INSERT INTO schedule_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?)', schedule_entries)
    
    rides = [
        (str(uuid.uuid4()), schedule_entries[0][0], users[0][0], 4, 0, 'planned', datetime.now().isoformat()),
        (str(uuid.uuid4()), schedule_entries[2][0], users[0][0], 4, 0, 'planned', datetime.now().isoformat()),
        (str(uuid.uuid4()), schedule_entries[5][0], users[2][0], 4, 0, 'planned', datetime.now().isoformat()),
        (str(uuid.uuid4()), schedule_entries[7][0], users[2][0], 4, 0, 'planned', datetime.now().isoformat()),
        (str(uuid.uuid4()), schedule_entries[8][0], users[3][0], 4, 0, 'planned', datetime.now().isoformat())
    ]
    c.executemany('INSERT INTO rides VALUES (?, ?, ?, ?, ?, ?, ?)', rides)
    
    conn.commit()

# Haversine distance between two coordinates
def haversine(coord1, coord2):
    lat1, lon1 = map(float, coord1.split(','))
    lat2, lon2 = map(float, coord2.split(','))
    return geodesic((lat1, lon1), (lat2, lon2)).km

# Calculate matching score
def calculate_matching_score(driver_entry, rider_entry, driver_user):
    if driver_user is None:
        return 0
    pickup_distance = haversine(driver_entry[6], rider_entry[6])
    dropoff_distance = haversine(driver_entry[7], rider_entry[7])
    max_distance = 10
    distance_score = max(0, 1 - (pickup_distance + dropoff_distance) / (2 * max_distance)) * 50

    driver_start = datetime.strptime(driver_entry[3], '%H:%M:%S').time()
    driver_end = datetime.strptime(driver_entry[4], '%H:%M:%S').time()
    rider_start = datetime.strptime(rider_entry[3], '%H:%M:%S').time()
    rider_end = datetime.strptime(rider_entry[4], '%H:%M:%S').time()
    latest_start = max(driver_start, rider_start)
    earliest_end = min(driver_end, rider_end)
    overlap_minutes = (earliest_end.hour * 60 + earliest_end.minute - latest_start.hour * 60 - latest_start.minute)
    total_minutes = 60
    time_score = max(0, overlap_minutes / total_minutes) * 30 if overlap_minutes > 0 else 0

    detour_time = (pickup_distance + dropoff_distance) * 5
    delay_score = (1 if detour_time <= driver_user[5] else 0) * 20

    return round(distance_score + time_score + delay_score, 2)

# Fetch Mapbox optimized route
def get_mapbox_optimized_route(waypoints):
    coords = ';'.join([f'{lon},{lat}' for lat, lon in waypoints])
    url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coords}?geometries=geojson&access_token={MAPBOX_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['trips']:
            return [[coord[1], coord[0]] for coord in data['trips'][0]['geometry']['coordinates']], data['trips'][0]['distance'], data['trips'][0]['duration']
        return [waypoints[0], waypoints[-1]], 0, 0
    except requests.RequestException:
        return [waypoints[0], waypoints[-1]], 0, 0

class RideDialog(QDialog):
    def __init__(self, matches, rider_id, rider_entry, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Available Rides")
        self.conn = conn
        self.rider_id = rider_id
        self.rider_entry = rider_entry
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Driver', 'Day', 'Time', 'Riders', 'Score', 'Action'])
        layout.addWidget(self.table)

        self.populate_table(matches)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def populate_table(self, matches):
        self.table.setRowCount(len(matches))
        for row, (ride_id, driver_name, day, start_time, end_time, current_riders, max_riders, status, score) in enumerate(matches):
            self.table.setItem(row, 0, QTableWidgetItem(driver_name))
            self.table.setItem(row, 1, QTableWidgetItem(day))
            self.table.setItem(row, 2, QTableWidgetItem(f"{start_time} - {end_time}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{current_riders}/{max_riders}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(score)))
            btn = QPushButton("Confirm")
            btn.clicked.connect(lambda: self.confirm_ride(ride_id))
            self.table.setCellWidget(row, 5, btn)

    def confirm_ride(self, ride_id):
        c = self.conn.cursor()
        c.execute("SELECT current_riders, max_riders, schedule_entry_id FROM rides WHERE id = ?", (ride_id,))
        result = c.fetchone()
        if not result:
            self.parent().status_label.setText("Status: Error - Invalid ride")
            return
        current_riders, max_riders, schedule_entry_id = result
        if current_riders < max_riders:
            c.execute("INSERT INTO ride_passengers VALUES (?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), ride_id, self.rider_id, 'confirmed', datetime.now().isoformat()))
            c.execute("UPDATE rides SET current_riders = ? WHERE id = ?", (current_riders + 1, ride_id))
            self.conn.commit()
            c.execute("SELECT id FROM schedule_entries WHERE id = ?", (schedule_entry_id,))
            if c.fetchone():
                self.parent().update_ride_info(ride_id)
                self.parent().status_label.setText("Status: Rider added successfully")
            else:
                self.parent().status_label.setText("Status: Error - Invalid schedule entry")
            self.accept()
        else:
            self.parent().status_label.setText("Status: Error - Ride is full")

class CarpoolingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Corporate Carpooling App")
        self.setGeometry(100, 100, 1400, 800)
        
        self.conn = init_db()
        insert_sample_data(self.conn)
        
        self.init_ui()
        self.load_map()
        self.load_users()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Left panel: User list and schedule
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet("border: 1px solid #ccc; padding: 10px;")

        self.user_list = QListWidget()
        self.user_list.itemClicked.connect(self.load_user_schedules)
        left_layout.addWidget(QLabel("Users"))
        left_layout.addWidget(self.user_list)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(['Day', 'Start', 'End', 'Role', 'Pickup'])
        self.schedule_table.itemSelectionChanged.connect(self.show_route)
        left_layout.addWidget(QLabel("Schedules"))
        left_layout.addWidget(self.schedule_table)

        self.request_ride_btn = QPushButton("Request Ride")
        self.request_ride_btn.clicked.connect(self.request_ride)
        left_layout.addWidget(self.request_ride_btn)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: blue;")
        left_layout.addWidget(self.status_label)

        layout.addWidget(left_widget, 1)

        # Center panel: Map
        self.map_view = QWebEngineView()
        self.map_view.setMinimumWidth(600)
        layout.addWidget(self.map_view, 2)

        # Right panel: Ride info
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_widget.setStyleSheet("border: 1px solid #ccc; padding: 10px;")

        right_layout.addWidget(QLabel("Ride Information"))
        self.ride_info_text = QTextEdit()
        self.ride_info_text.setReadOnly(True)
        right_layout.addWidget(self.ride_info_text)

        layout.addWidget(right_widget, 1)

        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QPushButton { background-color: #007BFF; color: white; padding: 5px; border-radius: 5px; }
            QPushButton:hover { background-color: #0056b3; }
            QTableWidget { border: 1px solid #ccc; }
            QLabel { font-weight: bold; }
        """)

    def load_map(self):
        m = folium.Map(location=[40.7589, -73.9851], zoom_start=12)
        folium.TileLayer(
            tiles=f'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}',
            attr='Mapbox',
            name='Mapbox Streets'
        ).add_to(m)

        c = self.conn.cursor()
        c.execute("SELECT name, home_address FROM users")
        for name, home in c.fetchall():
            lat, lng = map(float, home.split(','))
            folium.Marker([lat, lng], popup=name).add_to(m)

        data = BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())

    def load_users(self):
        self.user_list.clear()
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM users")
        for user_id, name in c.fetchall():
            self.user_list.addItem(f"{name} ({user_id})")

    def load_user_schedules(self, item):
        user_id = item.text().split('(')[1][:-1]
        self.schedule_table.setRowCount(0)
        c = self.conn.cursor()
        c.execute("SELECT id, day_of_week, start_time, end_time, role, pickup_location, dropoff_location FROM schedule_entries WHERE user_id = ?", (user_id,))
        for row, entry in enumerate(c.fetchall()):
            self.schedule_table.insertRow(row)
            for col, value in enumerate(entry[1:6]):
                self.schedule_table.setItem(row, col, QTableWidgetItem(str(value)))
            self.schedule_table.setItem(row, 0, QTableWidgetItem(entry[0]))
            self.schedule_table.item(row, 0).setData(32, entry[0])

    def show_route(self):
        selected_items = self.schedule_table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        entry_id = self.schedule_table.item(row, 0).data(32)
        c = self.conn.cursor()
        c.execute("SELECT pickup_location, dropoff_location, user_id FROM schedule_entries WHERE id = ?", (entry_id,))
        result = c.fetchone()
        if not result:
            self.ride_info_text.setText("Error: Schedule entry not found.")
            return
        pickup, dropoff, user_id = result

        c.execute("SELECT id FROM rides WHERE schedule_entry_id = ?", (entry_id,))
        ride = c.fetchone()
        if ride:
            self.update_ride_info(ride[0])
        else:
            self.ride_info_text.setText("No ride associated with this schedule.")

        m = folium.Map(location=[40.7589, -73.9851], zoom_start=12)
        folium.TileLayer(
            tiles=f'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}',
            attr='Mapbox',
            name='Mapbox Streets'
        ).add_to(m)

        pickup_coords = list(map(float, pickup.split(',')))
        dropoff_coords = list(map(float, dropoff.split(',')))
        waypoints = [pickup_coords]
        
        if ride:
            c.execute("SELECT u.home_address FROM ride_passengers rp JOIN users u ON rp.user_id = u.id WHERE rp.ride_id = ?", (ride[0],))
            for passenger in c.fetchall():
                waypoints.append(list(map(float, passenger[0].split(','))))
        
        waypoints.append(dropoff_coords)
        route_coords, distance, duration = get_mapbox_optimized_route(waypoints)
        
        folium.Marker(pickup_coords, popup='Driver Pickup').add_to(m)
        for i, waypoint in enumerate(waypoints[1:-1]):
            folium.Marker(waypoint, popup=f'Passenger {i+1} Pickup').add_to(m)
        folium.Marker(dropoff_coords, popup='Dropoff').add_to(m)
        folium.PolyLine(route_coords, color='blue', weight=5).add_to(m)

        c.execute("SELECT name, home_address FROM users")
        for name, home in c.fetchall():
            lat, lng = map(float, home.split(','))
            folium.Marker([lat, lng], popup=name).add_to(m)

        data = BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())

    def update_ride_info(self, ride_id):
        c = self.conn.cursor()
        c.execute("""
            SELECT r.id, u.name, se.day_of_week, se.start_time, se.end_time, 
                   r.current_riders, r.max_riders, r.status
            FROM rides r
            JOIN schedule_entries se ON r.schedule_entry_id = se.id
            JOIN users u ON r.user_id = u.id
            WHERE r.id = ?
        """, (ride_id,))
        ride = c.fetchone()
        if not ride:
            self.ride_info_text.setText("Error: Ride not found.")
            return

        c.execute("SELECT u.name FROM ride_passengers rp JOIN users u ON rp.user_id = u.id WHERE rp.ride_id = ?", (ride_id,))
        passengers = [row[0] for row in c.fetchall()]

        c.execute("SELECT pickup_location, dropoff_location FROM schedule_entries WHERE id = ?", (ride[2],))
        result = c.fetchone()
        if not result:
            self.ride_info_text.setText("Error: Schedule entry not found for this ride.")
            return
        pickup, dropoff = result

        waypoints = [list(map(float, pickup.split(',')))]
        for passenger in passengers:
            c.execute("SELECT home_address FROM users WHERE name = ?", (passenger,))
            result = c.fetchone()
            if result:
                waypoints.append(list(map(float, result[0].split(','))))
        waypoints.append(list(map(float, dropoff.split(','))))
        _, distance, duration = get_mapbox_optimized_route(waypoints)

        info = (
            f"Ride ID: {ride[0]}\n"
            f"Driver: {ride[1]}\n"
            f"Day: {ride[2]}\n"
            f"Time: {ride[3]} - {ride[4]}\n"
            f"Riders: {ride[5]}/{ride[6]}\n"
            f"Status: {ride[7]}\n"
            f"Passengers: {', '.join(passengers) if passengers else 'None'}\n"
            f"Distance: {distance/1000:.2f} km\n"
            f"Duration: {duration/60:.2f} minutes"
        )
        self.ride_info_text.setText(info)

    def request_ride(self):
        selected = self.user_list.currentItem()
        if not selected:
            self.status_label.setText("Status: Select a user first")
            return
        rider_id = selected.text().split('(')[1][:-1]
        c = self.conn.cursor()
        
        c.execute("SELECT * FROM schedule_entries WHERE user_id = ? AND role = 'rider'", (rider_id,))
        rider_entry = c.fetchone()
        if not rider_entry:
            self.status_label.setText("Status: No rider schedule found")
            return

        matches = []
        c.execute("SELECT * FROM schedule_entries WHERE role = 'driver' AND day_of_week = ?", (rider_entry[2],))
        for driver_entry in c.fetchall():
            c.execute("SELECT * FROM users WHERE id = ?", (driver_entry[1],))
            driver_user = c.fetchone()
            if driver_user:
                score = calculate_matching_score(driver_entry, rider_entry, driver_user)
                c.execute("""
                    SELECT r.id, u.name, se.day_of_week, se.start_time, se.end_time, 
                           r.current_riders, r.max_riders, r.status
                    FROM rides r
                    JOIN schedule_entries se ON r.schedule_entry_id = se.id
                    JOIN users u ON r.user_id = u.id
                    WHERE r.schedule_entry_id = ?
                """, (driver_entry[0],))
                ride = c.fetchone()
                if ride:
                    matches.append(ride + (score,))
        
        matches.sort(key=lambda x: x[8], reverse=True)
        dialog = RideDialog(matches, rider_id, rider_entry, self.conn, self)
        dialog.exec_()
        self.status_label.setText("Status: Ready")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CarpoolingApp()
    window.show()
    sys.exit(app.exec_())