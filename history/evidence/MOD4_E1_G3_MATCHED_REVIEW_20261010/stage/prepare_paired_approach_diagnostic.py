"""CPU prefix diagnosis and one frozen approach-distance axis; no physics or learning."""
from pathlib import Path
import ast,copy,hashlib,json,time,zipfile
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';A=D/'artifacts';R.mkdir(exist_ok=True);A.mkdir(exist_ok=True)
G=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010';L=W/'MOD4_E1_G3_LEARNING_PREPARE_20261010'
read=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
PROTO='approved_E1_G3_derived35mm_paired_approach040_behavior_v2'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 assert not (R/'PAIRED_APPROACH_PREPARED.json').exists()
 review_path=sorted((L/'reports').glob('CANDIDATE_127_REVIEW_*.json'))[-1];v=read(review_path);assert v['review_complete'] and not v['pending']
 old=read(sorted((G/'reports').glob('G3_126_REVIEW_*.json'))[-1]);oldjid,oldrow=next(iter(old['review'].items()));groups={};data={}
 cj='clk2500-closure-episode-d3-127-e1-g3-observation-terrain-flat'
 for role,folder,review in (('source32058',G/'reports/cases'/oldjid,oldrow['review']),('candidate32063',L/'reports/cases'/cj,v['terrain'])):
  p=read(folder/'probe.json');half=p['route_scope']['wave_x_halfspan_m'];centers=np.array(p['route_scope']['tile_centers']);rows=[]
  with np.load(folder/p['full_route_raw']['name']) as a:
   for r in review['full_route_rows']:
    if r['group']=='stand':continue
    i=r['env'];direction=1 if r['group']=='forward' else -1
    wheel=direction*(a['COM_link_pos'][:,i][:,review['actual_wheel_indices'],0]-centers[i,0]);first=float(np.max(wheel[0]));best=float(np.min(wheel,axis=1).max());last=float(np.min(wheel[-1]))
    # Existing first-control wheel support proves the new .25m shorter approach retains >.2m actual front support margin; actual new run is independently checked again.
    predicted_first=first+.25;assert predicted_first < -half-.2,(role,i,predicted_first)
    delta=a['root'][-200:,i,0]-a['before_root'][-200:,i,0]
    rows.append(dict(env=i,group=r['group'],whole_wave_exit=bool(best>half),complete_original15s=bool(r['complete_episodes']),first_both_wheels_support_margin_m=-half-first,last_after_wave_margin_m=last-half,last_after_200mm_support_margin_m=last-half-.2,last2s_signed_world_x_speed_m_s=float(direction*delta.mean()/.01),predicted040_first_support_margin_m=-half-predicted_first,original_valid_prefix=r['segments'],first_ordinary_failure_control=r['first_ordinary_failure_control']))
  groups[role]={g:dict(count=sum(x['group']==g for x in rows),whole_wave_exit=sum(x['group']==g and x['whole_wave_exit'] for x in rows),full_after_support=sum(x['group']==g and x['complete_original15s'] for x in rows),incomplete=[x for x in rows if x['group']==g and not x['complete_original15s']]) for g in ('forward','reverse')}
  data[role]=dict(probe_sha256=H((folder/'probe.json').read_bytes()),raw_path=str((folder/p['full_route_raw']['name']).resolve()),raw_bytes=p['full_route_raw']['bytes'],raw_sha256=p['full_route_raw']['sha256'],ordinary=review['base_review']['ordinary'],closure_mm=review['base_review']['closure_mm'])
 diagnosis=dict(epoch=time.time(),trial_id='E1-G3-127-PAIRED-PREFIX-RETENTION-DIAGNOSIS-01',actual127_review=str(review_path.resolve()),source_and_candidate=groups,evidence=data,retention=v['summary']['retention'],decision='Reject blind PPO from32063 and advance50mm. Shorten only frozen front approach .65m to .40m to test full two-wheel10-wave plus unchanged200mm after-support within same15s. Both checkpoints tested in new paired initial state; original15s incomplete facts remain.',permanent_anti_forgetting_proven=False,not_all35mm_pass=True,no_PPO_or_budget_write=True,new_budget_seconds=0)
 save('PAIRED_PREFIX_RETENTION_DIAGNOSIS.json',diagnosis)
 # The healthy evaluator admits only300/1500 controls. Do not mutate or restart it to force a20s proposal.
 save('DURATION20S_PREDEPLOYMENT_REVIEW_REJECTED.json',dict(epoch=time.time(),trial_id='E1-G3-DURATION20S-PREDEPLOYMENT-REVIEW-01',proposal_only=True,reason='Current pinned frozen.execute asserts steps in [300,1500]. 2000-step proposal rejected at source review before package, queue, process, GPU or budget mutation. Healthy worker unchanged; alternative single frozen approach-distance axis uses valid1500 controls.',source=str((W/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/eval_worker_closure2500.py').resolve()),source_sha256=H((W/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/eval_worker_closure2500.py').read_bytes()),not_physical_failure=True,no_stage_replay=True))
 zpath=G/'artifacts/e1-g3-derived35mm-complete-route-manifest-reviewed-v2-frozen.zip';assert H(zpath.read_bytes())=='ccf288b3f32c0d028d8e1cb555d64e98af5267be27fcf4157a3750b8bdfeeebc'
 member='runtime/isaac/mod4/frozen_history_flat.py'
 with zipfile.ZipFile(zpath) as z:
  original=z.read(member);tree=ast.parse(original.decode());before=ast.dump(tree,include_attributes=False);count={'approach':0,'protocol':0}
  class Axis(ast.NodeTransformer):
   def visit_Assign(self,n):
    if any(isinstance(t,ast.Name) and t.id=='support' for t in n.targets):
     assert isinstance(n.value,ast.Constant) and n.value.value==.65;n.value.value=.4;count['approach']+=1
    return self.generic_visit(n)
   def visit_Constant(self,n):
    if n.value=='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1':n.value=PROTO;count['protocol']+=1
    return n
  transformed=Axis().visit(copy.deepcopy(tree));assert count==dict(approach=1,protocol=1)
  class Reverse(ast.NodeTransformer):
   def visit_Assign(self,n):
    if any(isinstance(t,ast.Name) and t.id=='support' for t in n.targets):n.value.value=.65
    return self.generic_visit(n)
   def visit_Constant(self,n):
    if n.value==PROTO:n.value='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1'
    return n
  assert ast.dump(Reverse().visit(copy.deepcopy(transformed)),include_attributes=False)==before
  raw=(ast.unparse(ast.fix_missing_locations(transformed))+'\n').encode();compile(raw,member,'exec');out=D/'implementation/frozen_history_flat_approach040.py';out.parent.mkdir(exist_ok=True);out.write_bytes(raw)
  m=json.loads(z.read('SOURCE_MANIFEST.json'));assert m['files'][member]==H(original);m['files'][member]=H(raw)
  for k in ('new_or_changed_members','new_or_changed_G3_members'):
   if isinstance(m.get(k),dict) and member in m[k]:m[k][member]=H(raw)
  m.update(protocol=PROTO,frozen_approach_distance_diagnostic=dict(before_m=.65,after_m=.4,steps=1500,seconds=15,physical_callbacks=6000,geometry_and_DR_and_hardware_unchanged=True,after_support_required_m=.2,no_learning=True,old15s_results_preserved=True),parent_archive_sha256=H(zpath.read_bytes()))
  package=A/'e1-g3-derived35mm-paired-approach040-frozen-v2.zip';assert not package.exists()
  with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as dst:
   for info in z.infolist():dst.writestr(info,raw if info.filename==member else json.dumps(m,indent=2).encode() if info.filename=='SOURCE_MANIFEST.json' else z.read(info.filename))
  with zipfile.ZipFile(package) as new:
   assert all(H(new.read(p))==h for p,h in m['files'].items());changed=[n for n in z.namelist() if z.read(n)!=new.read(n)];assert changed==[n for n in z.namelist() if n in (member,'SOURCE_MANIFEST.json')]
 source_sha='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b';candidate_sha='e912058d079bf1db7e40c546c54f55568218d514937cba30c65d8c913882a2cf'
 pkg=dict(path=str(package.resolve()),bytes=package.stat().st_size,sha256=H(package.read_bytes()))
 template=read(G/'reports/MANIFEST_TEMPLATE.json');jobs=[]
 for role,h in (('source32058',source_sha),('candidate32063',candidate_sha)):
  job=copy.deepcopy(template);job.update(job_id='clk2500-closure-episode-d3-128-e1-g3-'+role+'-approach040-fullroute-flat',role=role,protocol=PROTO,actual_behavior_scope='Paired new .40m front approach, same35mm complete10-wave geometry and200mm rear support, same1500 controls. Duration20s proposal rejected before deployment; no learning.',frozen_approach_distance_m=.4)
  job['artifacts']['runtime']=dict(path='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/artifacts/'+package.name,bytes=pkg['bytes'],sha256=pkg['sha256']);job['artifacts']['checkpoint']=dict(path='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/artifacts/e1-stable-own-'+h+'.pt',bytes=16750577,sha256=h);jobs.append(job)
 save('PAIRED_APPROACH_PREPARED.json',dict(epoch=time.time(),trial_id='E1-G3-PAIRED-APPROACH040-PREPARE-01',package=pkg,jobs=jobs,AST_single_axis_inverse_exact=True,changed_members=changed,file_map_verified=len(m['files']),ordinary_source_and_candidate_zero=True,old_ground_contact_tolerances_unchanged=True,new_budget_seconds=0))
 print(json.dumps(dict(groups={r:{g:{k:v for k,v in d.items() if k!='incomplete'} for g,d in gs.items()} for r,gs in groups.items()},package=pkg,changed_members=changed,all281_file_map_exact=True,no_PPO=True)))
if __name__=='__main__':main()
