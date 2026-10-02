"""Bounded read-only final collection, no Isaac/Torch imports or GPU work."""
import datetime, hashlib, json, pathlib, os
ROOT=pathlib.Path('/home/egde/fangzhen_linux')
relative=[
 'isaac/rmuc2026_field.py', 'train/deploy/contract_rm2025_later.json',
 'incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd',
 'incoming/mod4_rolling_20260913/chassis_mod4/isaac/import_contract.json',
 'incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot_cfg.py',
 'incoming/rmuc2026_field_20260911/rmuc2026_training/isaac/route_commands.py',
 'incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json',
 'third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/envs/manager_based_rl_env.py',
 'third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/managers/event_manager.py',
 'third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/managers/observation_manager.py',
 'migration/linux/run_special_phases_v3.sh']
files={}
for rel in relative:
 p=ROOT/rel
 if not p.is_file(): files[rel]={'error':'missing'};continue
 before=p.stat();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 after=p.stat()
 files[rel]={'sha256':h.hexdigest(),'bytes':after.st_size,
             'stable_during_read':before.st_mtime_ns==after.st_mtime_ns}
log=ROOT/'logs/isaac_mod4/stage_mixed_fixedplant_20260913_144725.log'
tail=''
if log.exists():
 with log.open('rb') as f:
  f.seek(max(0,log.stat().st_size-180000));tail=f.read().decode(errors='replace')
print(json.dumps({'time':datetime.datetime.now().astimezone().isoformat(),'files':files,
 'log_path':str(log),'log_tail':tail},ensure_ascii=False,indent=2))
