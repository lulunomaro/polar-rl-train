"""Apply both course limits to every substep of native CPU replays."""
from jump380_r4_replay import Trial, run_trial as replay_physics
from jump380_r6_scene import YAW_LIMIT_DEG, Y_LIMIT


def run_trial(plant, policy, trial, video=None):
    plant.measure_course = True
    try:
        row, trace = replay_physics(plant, policy, trial, video)
    finally:
        plant.measure_course = False
    on_course = plant.max_abs_y <= Y_LIMIT and plant.max_abs_yaw <= YAW_LIMIT_DEG
    row.update(course_qualified=on_course, max_abs_y_m=plant.max_abs_y, max_abs_yaw_deg=plant.max_abs_yaw,
               approach_max_abs_y_m=plant.approach_max_abs_y, approach_max_abs_yaw_deg=plant.approach_max_abs_yaw)
    for metric in ("obstacle_pass_physical", "qualified", "strict_direct"):
        row[metric] &= on_course
    return row, trace
