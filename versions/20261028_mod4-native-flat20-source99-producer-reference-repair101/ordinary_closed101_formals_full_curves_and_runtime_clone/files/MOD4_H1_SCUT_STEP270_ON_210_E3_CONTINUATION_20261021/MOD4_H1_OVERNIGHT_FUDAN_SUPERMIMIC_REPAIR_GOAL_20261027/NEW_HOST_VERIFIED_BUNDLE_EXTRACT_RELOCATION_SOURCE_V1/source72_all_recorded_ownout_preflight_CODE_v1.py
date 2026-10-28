"""CODE only. Future source72 read-only preflight; never connects on import."""
CODE=r'''
from pathlib import Path
import hashlib,json,os,time
E=Path('/home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1');S=E/'direct_https_data_v1'
assert E.resolve()==E and S.resolve()==S
producer=json.loads((E/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').read_bytes());pack=json.loads((E/'EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());release=json.loads((E/'EXPORT_SUPERVISOR_EXIT_ACTUAL.json').read_bytes())
assert producer==v['producer'] and producer['producer_SHA']=='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
assert pack['passed'] and pack['actual_child_waited'] and pack['returncode']==0 and pack['all_recorded_own_children_out'] and release['own_lock_released']
service=json.loads((S/'TLS_DATA_SERVICE_TERMINAL_ACTUAL.json').read_bytes());assert service==v['source_service_terminal'] and service['listener_closed']
endpoint=json.loads((S/'TLS_DATA_SERVICE_PUBLIC_ENDPOINT_ACTUAL.json').read_bytes());assert endpoint['identity']==service['identity'] and endpoint['producer_SHA']==producer['producer_SHA']
scope_raw=(E/'PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json').read_bytes();scope=json.loads(scope_raw)
def own_out(row):
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return dict(expected=row,out=True,reason='known original PID absent')
 if creation!=row['creation']:return dict(expected=row,out=True,reason='PID reused; no new exe/argv inspected')
 return dict(expected=row,out=a[0]=='Z',reason='known original nonexecuting zombie' if a[0]=='Z' else 'known original still executing',state=a[0],creation=creation)
known=[pack['supervisor'],pack['worker']]+pack['recorded_tar_pigz']+[service['identity']];rows=[own_out(x) for x in known];passed=all(x['out'] for x in rows)
print(json.dumps(dict(kind='MOD4_PROVEN72_EXPORT_AND_TLS_SOURCE_ALL_OWNOUT_ACTUAL_V1',epoch=time.time(),passed=passed,all_known_recorded_out=passed,known_only=rows,producer_SHA=producer['producer_SHA'],caller_receipt_SHA=v['caller_receipt_SHA'],source_service_terminal=service,pack_terminal=pack,logical_input_bytes=scope['logical_input_bytes'],input_scope_SHA=hashlib.sha256(scope_raw).hexdigest(),no_archive_content_model_GPU_signal_or_source_write=True)))
'''
