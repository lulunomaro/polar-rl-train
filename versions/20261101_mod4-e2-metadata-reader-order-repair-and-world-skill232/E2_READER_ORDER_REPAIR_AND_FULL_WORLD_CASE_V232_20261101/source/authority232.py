from pathlib import Path
import hashlib,json,psutil,time
CANONICAL=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
def fresh_authority(expected):
 raw=CANONICAL.read_bytes();c=json.loads(raw);owner=expected['owner'];O=Path(owner['root'])
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 active=c['active_segment'];assert active is not None and active['owner_parent_pid']==owner['pid']
 identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
 q=psutil.Process(owner['pid']);actual=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd(),root=owner['root'],role='owner')
 assert q.status()!=psutil.STATUS_ZOMBIE and all(actual[k]==owner[k]for k in('pid','creation','exe','argv','cwd'))
 assert identity['pid']==owner['pid'] and identity['creation']==owner['creation'] and current['go']['w35_72']['run_id']==expected['run_id'] and current['go']==expected['go']
 return dict(passed=True,epoch=time.time(),canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical=dict(path=str(CANONICAL),generation=c['authority_generation'],total_authorized_seconds=c['authorized_training_seconds'],active_segment=active),current227D=dict(run_id=current['go']['w35_72']['run_id'],owner=actual,go=current['go']),owner_identity_file=identity,no_account_write=True)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
 with Path(p).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
def actual_authority_file(job,purpose,expected,name):
 actual=fresh_authority(expected);producer=job/(name+'_PRODUCER.json');write(producer,actual)
 out=dict(kind='ROOT_E2_FROM226_CURRENT_AUTHORITY_ACTUAL',purpose_id=purpose,job_root=str(job),passed=True,fresh_actual_read=True,checked_epoch=actual['epoch'],no_new_writer_budget_GO_or_account_write=True,canonical=actual['canonical'],mode='EXACT227D_ACTIVE',expected227D={k:expected[k]for k in('run_id','owner','go')},current227D=actual['current227D'],actual_report_refs=[dict(path=str(producer),bytes=producer.stat().st_size,SHA=H(producer))])
 p=job/(name+'.json');write(p,out);return p,out
