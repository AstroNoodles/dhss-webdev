import psycopg2
from flask import Flask, render_template, request
from dataclasses import dataclass
import datetime

app = Flask(__name__)

@dataclass
class FlightSchema:
    flight_number: str
    origin_code: str
    dest_code: str
    departure_date: datetime.time
    departure_time: datetime.time
    duration: datetime.timedelta

@dataclass
class CapacitySchema:
    flight_number: str
    departure_date: datetime.date
    current_bookings: int
    plane_type: str
    capacity: int

@dataclass
class AirportSchema:
    flight_number: str
    code_name: str
    city: str
    country: str

def readable_departure_time(departure_time: datetime.time):
    return departure_time.strftime('%I:%M %p')

def readable_duration(duration: datetime.timedelta):
    total_seconds = int(duration.total_seconds())
    total_hrs = total_seconds // 3600
    total_min = (total_seconds // 60) % 60

    return f"{total_hrs} hrs {total_min} min"

@app.route('/check_capacity/<string:id>')
def check_capacity(id):
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password='local456',
        host='localhost'
    )

    print("Received ID: ", id)

    cursor = connection.cursor()

    capacity_query = f"""
    SELECT f.flight_number, f.departure_date, COUNT(b.seat_number), a.plane_type, capacity FROM Booking b 
    JOIN Flight f ON b.flight_number = f.flight_number
    JOIN Aircraft a ON f.plane_type = a.plane_type
    WHERE f.flight_number='{id}'
    GROUP BY f.flight_number, f.departure_date, a.plane_type, capacity
    ORDER BY f.departure_date ASC
    """

    origin_dest_code_query = f"""
    SELECT f.flight_number, f.origin_code, f.dest_code FROM FlightService f
    WHERE f.flight_number='{id}'
    """

    cursor.execute(capacity_query)

    capacity_out = cursor.fetchall()

    capacity_records = [CapacitySchema(flight_number=record[0], departure_date=record[1], 
                                       current_bookings=record[2], plane_type=record[3], capacity=record[4]) for record in capacity_out]

    cursor.execute(origin_dest_code_query)
    code_out = cursor.fetchone()
    _, origin_code, dest_code = code_out

    print(origin_code, dest_code)

    print(origin_code, dest_code)

    
    origin_query = f"""
    SELECT a.name, a.city, a.country FROM Airport a
    WHERE a.airport_code='{origin_code}'
    """

    departure_query = f"""
    SELECT a.name, a.city, a.country from Airport a
    WHERE a.airport_code='{dest_code}'
    """

    cursor.execute(origin_query)
    origin_name, origin_city, origin_country = cursor.fetchone()

    cursor.execute(departure_query)
    dest_name, dest_city, dest_country = cursor.fetchone()

    print(origin_name, origin_city, origin_country)
    print(dest_name, dest_city, dest_country)

    cursor.close()
    connection.close()

    return render_template('flight_capacity.html', 
                           info_record_origin=AirportSchema(id, origin_name, origin_city, origin_country), 
                           info_record_destination=AirportSchema(id, dest_name, dest_city, dest_country), 
                           capacity_records=capacity_records)




@app.route('/update', methods=['POST'])
def update():
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password='local456',
        host='localhost'
    )

    cursor = connection.cursor()

    origin_airport = request.form['origin-airport']
    dest_airport = request.form['dest-airport']
    start_date = request.form['date1']
    end_date = request.form['date2']

    print(origin_airport, dest_airport, start_date, end_date)

    query = f"""
    SELECT distinct fs.flight_number, fs.origin_code, fs.dest_code, b.departure_date, fs.departure_time, fs.duration from FlightService fs
    JOIN Booking b ON fs.flight_number = b.flight_number WHERE fs.origin_code='{origin_airport}' AND fs.dest_code='{dest_airport}' 
	AND b.departure_date >= '{start_date}'::date 
    AND b.departure_date <= '{end_date}'::date
    """

    cursor.execute(query)
    out = cursor.fetchall()
    
    print('Output of Specific Query:')
    print(out)

    condition_records = [FlightSchema(flight_number=record[0], origin_code=record[1], dest_code=record[2], 
                                      departure_date=record[3], 
                                      departure_time=readable_departure_time(record[4]), 
                                      duration=readable_duration(record[5])) for record in out]

    cursor.close()
    connection.close()

    return render_template('flight_database.html', records=condition_records)

@app.route('/')
def index():
    print('ehllo')
    return render_template('flight_database.html', records=[])

if __name__ == '__main__':
    app = Flask(__name__)
    app.run()
