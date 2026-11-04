"""One completed diagnostic stage; reuse the original recorder unchanged."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

R=Path(__file__).resolve().parent
REPO=R.parent/'repo-lqr-robust'
ID='mod4v1-terrain-t01-contact-geometry'
BASE=Path('history/experiments/mod4v1_t01_contact_geometry_20261104')
OUT=REPO/BASE
CASE='t01_c2_contact_geometry_420151_probe001'
DATA=Path('RM_ROBUSTNESS_V1/contact_geometry_probe_v1')
NOTE='''# T01 read-only contact geometry diagnosis

One intentionally new instrumented nominal C2 trajectory, not an independent robustness sample or fourth controller. No control/robot/PD/D4/DC/KF/gate changes, no old raw rereads or extra mj_step/forward. The existing formal runner and audited plant were reused. Completed1200 controls/24000 physics/20000 scored samples, one model and one DR; 48.0468931s wall. Parent collected pwsh-7e88456422f844c3 exit0.

Every low-force left2029/right897/whole165 sample had NO contact points/active constraints and exactly zero normal, rather than an existing contact force merely falling below1N. Supported samples had active constraints and negative distances (minimum left-51.1099um/right-48.8394um). No finite separation distance was measured during absent-contact samples: do not infer finite geometric flight, mesh-facet cause, or a solver bug solely from missing contacts. MuJoCo mj_geomDistance docstring is available for the next minimal missing observation, not yet run. Original T01 is still false: only main support and whole-low-force gates failed; all non-contact gates and guide/hard gates pass. Nominal metrics exactly reproduced prior deterministic C2.

Important measurement erratum: whole_low_force.max_abs_applied_torque_Nm and post_speed_abs_peak_rad_s in the original generated summary stayed initialized0 because its accumulator used axis=None. These two whole-bucket fields are UNAVAILABLE, not physical zero. Original summary preserved; per-wheel measured fields are valid, not full DC clip duty. Task file carries the same erratum.

Human20:06 explicitly requested one reused child for LQR/MPC jumping onto200mm. Existing child abf2088f-af10-479a-9108-202785031447 dispatched and acknowledged source work20:10; no new child. This is an explicit sequencing exception alongside parent T01. J200 active source/results are excluded from this cutoff, no completed200mm claim; full36 tasks/270mm remain. No hardware/newdeps/GPU/SSH/PPO/canonical/main changes.

Raw control/contact logs are indexed only by path/size, SHA unknown and not read/hashed for archive. Existing record helper called once with in-memory sparse-add adapter, no edits to original helper. Prior pendingPH12 remains pending. Receipt updates do not trigger a new archive loop.
'''

def main():
    def gr(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
    if gr('branch','--show-current')!='mod4v1-lqr-mpc-robust' or gr('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or existing staged data')
    if (REPO/f'history/experiments/20261104-{ID}.json').exists():raise RuntimeError('Record already exists; continue its existing objects')
    OUT.mkdir(parents=True,exist_ok=False);selected=[]
    def put(rel,body):
        p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);selected.append(p.relative_to(REPO).as_posix())
    files=['TERRAIN_ADAPTATION_TASKS_V1.md','RM_ROBUSTNESS_V1/run_t01_contact_geometry_probe_v1.py',(DATA/'T01_PROTOCOL_V1.json').as_posix(),'RM_ROBUSTNESS_V1/'+CASE+'.console.log']
    files +=[(DATA/'runs'/CASE/n).as_posix() for n in('config.json','protocol.json','meta.json','result.json','contact_geometry_summary.json')]
    for rel in files:put(Path('payload')/rel,(R/rel).read_bytes())
    external=[]
    for n in('trace.jsonl','contact_trace.jsonl'):
        p=R/DATA/'runs'/CASE/n
        external.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,status='UNKNOWN_NOT_HASHED_OR_READ_FOR_ARCHIVE'))
    put('NOTE.md',NOTE.encode('utf8'));put('EXTERNAL_ARTIFACTS.json',(json.dumps(external,indent=2)+'\n').encode())
    put(Path(__file__).name,Path(__file__).read_bytes())
    listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode())
    spec=importlib.util.spec_from_file_location('original_contact_probe_recorder',REPO/'archive_tools/record_experiment.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);old=m.git
    def git(*a):
        if a and a[0]=='add':a=('add','--sparse',*a[1:])
        try:return old(*a)
        except subprocess.CalledProcessError as e:print(e.stdout,e.stderr,flush=True);raise
    m.git=git
    sys.argv=['record_experiment.py','--id',ID,'--title','Record T01 zero-contact geometry probe and human J200 delegation','--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation','New read-only C2 probe complete; original contact gates still fail. No contact points at all low-force samples, finite separation not measured.','--files',*selected]
    m.main()

if __name__=='__main__':main()
