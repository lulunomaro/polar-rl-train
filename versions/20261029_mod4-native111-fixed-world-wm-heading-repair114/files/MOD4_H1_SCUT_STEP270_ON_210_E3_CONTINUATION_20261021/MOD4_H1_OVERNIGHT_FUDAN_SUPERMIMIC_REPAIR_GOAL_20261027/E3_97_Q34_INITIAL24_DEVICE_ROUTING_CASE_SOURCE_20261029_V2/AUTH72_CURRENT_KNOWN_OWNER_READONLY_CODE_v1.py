
from pathlib import Path
import hashlib,json,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
active=c['active_segment'];known=v['known_binding'];bound=None
if active is not None:
 assert known is not None and set(known)=={'owner','run_id','go'}
 expected=known['owner'];assert active['owner_parent_pid']==expected['pid'] and set(active['experts'])==set(known['go'])
 p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert actual==expected
 assert all(g['run_id']==known['run_id'] and active['experts'][key]['started_epoch']==g['learning_started_epoch'] for key,g in known['go'].items())
 bound=dict(owner=actual,run_id=known['run_id'],genuine_slots=sorted(known['go']))
print(json.dumps(dict(passed_readonly_original72_finite_authority=True,epoch=time.time(),canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),generation=c['authority_generation'],remaining_snapshot=c['remaining_training_seconds'],CNone=active is None,known_active_binding=bound,no_account_lock_copy_write_GO_or_secondwriter=True)))
