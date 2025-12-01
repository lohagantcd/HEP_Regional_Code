import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pwlf
import math
import csv
import os
from pathlib import Path

file_dir = r"C:\Users\Luke TCD Woek\OneDrive - Trinity College Dublin\Opensky_Flights\Raw Mission Data"
# file_dir = r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\Raw Mission Data"
all_figs = []

def make_climbdesc_csv(df_seg, name, file_wo_ext, cruise_alt=None, cruise_vel=None, adjust_edges=False):

    output_dir = f"/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{file_wo_ext}"
    # output_dir = f"/Users/OHAGANLU/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{file_wo_ext}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Nested directories '{output_dir}' created successfully.")

    alt_start, alt_end = [], []
    vel_start, vel_end = [], []
    climb_rate, body_angle = [], []

    DT = 60.0
    GS_MIN = 0.1

    for i in range(len(df_seg) - 1):
        h1 = float(df_seg.loc[i,     "altitude"])
        h2 = float(df_seg.loc[i + 1, "altitude"])
        v1 = float(df_seg.loc[i,     "velocity"])
        v2 = float(df_seg.loc[i + 1, "velocity"])

        cr = abs((h2 - h1) / DT  )                 
        gs = max((v1 + v2) * 0.5, GS_MIN)     
        theta_deg = abs(math.degrees(math.atan(cr / gs)))

        alt_start.append(h1)
        alt_end.append(h2)
        vel_start.append(v1)
        vel_end.append(v2)
        climb_rate.append(cr)
        body_angle.append(theta_deg)

    if adjust_edges and (cruise_alt is not None) and (cruise_vel is not None) and len(alt_end) > 0:
        if name.lower() == "climb":
            alt_end[-1] = float(cruise_alt)
            vel_end[-1] = float(cruise_vel)

            h1 = alt_start[-1]; h2 = alt_end[-1]
            v1 = vel_start[-1]; v2 = vel_end[-1]
            cr = abs((h2 - h1) / DT)
            gs = max((v1 + v2) * 0.5, GS_MIN)
            body_angle[-1] = abs(math.degrees(math.atan(cr / gs)))
            climb_rate[-1] = cr
        elif name.lower() == "descent":
            alt_start[0] = float(cruise_alt)
            vel_start[0] = float(cruise_vel)

            h1 = alt_start[0]; h2 = alt_end[0]
            v1 = vel_start[0]; v2 = vel_end[0]
            cr = abs((h2 - h1) / DT)
            gs = max((v1 + v2) * 0.5, GS_MIN)
            body_angle[0] = abs(math.degrees(math.atan(cr / gs)))
            climb_rate[0] = cr

    rows = [alt_start, alt_end, vel_start, vel_end, climb_rate, body_angle]
    out_name = os.path.join(output_dir, f"{name}_segments.csv")

    with open(out_name, "w", newline="") as f:
        csv.writer(f).writerows(rows)
        
    print(f"Saved {out_name} ({len(alt_start)} intervals, manual climb_rate).")


def make_cruise_csv(df_seg, file_wo_ext):

    output_dir = f"/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{file_wo_ext}"
    # output_dir = f"/Users/OHAGANLU/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{file_wo_ext}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Nested directories '{output_dir}' created successfully.")

    alt_mean  = float(df_seg["altitude"].mean())
    vel_mean  = float(df_seg["velocity"].mean())
    total_s   = float(len(df_seg))

    rows = [[alt_mean], [vel_mean], [total_s]]
    out_name = os.path.join(output_dir, "cruise_segments.csv")

    with open(out_name, "w", newline="") as f:
        csv.writer(f).writerows(rows)

    print(f"Saved {out_name} (mean cruise, manual format).")

    return alt_mean, vel_mean

for root, dirs, files in os.walk(file_dir):
    for file in files: 
        if file.endswith(".csv"):
            print("File read: ", file)
            file_path = os.path.join(file_dir, file)
            print("Mission data file path: ", file_path)
            df = pd.read_csv(file_path)

            time = df['seconds'].to_numpy() / 60.0 
            alt = df['geoaltitude'].to_numpy()
            print(time)
            print(alt)

            n_segments = 3
            model = pwlf.PiecewiseLinFit(time, alt)
            breaks = model.fit(n_segments)

            print(f"\nBreakpoints (in minutes): {breaks}\n")

            x_fit = np.linspace(time.min(), time.max(), 500)
            y_fit = model.predict(x_fit)

            for i in range(len(breaks) - 1):
                start, end = breaks[i], breaks[i + 1]
                slope = model.slopes[i]
                print(f"Segment {i+1}: {start:.2f} – {end:.2f} min, slope = {slope:.4f}")

            output_dir = r"C:\Users\Luke TCD Woek\OneDrive - Trinity College Dublin\Opensky_Flights\PWLF Processed Data"
            # output_dir = r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\PWLF Processed Data"
            filename = Path(file)
            file_wo_ext = filename.with_suffix('')
            fit_out = os.path.join(output_dir, f"{file_wo_ext}_pwlf_processed_data.csv")
            fit_df = pd.DataFrame({"time_min": x_fit, "altitude_m": y_fit})
            fit_df.to_csv(fit_out, index=False)
            print(f"\nSaved PWLF fit data to: {fit_out}")

            df["minute"] = (df["seconds"] // 60).astype(int)
            df_min = df.groupby("minute", as_index=False).agg(
                time_min=("seconds", "min"),
                altitude=("geoaltitude", "median"),
                velocity=("velocity", "median"),
            )

            break_secs = breaks * 60 + df_min["time_min"].iloc[0]

            segments = []
            for i in range(len(break_secs) - 1):
                seg = df_min[(df_min["time_min"] >= break_secs[i]) &
                             (df_min["time_min"] <= break_secs[i + 1])]
                segments.append(seg.reset_index(drop=True))

            cruise_alt, cruise_vel = make_cruise_csv(segments[1], file_wo_ext)
            make_climbdesc_csv(segments[0], "climb", file_wo_ext,  cruise_alt, cruise_vel, adjust_edges=True)
            make_climbdesc_csv(segments[2], "descent", file_wo_ext, cruise_alt, cruise_vel, adjust_edges=True)

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(time, alt, "k.", markersize=2, label="Raw data")
            ax.plot(x_fit, y_fit, "r-", linewidth=2, label="3-segment PWLF fit")
            ax.set_xlabel("Time [min]")
            ax.set_ylabel("Altitude [m]")
            ax.set_title(f"{file_wo_ext}: Altitude vs Time")
            ax.legend()
            ax.grid(True)
            
            fig, ax1 = plt.subplots(figsize=(10, 6))
            ax1.plot(time, alt, "k.", markersize=2, label="Raw data")
            ax1.set_xlabel("Time [min]")
            ax1.set_ylabel("Altitude [m]")
            ax1.set_title(f"{file_wo_ext}: Altitude vs Time")
            ax1.legend()
            ax1.grid(True)

            all_figs.append(fig)

plt.show()


