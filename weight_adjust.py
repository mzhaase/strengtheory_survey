# Script adjusts lbs to kg using following heuristic:
#
# 1. Lifts above world records converted to kg
# 2. Calculate allometrically scaled strength (weight lifted * bodyweight ^ (-2/3))
# 3. Above certain threshold, convert to kg
#
# World records taken from http://www.powerliftingwatch.com/records/raw/women-world
# World records as of 9th Jan 2017
#
# Written for Strengtheory.com
# Copyright Mattis Haase 2017

import numpy as np

# Constants
kg_to_lbs                    = 2.2045
total_cutoff                 = 30
squat_cutoff                 = 13
bench_cutoff                 = 9
deadlift_cutoff              = 14
mens_squat_world_record      = 456
mens_bench_world_record      = 335
mens_deadlift_world_record   = 460
womens_squat_world_record    = 278
womens_bench_world_record    = 207
womens_deadlift_world_record = 267

# Columns
squat_column             = 29
squat_wrap_column        = 30
bench_column             = 31
deadlift_column          = 32
total_column             = 33
bodyweight_column        = 4
training_duration_column = 7

filename = 'original_survey_no_comma.csv'

entries = []

# Parse CSV
with open(filename, 'r') as f:
    for idx, line in enumerate(f):
        if not idx == 0:
            entries.append(line.split(','))

# Calculates allometric scaled strenght weight lifted * bodyweight ^ (-2/3)
def allometric_scaled_strength(lift, bodyweight):
    return(lift*np.power(bodyweight, -2./3))

# convert weight to kg
def convert_to_kg(weight):
    return(weight/kg_to_lbs)

# heuristic to check if it is wrong unit
def is_wrong_unit(bodyweight, training_duration, sex, squat, squat_wrap, bench, deadlift, total):
    # first, filter for world records
    if sex == 'f':
        if squat >= womens_squat_world_record: return True
        if bench >= womens_bench_world_record: return True
        if deadlift >= womens_deadlift_world_record: return True
    if sex == 'm':
        if squat >= mens_squat_world_record: return True
        if bench >= mens_bench_world_record: return True
        if deadlift >= mens_deadlift_world_record: return True
    if training_duration < 5: # if training for less than 2 years
        allometric_squat      = allometric_scaled_strength(squat, bodyweight)
        allometric_squat_wrap = allometric_scaled_strength(squat_wrap, bodyweight)
        allometric_bench      = allometric_scaled_strength(bench, bodyweight)
        allometric_deadlift   = allometric_scaled_strength(deadlift, bodyweight)
        allometric_total      = allometric_scaled_strength(total, bodyweight)

        # check whether lifts are above allometric scaled strength cutoff points
        if allometric_squat      >= squat_cutoff   : return True
        if allometric_squat_wrap >= squat_cutoff   : return True
        if allometric_bench      >= bench_cutoff   : return True
        if allometric_deadlift   >= deadlift_cutoff: return True
        if allometric_total      >= total_cutoff   : return True

changed_entries = []

# main loop
for idx, entry in enumerate(entries):
    # get all relevant colums. If column is empty, use 1 instead.
    training_duration = int(entry[training_duration_column])
    sex = 'm' if entry[1] == 1 else 'f'
    try:
        squat = float(entry[squat_column])
    except:
        squat = 1
    try:
        squat_wrap = float(entry[squat_wrap_column])
    except:
        squat_wrap = 1
    try:
        bench = float(entry[bench_column])
    except:
        bench = 1
    try:
        deadlift = float(entry[deadlift_column])
    except:
        deadlift = 1
    try:
        total = float(entry[total_column])
    except:
        total = 1
    #print(idx, entry[bodyweight_column])
    try:
        bodyweight = float(entry[bodyweight_column])
    except:
        bodyweight = 1

    # check if wrong unit using heuristic, if yes, convert all lifts to kg
    if is_wrong_unit(bodyweight, training_duration, sex, squat, squat_wrap, bench, deadlift, total):
        entries[idx][squat_column]      = convert_to_kg(squat)
        entries[idx][squat_wrap_column] = convert_to_kg(squat_wrap)
        entries[idx][bench_column]      = convert_to_kg(bench)
        entries[idx][deadlift_column]   = convert_to_kg(deadlift)
        entries[idx][total_column]      = convert_to_kg(total)
        changed_entries.append(idx + 2)

print(changed_entries)

# Write entries
# with open('survey_adjusted.csv', 'w') as f:
#     for entry in entries:
#         f.write(entry)
