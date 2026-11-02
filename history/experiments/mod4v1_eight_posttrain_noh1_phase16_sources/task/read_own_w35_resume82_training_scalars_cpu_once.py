"""One actual CPU pass of completedownPPO tensorboard event artifacts only; no weights/raweval/SDK/budget.
CaptureactualLR/reward/entropy scalars tointerpret learning, never infer unloggedKL ornewgradgate.
"""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000'
code="""from pathlib import Path
import json,hashlib,struct,collections
from tensorboard.compat.proto.event_pb2 import Event
B=Path(%r);end=json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes());assert end['error']is None and end['all_own_children_waited']and end['private_finite_leases_released']and end['original_cost_settled']
logs=[p for p in(B/'production/logs').iterdir()if p.is_dir()and p.name.startswith('2026-11-02_')];assert len(logs)==1;L=logs[0];paths=sorted(L.glob('events.out.tfevents.*'));assert 0<len(paths)<=3
with(B/'OWN_RESUME82_TB_SCALAR_CPU_PURPOSE_CONSUMED.json').open('x')as f:json.dump({'purpose':'ONE_COMPLETED_OWN_PPO_EVENT_CPU_PARSE','paths':[str(p)for p in paths],'model_or_eval_raw_opens':0,'SDK_or_canonical_access':False},f)
series=collections.defaultdict(list);files=[];records=0;unsupported=[]
for p in paths:
 before=p.stat();assert before.st_size<32*1024**2;raw=p.read_bytes();after=p.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns;at=0;count=0
 while at<len(raw):
  assert len(raw)-at>=16;n=struct.unpack_from('<Q',raw,at)[0];assert 0<=n<=len(raw)-at-16;data=raw[at+12:at+12+n];ev=Event.FromString(data);at+=16+n;count+=1
  for value in ev.summary.value:
   scalar=None
   if value.HasField('simple_value'):scalar=float(value.simple_value)
   elif value.HasField('tensor'):
    t=value.tensor;shape=[d.size for d in t.tensor_shape.dim]
    if not shape or shape==[1]:
     for name in('float_val','double_val','int_val','int64_val'):
      vals=getattr(t,name)
      if len(vals)==1:scalar=float(vals[0]);break
     if scalar is None and t.tensor_content:
      types={1:'f',2:'d',3:'i',9:'q'}
      if t.dtype in types and len(t.tensor_content)==struct.calcsize('<'+types[t.dtype]):scalar=float(struct.unpack('<'+types[t.dtype],t.tensor_content)[0])
   if scalar is not None:series[value.tag].append({'step':int(ev.step),'wall_time':ev.wall_time,'value':scalar})
   else:unsupported.append({'tag':value.tag,'step':int(ev.step),'type':value.WhichOneof('value')})
 assert at==len(raw);records+=count;files.append({'path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'physical_reads':1,'TFRecord_event_count':count,'unchanged_size_mtime_during_read':True})
summary={}
for tag,values in series.items():
 nums=[r['value']for r in values];summary[tag]={'n':len(values),'first':nums[0],'last':nums[-1],'min':min(nums),'max':max(nums),'mean':sum(nums)/len(nums),'first_step':values[0]['step'],'last_step':values[-1]['step']}
result={'kind':'ACTUAL_COMPLETED_OWN_W35_RESUME82_PPO_SCALARS_CPU_ONEPASS','job':str(B),'source_parent89aca':True,'actual_new_PPO_updates':82,'final_model_SHA':'8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54','files':files,'TFRecord_events':records,'scalar_tags':sorted(series),'tag_summary':summary,'series':dict(series),'unsupported_non_scalar_events':unsupported,'model_eval_raw_SDK_canonical_access':False,'unlogged_KL_or_cause_not_inferred':True,'skill_graduation':False}
with(B/'OWN_RESUME82_PPO_SCALARS_CPU_ANALYSIS_V1.json').open('x')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(result,allow_nan=False))
"""%job
c=connect72();report={'kind':'ROOT_OWN_COMPLETED_PPO82_SCALAR_PURPOSE_CPU_ONLY','job':job,'model_or_eval_raw_or_SDK_canonical_access':False}
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stderr=err)
 if rc==0:report.update(status='ACTUAL_OWN_EVENT_BYTES_SHA_AND_SCALARS_PARSED',analysis=json.loads(text))
 else:report.update(status='FAILED_PRESERVED_NO_AUTOMATIC_REPLAY',stdout=text)
finally:c.close()
p=R/'reports'/('W35_RESUME82_OWN_TB_SCALARS_CPU_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({k:v for k,v in report.items()if k!='analysis'},ensure_ascii=False,indent=2));print(json.dumps(report.get('analysis',{}).get('tag_summary',{}),ensure_ascii=False,indent=2))
