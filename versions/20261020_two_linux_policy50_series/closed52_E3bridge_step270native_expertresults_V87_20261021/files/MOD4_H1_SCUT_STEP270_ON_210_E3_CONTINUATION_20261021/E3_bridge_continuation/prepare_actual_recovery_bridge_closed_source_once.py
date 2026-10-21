"""Copy once to the reserved next stage, run only after previous actual full closure."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes())
def main():
 cfg=read(B/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');P=Path(cfg['previous_stage_dir']);oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');proof=read(P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed'] and proof['original_canonical_cost_settled'] and set(proof['models'])=={'e2','recovery'};closed=read(P/'reports/TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL.json');assert closed['actual_finite_transport_returned'];rec=read(P/'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');rec.update(remaining_after=proof['remaining_actual_snapshot'],derived_current_cohort_source_cost_receipt_only=True,legacy18_pending_not_reconciled_again=True,source_current_cohort_original_cost_summary=proof);extension=read(B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports/EIGHTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json');assert extension['passed'] and extension['budget']['authorized_after']==1548000 and extension['budget']['extension_records']==8;rec.update(authorized_total=1548000,extension_records=8,explicit_eighth_extension_receipt=extension);
 if cfg['previous_actual_run_id']=='TWO_LINUX_POLICY50_ORIGINAL_1792562830710752300':
  assert abs(proof['remaining_actual_snapshot']-extension['budget']['remaining_seconds']+360000)<1e-5;rec['remaining_after']=extension['budget']['remaining_seconds']
 (R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(rec,indent=2));outroot=B/'two50_payloads';assert not outroot.exists();outroot.mkdir();payloads={};specs={};sources={}
 controllers=B/'two_policy50_original_account_controllers';shutil.copytree(P/'two_policy50_original_account_controllers',controllers);shutil.copy2(B/'original_account_policy50_source_same_clock_v2_CPU.py',controllers/'original_account_policy50_source_CPU.py')

 binding=json.loads((B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/reports/EIGHTH_NEW_CONTROLLERS_AND_UNUSED_WORKFLOW_CPU_ACTUAL.json').read_bytes());assert binding['passed']
 for name in ('three_slot_finite_owner_v1.py','three_slot_common_v1.py'):
  src=B.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/bound_controllers'/name;assert H(src)==binding['bound_source_SHA'][name];shutil.copy2(src,controllers/name)
 owner_path=controllers/'three_slot_finite_owner_v1.py';owner=owner_path.read_text('utf8');owner=owner.replace("set(specs)=={'e2','recovery'}","set(specs)=={'recovery'}").replace("cfg['deferred_experts']==['h1']","cfg['deferred_experts']==['e2','h1']").replace("kind='Linux_AVAILABLE_E2_E3_'","kind='Linux_RECOVERY_WHILE_H1_NATIVE210_'").replace("sum(b.CAPS[k] for k in specs)+9400.860692501068","sum(b.CAPS[k] for k in specs)+b.CAPS['h1']+9400.860692501068");owner_path.write_text(owner,'utf8')
 for key in ('recovery',):
  base=Path(oldq['payloads'][key]);oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');model=proof['models'][key];mfinal=model['final'];source=Path(mfinal['local_path']);assert source.is_file() and source.stat().st_size==mfinal['bytes'];dest=outroot/key;shutil.copytree(base,dest);spec=dict(oldq['specs'][key]);oldAdam=spec['source_Adamstep'];spec.update(previous_runtime_root=oldq['roots'][key],source_SHA=mfinal['SHA'],source_Adamstep=model['Adam'],source_policy_hz=50,policy_hz=50,closed_production_continuation=True);shutil.copy2(source,dest/'job0/source'/spec['source_filename'])
  if key=='recovery':
   p=dest/'recovery_worker.py';s=p.read_text('utf8');needle='{'+str(oldAdam)+'+20*updates}';assert needle in s;s=s.replace(needle,'{'+str(model['Adam'])+'+20*updates}');p.write_text(s,encoding='utf8')
  for p in controllers.iterdir():
   if p.is_file():shutil.copy2(p,dest/p.name)
  task=read(dest/'job0/TASK.json');task.update(id=cfg['cohort_id']+'_'+key,source_SHA=mfinal['SHA'],source_Adamstep=model['Adam'],source_policy_hz=50,policy_hz=50,source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],same_clock_complete_source_no_native_replay=True);(dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8');(dest/'QUALIFIED_RUNTIME_BASE_MANIFEST.json').write_text(json.dumps(oldm,indent=2),encoding='utf8');(dest/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');(dest/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').write_text(json.dumps(rec,indent=2),encoding='utf8');rows=[];before={x['relative']:x for x in oldm['files']}
  for p in sorted(dest.rglob('*')):
   if p.is_file() and p.name!='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
    if p.suffix=='.py':ast.parse(p.read_text('utf8'))
    rel=p.relative_to(dest).as_posix();sha=H(p) if p.suffix not in ('.pt','.npz','.usd','.stl') else (mfinal['SHA'] if rel=='job0/source/'+spec['source_filename'] else before[rel]['SHA']);rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
  m=dict(oldm,source_SHA=mfinal['SHA'],source_Adamstep=model['Adam'],source_policy_hz=50,policy_hz=50,files=rows);(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');payloads[key]=str(dest);specs[key]=spec;sources[key]=dict(SHA=mfinal['SHA'],bytes=mfinal['bytes'],Adam=model['Adam'],updates=model['updates'],path=mfinal['path'])
 q=dict(epoch=time.time(),passed=True,payloads=payloads,specs=specs,sources=sources,roots=cfg['roots'],owner_root=cfg['owner_root'],both_sources_previous_actual_wholeCPU_and_original_cost_passed=True,no_new_native_or_GO_yet=True)
 with (R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(prepared=True,source_SHA={k:x['SHA'] for k,x in sources.items()},no_native_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEXT_TWO50_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True),f,indent=2)
  raise
