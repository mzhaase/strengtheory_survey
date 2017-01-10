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
import csv

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

# Exercise definitions
exercises = [
    {'name':'meet_raw_squat_column',        'column': 19, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'meet_raw_squat_wrap_column',   'column': 20, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'meet_single_ply_squat_column', 'column': 21, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'meet_multi_ply_squat_column',  'column': 22, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'meet_raw_bench_column',        'column': 23, 'type':'bench', 'value':0, 'allometric_scale':0},
    {'name':'meet_single_ply_bench_column', 'column': 24, 'type':'bench', 'value':0, 'allometric_scale':0},
    {'name':'meet_multi_ply_bench_column',  'column': 25, 'type':'bench', 'value':0, 'allometric_scale':0},
    {'name':'meet_raw_dead_column',         'column': 26, 'type':'deadlift', 'value':0, 'allometric_scale':0},
    {'name':'meet_single_ply_dead_column',  'column': 27, 'type':'deadlift', 'value':0, 'allometric_scale':0},
    {'name':'meet_multi_ply_dead_column',   'column': 28, 'type':'deadlift', 'value':0, 'allometric_scale':0},
    {'name':'squat_column',                 'column': 29, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'squat_wrap_column',            'column': 30, 'type':'squat', 'value':0, 'allometric_scale':0},
    {'name':'bench_column',                 'column': 31, 'type':'bench', 'value':0, 'allometric_scale':0},
    {'name':'deadlift_column',              'column': 32, 'type':'deadlift', 'value':0, 'allometric_scale':0},
    {'name':'total_column',                 'column': 33, 'type':'total', 'value':0, 'allometric_scale':0}
]
bodyweight_column        = 4
training_duration_column = 7

filename = 'original_survey_no_comma.csv'

entries = []

# Parse CSV
with open(filename, 'r') as f:
    for idx, line in enumerate(f):
        if not idx == 0:
            entries.append(line.split(','))
        else:
            header = line

# Calculates allometric scaled strenght weight lifted * bodyweight ^ (-2/3)
def allometric_scaled_strength(lift, bodyweight):
    return(lift*np.power(bodyweight, -2./3))

# convert weight to kg
def convert_to_kg(weight):
    return(str(weight/kg_to_lbs))

# heuristic to check if it is wrong unit
def is_wrong_unit(bodyweight, training_duration, sex, exercises):
    # first, filter for world records
    for exercise in exercises:
        if exercise['type'] == 'squat':
            if sex == 'f' and exercise['value'] >= womens_squat_world_record: return True
            if sex == 'm' and exercise['value'] >= mens_squat_world_record: return True
        if exercise['type'] == 'bench':
            if sex == 'f' and exercise['value'] >= womens_bench_world_record: return True
            if sex == 'm' and exercise['value'] >= mens_bench_world_record: return True
        if exercise['type'] == 'deadlift':
            if sex == 'f' and exercise['value'] >= womens_deadlift_world_record: return True
            if sex == 'm' and exercise['value'] >= mens_deadlift_world_record: return True

    if training_duration < 5: # if training for less than 2 years
        for idx, exercise in enumerate(exercises):
            exercise['allometric_scale'] = allometric_scaled_strength(exercise['value'], bodyweight)
            if exercise['type'] == 'squat' and exercise['allometric_scale'] > squat_cutoff: return True
            if exercise['type'] == 'bench' and exercise['allometric_scale'] > bench_cutoff: return True
            if exercise['type'] == 'deadlift' and exercise['allometric_scale'] > deadlift_cutoff: return True
            if exercise['type'] == 'total' and exercise['allometric_scale'] > total_cutoff: return True

    return False

# some tests
assert_list = [{'type':'squat', 'value':278}]
assert_bodyweight = 99
assert is_wrong_unit(assert_bodyweight, 5, 'f', assert_list) == True
assert is_wrong_unit(assert_bodyweight, 4, 'm', assert_list) == False
assert_bodyweight = 60
assert is_wrong_unit(assert_bodyweight, 5, 'm', assert_list) == False
assert is_wrong_unit(assert_bodyweight, 4, 'm', assert_list) == True


changed_entries = []

# main loop
for idx, entry in enumerate(entries):
    # get all relevant colums. If column is empty, use 1 instead.
    training_duration = int(entry[training_duration_column])
    sex = 'm' if entry[1] == 1 else 'f'
    for exercise_idx, exercise in enumerate(exercises):
        try:
            exercises[exercise_idx]['value'] = float(entry[exercise['column']])
        except:
            exercises[exercise_idx]['value'] = 1

    try:
        bodyweight = float(entry[bodyweight_column])
    except:
        bodyweight = 1

    # check if wrong unit using heuristic, if yes, convert all lifts to kg
    if is_wrong_unit(bodyweight, training_duration, sex, exercises):
        for exercise in exercises:
            # ignore placeholder 1
            if not exercise['value'] == 1:
                entries[idx][exercise['column']] = convert_to_kg(exercise['value'])
                if not idx + 2 in changed_entries: changed_entries.append(idx + 2)

print(changed_entries)
#print(entries[4])
# Write entries to file
with open('survey_adjusted.csv', 'w') as f:
    f.write(header)
    for entry in entries:
        f.write(','.join(entry).replace("'",""))
