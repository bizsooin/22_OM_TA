import pandas as pd
import numpy as np
import datetime

# This code is a simple program to facilitate the attendance check of students during non-face-to-face zoom classes.
# Due to the instability of Zoom and the Internet, some students may leave during Zoom classes, or some may withdraw from attendance.
# Our goal is to create an algorithm that considers all the time students actually participated in class.

# set late time based on class number (5 minutes)
def class_word(date, class_num):
    time = '11:05:00' if class_num == 1 else '09:35:00'
    norm_time = f"{date} {time}"
    return norm_time

# convert time to second for comparison
def time_to_num(time_str):
    hh, mm, ss = map(int, time_str.split(':'))
    return ss + 60 * (mm + 60 * hh)

#input file (customed file, usually zoom attendence files contains join time, leave time, duration, name, id number)
zoom = pd.read_excel("zoom_0930_0310.xlsx")

zoom_subset = zoom[['ID number', 'Name', 'Duration']]
zoom_name = zoom[['ID number', 'Name']]

# calculate student's attendence duration
time_consume = np.array([time_to_num(duration) for duration in zoom_subset['Duration']])

# Query the time each student attended and left class
zoom_time = pd.concat([zoom_subset, pd.DataFrame(time_consume, columns=['Time'])], axis=1)
zoom_time_count = zoom_time.groupby('ID number').sum('Time')
zoom_join = zoom.groupby(['ID number', 'Name'])['Join time'].min()
zoom_leave = zoom.groupby(['ID number', 'Name'])['Leave time'].max()

zoom_one = (
    zoom_name
    .merge(zoom_join, on='ID number')
    .merge(zoom_leave, on='ID number')
    .merge(zoom_time_count, on='ID number')
)

# Example for class 1 starting at 03/08/2021 09:30:00
norm_time = "2022/03/08 09:35:00"

# Late are based on whether student joined class after 5 minutes
# Left Early are based on whether student attended class more than 1 hour
late_0308 = [0.5 if join > norm_time or time < 3600 else 0 for join, time in zip(zoom_one['Join time'], zoom_one['Time'])]

#if that the case, deduct 0.5 point for penalty
late_0308 = pd.DataFrame(late_0308, columns=['Late_0308'])

zoom_new = pd.concat([zoom_one, late_0308], axis=1)
zoom_new = zoom_new.drop_duplicates().reset_index(drop=True)

print(zoom_new)