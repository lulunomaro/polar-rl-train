"""New reader distinguishes local COM position from D0 principal-axis quaternion representation."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D7_NOMINAL_FRAME_REVIEW_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,hashlib,zipfile,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (R/'D7_NOMINAL_FRAME_REVIEW_PUBLISHED.json').exists()
first=read(R/'D7_NOMINAL_RESET_REVIEW_PUBLISHED.json');base=Path(first['job']['artifacts']['runtime']['path']);assert sha(base)==first['job']['artifacts']['runtime']['sha256']
failed=read(E/'eval_results'/first['job']['job_id']/'result.json');assert failed['phase']=='retained_failed'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';t=payload[key].decode()
old="    for key in ('body_names','chassis_index','chassis_name','local_COM_pose_xyz_xyzw','explicit_PD','body_count','joint_names'):"
assert t.count(old)==1
t=t.replace(old,"    from pathlib import Path as D7Path\n    D7Path(str(args.output)+'.D7_readback.raw.json').write_text(json.dumps(dict(initial=D7_initial,final=result['D7_nominal_chassis_PD_final']),indent=2))\n    for key in ('body_names','chassis_index','chassis_name','explicit_PD','body_count','joint_names'):")
old="    result['D7_D0_mass_inertia_can_change_on_selected_episode_reset']=True";assert t.count(old)==1
t=t.replace(old,"    import torch as D7torch\n    D7_first=D7torch.tensor(D7_initial['static']['local_COM_pose_xyz_xyzw'])\n    D7_final=D7torch.tensor(result['D7_nominal_chassis_PD_final']['static']['local_COM_pose_xyz_xyzw'])\n    assert D7torch.equal(D7_first[...,:3],D7_final[...,:3])\n    result['D7_local_COM_xyz_unchanged_across_D0_reset']=True\n    result['D7_raw_principal_axis_quaternion_changed_across_D0_reset']=not D7torch.equal(D7_first[...,3:],D7_final[...,3:])\n"+old)
compile(t,key,'exec');payload[key]=t.encode()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},D7_local_COM_xyz_invariant_raw_quaternion_readbacks_retained=True)
dest=E/'artifacts/d7-chassis-pd-local-position-frame-reviewed-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
row=first['job'];oldjob=row['job_id'];job='clk2500-closure-episode-d3-90-d7-chassis-pd-frame-sdk'
row.update(job_id=job,published_epoch=time.time(),role='Read-only actual local COM xyz and explicit motor PD; retain raw quaternion and D0 mass/inertia reset changes, strict independent frame equality at each read',replaces_failed_reader_job=oldjob)
row['artifacts']['runtime']=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
target=E/'eval_queue'/(job+'.json');assert not target.exists();tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,target)
v=dict(epoch=time.time(),job=row,old_failed_job=oldjob,old_failed_result=failed,old_package_raw_retained=True,parameter_setters=0,production265_and_canonical_unchanged=True,SDK_pending=True)
(R/'D7_NOMINAL_FRAME_REVIEW_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 compile(code,'D7 readonly frame boundary correction','exec')
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D7_NOMINAL_FRAME_REVIEW_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],old_failures_retained=True)))
finally:c.close()
