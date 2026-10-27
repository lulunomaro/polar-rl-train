from pathlib import Path
import ast,json,hashlib
N=Path(__file__).resolve().parent
p=N/'install_native93_two_distinct_targets_actual_source_SDK_CPU_UNUSED_once.py'
s=p.read_text('utf8')
# Original unexecutedV1 retained. Actual88C detached receipt pins node==jobroot.
old="node=json.loads((old.parent/'node_h1/NODE_TERMINAL_ACTUAL.json').read_bytes())['row']"
new="node=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']"
assert s.count(old)==1;s=s.replace(old,new,1)
needle="put('NATIVE93_SOLE72_BEFORE_CPU_ACTUAL.json',before)"
code='''cpu210=cpu
  replacements=[("args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(script)]", "args=[v['python'],'-u','-B',str(script)]"),
   ("expected=[loader,'--library-path',lib,py,'-B','-u','-B',str(script)]", "expected=[v['python'],'-u','-B',str(script)]"),
   ("row['exe']==loader and row['argv']==expected and row['cwd']=='/home/lc01/Zonglin Li/zonglin2'", "row['exe']==str(Path(v['python']).resolve()) and row['argv']==expected and row['cwd']==str(B)")]
  for a,b in replacements:
   assert cpu210.count(a)==1,(a,cpu210.count(a));cpu210=cpu210.replace(a,b,1)
  for_name="stdout_tail=(B/'job0/FLAT90_SOURCE_CPU.log').read_text(errors='replace')[-16000:],"
  for text_name in ('cpu','cpu210'):
   value=locals()[text_name];assert value.count(for_name)==1
  cpu=cpu.replace(for_name,for_name+"stdout_full_UTF8=(B/'job0/FLAT90_SOURCE_CPU.log').read_text(),",1)
  cpu210=cpu210.replace(for_name,for_name+"stdout_full_UTF8=(B/'job0/FLAT90_SOURCE_CPU.log').read_text(),",1)
  '''+needle
assert s.count(needle)==1;s=s.replace(needle,code,1)
needle="result=d.code(c,python,cpu,dict(root=root,manifest_SHA=sp['payload_manifest_SHA']),timeout=330)"
assert s.count(needle)==1;s=s.replace(needle,"result=d.code(c,python,cpu if alias=='h1' else cpu210,dict(root=root,manifest_SHA=sp['payload_manifest_SHA'],python=sp['python']),timeout=330)",1)
ast.parse(s)
out=N/'install_native93_two_distinct_targets_identity_V2_actual_CPU_UNUSED_once.py'
with out.open('x',encoding='utf8') as f:f.write(s)
B=N.parent/'H1_STEP270_REWARD_PATH_V1_20261022';x=(B/'same_authorized_session_compressed_transport_v254.py').read_text('utf8');a="        'install_native93_two_distinct_targets_actual_source_SDK_CPU_UNUSED_once.py',";assert x.count(a)==1;x=x.replace(a,"        '"+out.name+"',\n"+a,1);ast.parse(x)
with (B/'same_authorized_session_compressed_transport_v255.py').open('x',encoding='utf8') as f:f.write(x)
with (N/'reports/NATIVE93_SELECTED_TWO_TARGET_IDENTITY_V2_SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(prepared_only=True,original_V1_never_executed=True,actual88C_detached_node_root_is_jobroot=True,original_target72_loader_identity_preserved=True,source210_exact_native_python_argv_executable_cwd_before_CPU_wait=True,all_model_source_checks_CPU_and_wait_preserved=True,full_UTF8_CPU_log_capture_added=True,selected=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest()),f,indent=2)
print(json.dumps(dict(prepared=True,selected=out.name,transport=255)))
