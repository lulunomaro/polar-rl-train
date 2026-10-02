from pathlib import Path
import ast
import hashlib
import json
import time

root=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
code=root/'isaac/mod4'
path=code/'validate_speed.py'
text=path.read_text()
if 'mild_initial_parameters' not in text:
    marker='''    env.reset()
    initial_capture='''
    replacement='''    env.reset()
    mild_initial_parameters = env._mild_dr.audit() if hasattr(env, '_mild_dr') else None
    mild_initial_q = env._rescue_reset_q.detach().cpu().tolist()
    mild_initial_root = robot.data.root_state_w.detach().cpu().tolist()
    initial_capture='''
    assert text.count(marker)==1
    text=text.replace(marker,replacement)
    marker="    Path(args.output).write_text(json.dumps(result,indent=2));print('RESCUE_RESULT '+json.dumps(result),flush=True)"
    assert text.count(marker)==1
    text=text.replace(marker,"""    result['mild_initial_parameters'] = mild_initial_parameters
    result['reset_joint_pos_before_physics'] = mild_initial_q
    result['reset_root_before_physics'] = mild_initial_root
    result['mild_final_parameters'] = env._mild_dr.audit() if hasattr(env, '_mild_dr') else None
"""+marker)
    ast.parse(text)
    path.write_text(text)
manifest={'recorded_epoch':time.time(), 'source':'isolated candidate only',
          'sha256':{name:hashlib.sha256((code/name).read_bytes()).hexdigest()
                    for name in ['mild_dr.py','mod4_task.py','validate_speed.py','mild_parameter_probe.py','env.json']},
          'prior_invalid_tests':'v1/v2 stopped before dynamics because audit compared the whole inertial COM pose quaternion; now inspect local COM translation and unchanged link-frame inertia.',
          'paired_rng':'DR uses separate generators; nominal pose RNG stream is unchanged'}
(root/'CANDIDATE_SOURCE_FREEZE.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
