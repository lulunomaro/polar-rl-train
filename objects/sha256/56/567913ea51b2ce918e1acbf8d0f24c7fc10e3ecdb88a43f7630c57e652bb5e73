"""Download the repair implementation and evidence, hash, zip, and upload a reviewable bundle."""
import os,json,hashlib,zipfile
from pathlib import Path
import paramiko

local=Path(__file__).resolve().parent
root='/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930'
client=paramiko.SSHClient();client.load_system_host_keys();client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.24.4.210',username='egde',password=os.environ['RM_SSH_PASSWORD'],timeout=15)
files=['REPAIR_PLAN.md','NEXT_AI_TASKS.json','budget_extension_20260930.json','REPAIR_READY.json','status.json',
       'reports/straight_preflight_3s.json','reports/supervisor_tests.json','reports/contact_actual_mesh_5925.json',
       'reports/contact_wheel32_5925_retry.json','reports/wheel_mesh_ab_comparison.json',
       'reports/contact_spectrum_diagnostic.json','reports/contact_leg_hold_5925.json','reports/leg_hold_comparison.json',
       'diagnostic_assets/ab_plan.json','diagnostic_assets/robot_wheel32_ab.usda']
files += ['isaac/mod4/'+n for n in ['supervise_repair.py','mod4_task.py','skills_isaac.py','mod4_env.py','rescue_training.py','validate_speed.py','contact_diagnostic_actual_mesh.py','contact_control_diagnostic.py','env.json','tui_rescue.py']]
try:
    with client.open_sftp() as sftp:
        for name in files:
            dest=local/'snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True)
            try:sftp.get(root+'/'+name,str(dest))
            except FileNotFoundError:
                if name in ['reports/contact_wheel32_5925_retry.json','reports/wheel_mesh_ab_comparison.json',
                            'reports/contact_leg_hold_5925.json','reports/leg_hold_comparison.json']:continue
                raise
        status=json.loads((local/'snapshot/status.json').read_text())
        (local/'snapshot/latest_evaluation.json').write_text(json.dumps(status.get('latest_evaluation'),indent=2),encoding='utf8')
        manifest={str(p.relative_to(local)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in local.rglob('*') if p.is_file() and p.name!='SHA256.json' and '__pycache__' not in p.parts}
        (local/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
        archive=local.with_suffix('.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for p in local.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:z.write(p,local.name+'/'+str(p.relative_to(local)))
        sftp.put(str(archive),root+'/'+archive.name)
        print(json.dumps({'local':str(archive),'remote':root+'/'+archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(manifest)},indent=2))
finally:client.close()
