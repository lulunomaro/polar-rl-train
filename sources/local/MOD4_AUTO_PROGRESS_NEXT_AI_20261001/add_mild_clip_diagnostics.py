"""Candidate-only diagnostic additions; legacy statistics and gates remain visible."""
from pathlib import Path
import ast
import hashlib
import json
import time

root=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
code=root/'isaac/mod4'
path=code/'validate_speed.py'
text=path.read_text()
if 'speed_safety_pass_gain_compensated' not in text:
    def replace(old,new):
        global text
        assert text.count(old)==1, old
        text=text.replace(old,new)
    replace("app=AppLauncher(args).app", "os.environ['RM_MILD_DR_PROFILE']=args.dr_profile\napp=AppLauncher(args).app")
    replace('AppLauncher.add_app_launcher_args(p);args=p.parse_args()',
            "p.add_argument('--dr-profile',choices=['nominal','white_v1'],default=os.environ.get('RM_MILD_DR_PROFILE','nominal'))\nAppLauncher.add_app_launcher_args(p);args=p.parse_args()")
    replace('    sat_run=torch.zeros(n,device=dev);sat_longest=sat_run.clone()',
            '    sat_run=torch.zeros(n,device=dev);sat_longest=sat_run.clone()\n    rated_run=sat_run.clone();rated_longest=sat_run.clone()')
    replace("'left_support_slip_control','right_support_slip_control']}",
            "'left_support_slip_control','right_support_slip_control','wheel_rating_clip_fraction','leg_rating_clip_fraction']}")
    replace('''        lc=(computed[:,legids]-applied[:,legids]).abs()>.1''','''        lc=(computed[:,legids]-applied[:,legids]).abs()>.1
        rated_wc=(computed[:,wheelids]*robot.actuators['wheels'].episode_scale-applied[:,wheelids]).abs()>.1
        rated_lc=(computed[:,legids]*robot.actuators['legs'].episode_scale-applied[:,legids]).abs()>.1
        values.update(wheel_rating_clip_fraction=rated_wc.float().mean(1),
                      leg_rating_clip_fraction=rated_lc.float().mean(1))''')
    replace('''        sat_longest=torch.maximum(sat_longest,sat_run)''','''        sat_longest=torch.maximum(sat_longest,sat_run)
        rated_run=torch.where(mask & rated_wc.any(1),rated_run+env.step_dt,0.)
        rated_longest=torch.maximum(rated_longest,rated_run)''')
    replace("    per['longest_wheel_effort_clip_s']=sat_longest",
            "    per['longest_wheel_effort_clip_s']=sat_longest\n    per['longest_wheel_rating_clip_s']=rated_longest")
    marker="    result['speed_limit']=args.speed_limit"
    replace(marker,"""    result['speed_safety_pass_gain_compensated']=result['physics_pass'] and all(
        g['survival_fraction']>=.95 and g['max_tilt'] is not None and g['max_tilt']<=15
        and g['height_error']<=.03 and g['wheel_rating_clip_fraction']<=.2
        and g['leg_rating_clip_fraction']<=.2 and g['longest_wheel_rating_clip_s']<=.5
        and g['wheel_near_no_load']<=.01 and g['base_force']<=1. and g['guide_force']<=1.
        for g in groups)
    result['gain_compensated_clipping_semantics']='requested PD torque times episode output gain minus final applied torque; 10ms snapshots, not substep peaks. Raw computed-minus-applied and original speed_safety_pass are retained separately.'
"""+marker)
    ast.parse(text);path.write_text(text)
manifest={'recorded_epoch':time.time(),'source':'isolated candidate only; old production unchanged',
          'changes':'CLI nominal/white_v1 replay and parallel gain-compensated torque-rating diagnostics; legacy gates preserved',
          'sha256':{name:hashlib.sha256((code/name).read_bytes()).hexdigest()
                    for name in ['mild_dr.py','mod4_task.py','validate_speed.py','mild_parameter_probe.py','env.json']}}
(root/'CANDIDATE_SOURCE_FREEZE_v2.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
