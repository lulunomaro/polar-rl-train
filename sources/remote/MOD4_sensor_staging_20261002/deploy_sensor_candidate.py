"""Run on remote: copy source to an isolated candidate, never budget/checkpoints."""
from pathlib import Path
import hashlib, json, shutil
OLD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
ROOT=Path('/home/egde/rl_candidates/MOD4_sim2real_sensor_dr_20261002')
STAGING=Path(__file__).resolve().parent
assert not (ROOT/'reports/DEPLOYMENT_RECEIPT.json').exists(), 'Already deployed: inspect, never overwrite'
if not ROOT.exists():
    ROOT.mkdir();(ROOT/'reports').mkdir()
    for name in ('isaac','train'):
        shutil.copytree(OLD/name,ROOT/name,ignore=shutil.ignore_patterns('__pycache__','floor_fix_source_before'))
else:
    assert (ROOT/'isaac/mod4/mod4_task.py').read_bytes()==(OLD/'isaac/mod4/mod4_task.py').read_bytes(), 'Partial deployment changed source'
CODE=ROOT/'isaac/mod4'
for name in ('sensor_core.py','sim2real_sensor.py','sensor_readback_probe.py','test_sensor_core.py'):
    shutil.copy2(STAGING/name,CODE/name)
path=CODE/'mod4_task.py';s=path.read_text()
old='    if OBS_DELAY_MAX <= 0:\n'
assert s.count(old)==1
s=s.replace(old,"    sensor = getattr(env, '_sim2real_sensor', None)\n    if sensor is not None:\n        return sensor.transform(env, key, base)\n"+old,1)
old='        from mild_dr import configure\n        configure(self)\n';assert s.count(old)==1
s=s.replace(old,old+'        from sim2real_sensor import configure as configure_sensor\n        configure_sensor(self)\n')
path.write_text(s)
config=json.loads((CODE/'env.json').read_text());assert float(config['RM_SPIN_MAX_RAD_S'])==4.
config['RM_SIM2REAL_SENSOR_PROFILE']='sensor_v1'
(CODE/'env.json').write_text(json.dumps(config,indent=2))
for name in ('spin_rate_probe.py','validate_speed.py'):
    p=CODE/name;s=p.read_text()
    marker='AppLauncher.add_app_launcher_args(p);args=p.parse_args()'
    assert marker in s
    s=s.replace(marker,"p.add_argument('--sensor-profile',choices=['off','sensor_v1'],default=os.environ.get('RM_SIM2REAL_SENSOR_PROFILE','off'))\n"+marker)
    marker="os.environ['RM_MILD_DR_PROFILE']=args.dr_profile"
    assert marker in s
    s=s.replace(marker,marker+"\nos.environ['RM_SIM2REAL_SENSOR_PROFILE']=args.sensor_profile")
    marker="    initial_q=robot.data.joint_pos.cpu().tolist();initial_root=robot.data.root_state_w.cpu().tolist()" if name=='spin_rate_probe.py' else None
    # Append actual audit without changing any existing statistics or gates.
    write_marker="    Path(args.output).write_text(json.dumps(result,indent=2))" if name=='spin_rate_probe.py' else None
    if name=='validate_speed.py':
        # Locate its report variable; support only this audited source spelling.
        lines=s.splitlines();writes=[line for line in lines if 'Path(args.output).write_text' in line]
        assert len(writes)==1,writes
        write_marker=writes[0].split(';')[0]
        var='report' if 'json.dumps(report' in write_marker else 'result'
    else:var='result'
    assert write_marker in s
    s=s.replace(write_marker,"    from sim2real_sensor import audit as sensor_audit\n    "+var+"['sensor_audit']=sensor_audit(env)\n"+write_marker)
    p.write_text(s)
manifest=json.loads((OLD/'reports/SPIN_SOURCE_FREEZE.json').read_text())
for name in ('mod4_task.py','env.json','spin_rate_probe.py','validate_speed.py','sensor_core.py','sim2real_sensor.py','sensor_readback_probe.py'):
    manifest['sha256']['isaac/mod4/'+name]=hashlib.sha256((CODE/name).read_bytes()).hexdigest()
manifest.update(candidate_only=True,source_root=str(OLD),canonical_budget_not_copied=True,
    sensor_profile='sensor_v1',physics_reward_ppo_unchanged=True)
(ROOT/'reports/SPIN_SOURCE_FREEZE.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'reports/DEPLOYMENT_RECEIPT.json').write_text(json.dumps(dict(source_root=str(OLD),candidate_root=str(ROOT),budget_added=False,production_modified=False),indent=2))
print(ROOT)
