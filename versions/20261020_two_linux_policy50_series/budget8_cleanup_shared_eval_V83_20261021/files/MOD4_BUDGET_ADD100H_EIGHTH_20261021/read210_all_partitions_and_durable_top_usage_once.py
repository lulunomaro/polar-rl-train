from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
import json,subprocess,time
def run(args,limit):
 p=subprocess.run(args,capture_output=True,text=True,timeout=limit);return dict(argv=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
block=run(['lsblk','-b','-J','-o','NAME,SIZE,FSTYPE,UUID,MOUNTPOINTS,RO,TYPE'],10);df=run(['df','-B1','-T'],10);du=run(['du','-x','-B1','--max-depth=2','/mnt/mod4_linux_durable_20261013'],60);assert len(du['stdout'])<2_000_000
print(json.dumps(dict(epoch=time.time(),block_devices=block,filesystems=df,durable_usage=du,read_only_no_mount_or_delete_or_GPU_or_account_write=True,active_training_untouched=True)))
'''
try:
 with (R/'PARTITION_USAGE_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,READ,timeout=90)
 finally:c.close()
 with (R/'PARTITIONS_AND_DURABLE_USAGE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 top=sorted((int(line.split('\t')[0]),line.split('\t',1)[1]) for line in v['durable_usage']['stdout'].splitlines() if '\t' in line)
 print(json.dumps(dict(epoch=v['epoch'],block_devices=json.loads(v['block_devices']['stdout']),filesystems=v['filesystems']['stdout'],largest_durable_paths=top[-20:],du_stderr=v['durable_usage']['stderr']),ensure_ascii=False))
except BaseException:
 with (R/'PARTITION_USAGE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
