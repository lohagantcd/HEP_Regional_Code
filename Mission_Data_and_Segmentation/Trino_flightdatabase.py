from pyopensky.trino import Trino
import pandas as pd
import csv
import time
import os
from datetime import datetime
import numpy as np
print("Current working directory:", os.getcwd())

trino = Trino()

start_date = "2024-05-13"
stop_date = "2024-05-14"
icao24 = "4caa54"
departure_airport = ["EGPF"]
arrival_airport = ["EIDW"]


# callsign = "EAG76P"

flights = trino.flightlist(
    start=start_date,
    stop=stop_date,
    icao24=icao24,
    # callsign=callsign,
    departure_airport=departure_airport,
    arrival_airport=arrival_airport
)

print(flights)

flights_list = pd.DataFrame(flights)

# Calculate flight times
flights_list['firstseen'] = pd.to_datetime(flights_list['firstseen'])
flights_list['lastseen'] = pd.to_datetime(flights_list['lastseen'])
flights_list['flight_duration'] = flights_list['lastseen'] - flights_list['firstseen']

# Format times to HH:MM:SS
flights_list['departure_time'] = flights_list['firstseen'].dt.strftime('%H:%M:%S')
flights_list['arrival_time'] = flights_list['lastseen'].dt.strftime('%H:%M:%S')

# Convert timedelta to hours, minutes, seconds
def format_duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

flights_list['flight_duration_str'] = flights_list['flight_duration'].apply(format_duration)

# Print flight details
for _, flight in flights_list.iterrows():
    print(f"\nFlight: {flight['callsign']}")
    print(f"Departure Time: {flight['departure_time']}")
    print(f"Arrival Time: {flight['arrival_time']}")
    print(f"Total Flight Time: {flight['flight_duration_str']}")

    flights_list.to_csv("C:\\Users\\Luke TCD Woek\\OneDrive - Trinity College Dublin\\Opensky_Flights\\flightlist_output.csv", 
                    index=False, 
                    quoting=csv.QUOTE_NONNUMERIC)
    # flights_list.to_csv("C:\\Users\\OHAGANLU\\OneDrive - Trinity College Dublin\\Opensky_Flights\\flightlist_output.csv", 
    #                 index=False, 
    #                 quoting=csv.QUOTE_NONNUMERIC)

    # flight = flights.iloc[0]

    # print(flight)

    BUFFER_SECONDS = 1800 
    
    # Apply buffer to the query window
    query_start = int(flight["firstseen"].timestamp()) - BUFFER_SECONDS
    query_end = int(flight["lastseen"].timestamp()) + BUFFER_SECONDS

    start_time = query_start
    stop_time = query_end

    query = f""" SELECT time, lat, lon, baroaltitude, geoaltitude, velocity, vertrate, onground, heading FROM state_vectors_data4 WHERE icao24 = '{icao24}'
    AND time BETWEEN {start_time} AND {stop_time} ORDER BY time """

    t0 = time.time()
    trajectory = trino.query(query)
    elapsed = time.time() - t0

    print(f"\nQuery completed in {elapsed:.1f} s")
    print(f"Retrieved {len(trajectory)} rows")

    # Ensure DataFrame
    if not isinstance(trajectory, pd.DataFrame):
        trajectory = pd.DataFrame(trajectory)

    if trajectory.empty:
        print("\nNo trajectory data returned for this flight.")
    else:

        if "time" in trajectory.columns:
            trajectory["datetime_utc"] = pd.to_datetime(trajectory["time"], unit="s", utc=True)
            trajectory["datetime_local"] = trajectory["datetime_utc"].dt.tz_convert("Europe/Dublin")
        else:
            print("Warning: no 'time' column found to convert.")

        save_path = r"C:\Users\Luke TCD Woek\OneDrive - Trinity College Dublin\Opensky_Flights"
        # save_path = r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\Raw Mission Data"
        os.makedirs(save_path, exist_ok=True)
        callsign = flight.get("callsign", "Unknown").strip()
        print(callsign)
        filename = f"{callsign}_{start_time}.csv".replace(" ", "_")
        full_path = os.path.join(save_path, filename)

        print("Will save to:", full_path)
        print("Final dataframe shape:", trajectory.shape)

        trajectory.to_csv(full_path, index=False)
        print(f"Saved trajectory data to '{full_path}'")
