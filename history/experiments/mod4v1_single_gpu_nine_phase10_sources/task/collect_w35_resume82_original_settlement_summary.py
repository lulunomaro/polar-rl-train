"""One read-only originalcanonical summary, only own1431521 completedsegment. No localledgercopy/write/modelread."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;code="""from pathlib import Path
import json,hashlib,sys
D=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000');sys.path.insert(0,str(D))
from single_writer72_authority_V85M_source import authority_original_extension_count
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);rows=[a for a in c['completed_segments']if a.get('owner_parent_pid')==1431521];assert len(rows)==1;a=rows[0];assert a['actual_terminal_rows']['w35_72']['terminal_all_own_children_waited']and a['actual_terminal_rows']['w35_72']['returncode']==0
fields=('kind','owner_parent_pid','started_epoch','ended_epoch','charged_expert_seconds','last_account_epoch','experts');segment={k:a[k]for k in fields if k in a};active=c['active_segment'];summary={'kind':'ORIGINAL_CANONICAL_OWN_W35_RESUME82_TERMINAL_SETTLEMENT_READONLY','original_path':str(C),'canonical_SHA_at_read':hashlib.sha256(raw).hexdigest(),'authority_generation':c['authority_generation'],'total_authorized_training_seconds':c['total_authorized_training_seconds'],'charged_training_seconds':c['charged_training_seconds'],'remaining_training_seconds':c['remaining_training_seconds'],'original_extension_count':authority_original_extension_count(c),'new_extensions_or_refunds_created_by_reader':0,'own_complete_segment':segment,'own_new_PPO_updates':a['actual_terminal_rows']['w35_72']['final']['actual_new_PPO_updates'],'own_terminal_saved_SHA':a['actual_terminal_rows']['w35_72']['final']['final']['SHA'],'active_segment_is_none':active is None,'active_owner_pid_only_if_other_current':None if active is None else active.get('owner_parent_pid'),'local_ledger_copy':False,'canonical_writes':0,'PT_or_SDK_reads':0};print(json.dumps(summary))
"""
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('W35_RESUME82_ORIGINAL_SETTLEMENT_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,ensure_ascii=False,indent=2))
