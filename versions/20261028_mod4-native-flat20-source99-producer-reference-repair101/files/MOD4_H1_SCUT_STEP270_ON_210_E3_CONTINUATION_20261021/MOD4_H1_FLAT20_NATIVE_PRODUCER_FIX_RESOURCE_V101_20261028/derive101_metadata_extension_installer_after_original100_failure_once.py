from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028'
p=O/'install_two100_target20_exact_saved99_sources_SDK_initial_CPU_once.py';s=p.read_text();tree=ast.parse(s);node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in x.targets));pre=ast.literal_eval(node.value)
for a,b in [("old=owned/'MOD4_H1_STANCE_START_COMPARE_2610v99/continue97'","old=Path(v['old100_root'])"),('MOD4_TWO99_NATIVE_START_COMPARE_2610v99','MOD4_TWO100_USER_FLAT20_NATIVE_2610v100'),('524298.0874166489','524081.4115035534'),('604005','609931'),('1793184720.95','1793190660.79'),('7229.4461233615875','216.67591309547424'),('3616.467855453491','106.82035231590271'),('3612.9782679080963','109.85556077957153'),("'restart'","'h1_seed28'")]:
 assert a in pre,a;pre=pre.replace(a,b)
a=" assert node['terminal_all_own_children_waited'] and not node['original_error'] and node['returncode']==0 and node['final']['passed'] and exit['actual_all_own_children_waited']";assert pre.count(a)==1;pre=pre.replace(a," assert node['terminal_all_own_children_waited'] and node['original_error'] and not (node.get('final') or {}).get('passed',False) and exit['actual_all_own_children_waited']")
a=pre.index(" if rel==v['new_native_relative']");b=pre.index('\n elif prior',a);pre=pre[:a]+' if prior'+pre[b+len('\n elif prior'):];ast.parse(pre);assert '37e34522213d' in pre and '37restart' not in pre
lines=s.splitlines(keepends=True);s=''.join(lines[:node.lineno-1])+'PRE='+repr(pre)+'\n'+''.join(lines[node.end_lineno:])
oldpath="L/'TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1/reports/TWO99_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json'";assert s.count(oldpath)==1;s=s.replace(oldpath,'OLD_ACTUAL_LAUNCH_PLACEHOLDER')
s=s.replace('TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_V2_ACTUAL.json','TWO101_EXACT_PRODUCER_REFERENCE_FIX_PAYLOADS_PREPARED_ACTUAL.json').replace('TWO100_','TWO101_').replace('NATIVE100_','NATIVE101_').replace('two100_','two101_')
s=s.replace('OLD_ACTUAL_LAUNCH_PLACEHOLDER',"L/'TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1/reports/TWO100_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json'")
a="dict(root=root,GPU=spec['GPU_UUID'],mode=mode,manifest=manifest,";assert s.count(a)==1;s=s.replace(a,"dict(root=root,GPU=spec['GPU_UUID'],mode=mode,manifest=manifest,old100_root=spec['old100_job_root'],")
ast.parse(s);p=N/'install_two101_producer_reference_metadata_extension_CPU_once.py';p.write_text(s,encoding='utf8')
(N/'reports/FROZEN_UNUSED_101_METADATA_EXTENSION_INSTALLER_INDEX_V1.json').write_text(json.dumps(dict(epoch=time.time(),entry=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),old100_original_failure_fee_allout_bound=True,only_source_label_changed_native_states_not_reloaded_by_CPU=True,unused=True),indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,entry=str(p))))
