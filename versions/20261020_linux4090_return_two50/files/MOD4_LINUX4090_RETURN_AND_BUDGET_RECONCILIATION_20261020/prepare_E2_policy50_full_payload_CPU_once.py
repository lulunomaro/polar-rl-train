from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;OLD=W/'MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019/payload/e2';OUT=B/'E2_policy50_payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert json.loads((R/'E2_POLICY50_ISOLATED_OVERLAY_SOURCE_AND_SECONDS_CPU_PREPARED_ACTUAL.json').read_bytes())['passed_CPU'];assert not OUT.exists();shutil.copytree(OLD,OUT)
 for p in (B/'E2_policy50_overlay').rglob('*'):
  if p.is_file():shutil.copy2(p,OUT/p.relative_to(B/'E2_policy50_overlay'))
 taskp=OUT/'job0/TASK.json';task=json.loads(taskp.read_bytes());task.update(id='E2_POLICY50_LINUX_RETURN_20261020_V31',policy_clock_migration_authorized=True,source_policy_hz=100,policy_hz=50,source_Adamstep=772320,native_warmup_controls=0,native_timed_controls=24,clock_native_protocol='24controls/192physics/0optimizer; distinct from historical native144',no_new_budget=True);taskp.write_text(json.dumps(task,indent=2),encoding='utf8')
 checker=W/'MOD4_POLICY_50HZ_CONTINUATION_20261020/controller50V5/target_full_source_sdk_cpu_review.py';shutil.copy2(checker,OUT/'target_policy50_full_source_sdk_cpu_review.py')
 m=json.loads((OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());m.update(original_PPO_reward_command_DR_hardware_unchanged=False,explicit_50Hz_policy_clock_change=True,reward_equations_geometry_hardware_original_bytes=True,native_worker_controls144_unchanged=False,native_controls=24,policy_hz=50,source_policy_hz=100,explicit_gamma=.9801,explicit_GAE_lambda=.9025,full_target_GPU_admission_not_yet=True);rows=[]
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name!='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 m['files']=rows;(OUT/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 spec=json.loads((W/'MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019/reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())['specs']['e2'];spec.update(manifest_SHA=H(OUT/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),policy_hz=50,source_policy_hz=100,native_controls=24,closed_production_continuation=False,clock_migration_native_required=True)
 put('E2_POLICY50_FULL_PAYLOAD_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU=True,payload=str(OUT),manifest_SHA=spec['manifest_SHA'],files=len(rows),spec=spec,new_unused_root='/mnt/mod4_linux_durable_20261013/E2policy50_2010v31/e2',target_admitted=False,no_GO_or_PPO_or_original_account_write=True));print(json.dumps(dict(prepared=True,files=len(rows),native24_required=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_POLICY50_PAYLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
