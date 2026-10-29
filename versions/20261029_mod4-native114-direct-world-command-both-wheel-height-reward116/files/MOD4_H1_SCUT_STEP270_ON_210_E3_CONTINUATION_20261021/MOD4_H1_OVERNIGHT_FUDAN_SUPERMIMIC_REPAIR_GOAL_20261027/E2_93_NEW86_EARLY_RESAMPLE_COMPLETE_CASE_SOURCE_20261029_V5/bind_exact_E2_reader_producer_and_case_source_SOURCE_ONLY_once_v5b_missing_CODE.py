"""Preseal source-only typed observer/producer/reader closure. No network/binaries."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
def main():
 changed=[]
 def edit(name,fn):
  p=B/name;raw=p.read_bytes();s=fn(raw.decode());ast.parse(s) if name.endswith('.py') else None;p.write_bytes(s.encode());changed.append(dict(name=name,old_SHA=H(raw),new_SHA=H(s.encode()),old_source=raw.decode()))
 def descriptor(s):
  s=s.replace('original E0 entry','original E2 entry').replace("('e0_','E0_')","('e2_','E2_')").replace('Missing declared internal E0 module','Missing declared internal E2 module').replace('empty map/flat E3 recovery','empty map/flat E2 original command').replace('original E0_PUBLIC_RECOVERY','original E2_WORLD_MOVING_SIGNED4').replace('original_E0_fullstate_entry','original_E2_fullstate_entry')
  anchor="modules['zonglin2_app_launcher']='lib/zonglin2_app_launcher.py'";assert anchor in s;s=s.replace(anchor,anchor+";modules['directional_spin_runtime']='runtime/isaac/mod4/e2_directional_spin_runtime_v1.py'",1)
  return s
 assert 'original E2_WORLD_MOVING_SIGNED4' in (B/'e2_declared_entry_receipt_cli_contract_v5.py').read_text() # already completed before original missingCODE error
 def reader(s):
  tree=ast.parse(s);code=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in n.targets))
  def change(a,b):
   nonlocal code
   assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
  change("nominal=sup['creation']+1800","early_path=F/'ACTUAL_E2_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json'\nnominal=sup['creation']+1800")
  change("if restore.exists() and native.exists() or errors or tt is not None or time.monotonic()>=limit:break","if restore.exists() and native.exists() and early_path.exists() or errors or tt is not None or time.monotonic()>=limit:break")
  change('admission=input_admission();rr=read(restore);nn=read(native);passed_native=',"early=read(early_path)\nearly_passed=bool(early and early.get('actual_original_postrestore_event_adopted') and not early.get('initial_left_censored') and early.get('observed_ids_count')==20000 and early.get('actual_physics_tick')==0 and early.get('actual_phase_zero') and early.get('source_SHA')==MODEL and not early.get('diagnostic_errors'))\nadmission=input_admission();rr=read(restore);nn=read(native);passed_native=")
  change(']+[restore,native]+errors',']+[restore,native,early_path]+errors')
  change('result=tt.get(\'result\') if tt else None;',"import importlib.util,sys\nproducer_helper=J/'e2_producer_metadata_only_read_contract_v5.py';mf=read(J/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json');pr=next(r for r in mf['files'] if r['relative']==producer_helper.name);assert H(producer_helper)==pr['SHA']\nsp=importlib.util.spec_from_file_location('owned_E2_producer_metadata_only',producer_helper);pm=importlib.util.module_from_spec(sp);sp.loader.exec_module(pm)\nproducers=pm.metadata_indexes(J,F,MODEL)\nlarge.extend(producers['indexes'])\nresult=tt.get('result') if tt else None;")
  change('print(json.dumps(dict(epoch=time.time(),purpose=mode,',"print(json.dumps(dict(early_original_resample=early,passed_actual_E2_early_observation_and_adoption=early_passed,typed_JSONL_producer_indexes_metadata_only=producers,epoch=time.time(),purpose=mode,")
  ast.parse(code);return '"""NEW E2 early first360/normal900-850, producer JSONL INDEX ONLY."""\nCODE='+repr(code)+'\n'
 edit('E2_frozen_actual_receipts_readonly_CODE_v4.py',reader)
 # New source version/purpose labels only; original reader gates are unchanged.
 edit('run_E2_new86_readonly_secure_stdin_v4.py',lambda s:s.replace("'E2_V4_'","'E2_V5_'"))
 mpath=B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mpath.read_bytes())
 for r in m['files']:
  p=Path(r['local_path'])
  if p.parent==B:r.update(bytes=p.stat().st_size,SHA=H(p.read_bytes()))
 mpath.write_bytes((json.dumps(m,indent=2)+'\n').encode());put('PRESEAL_READER_PRODUCER_SOURCE_BINDING_ORIGINALS_AND_CHANGES.json',dict(changes=changed,no_original_worker_numeric_or_resource_guard_changed=True))
 print(json.dumps(dict(source_prepared=True,inputs=len(m['files']),manifest_SHA=H(mpath.read_bytes()))))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_READER_SOURCE_BINDING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_remote_or_binaries=True));raise
