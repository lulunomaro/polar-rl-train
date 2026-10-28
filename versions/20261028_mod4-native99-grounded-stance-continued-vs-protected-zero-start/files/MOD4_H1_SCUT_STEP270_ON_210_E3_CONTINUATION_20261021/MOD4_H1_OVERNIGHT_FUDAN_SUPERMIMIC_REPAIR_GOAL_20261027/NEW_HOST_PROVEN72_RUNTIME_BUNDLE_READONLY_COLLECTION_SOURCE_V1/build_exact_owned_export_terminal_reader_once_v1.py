"""Source only: one recorded export terminal/producer/fulltext reader."""
from pathlib import Path
import ast,hashlib,json,shlex,time
B=Path(__file__).resolve().parent;L=B.parent;old=L/'NEW_HOST_ENVIRONMENT_MIGRATION_READONLY_SOURCE_V1/read_known72_exact_missing_launcher_maps_and_license_finite_v3.py';s=old.read_text();tree=ast.parse(s);n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));literal=ast.get_source_segment(s,n.value)
receipt=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_DETACHED_STARTUP_RETURNED_ACTUAL.json';expected=json.loads(receipt.read_bytes());assert expected['supervisor']['pid']==603115 and expected['worker']['pid']==603116
code='expected='+repr(expected)+'\n'+r'''
from pathlib import Path
import hashlib,json,os,stat,time
START=time.monotonic();RUN=Path('/home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1');assert RUN.resolve()==RUN and not RUN.is_symlink()
assert json.loads((RUN/'OWN_RUNTIME_EXPORT_MARKER.json').read_bytes())['root']==str(RUN)
def read(n):
 p=RUN/n
 if not p.exists():return None
 assert p.resolve()==p and stat.S_ISREG(p.lstat().st_mode);return json.loads(p.read_bytes())
assert read('EXPORT_DETACHED_STARTUP_ACTUAL.json')['supervisor']==expected['supervisor'] and read('EXPORT_DETACHED_STARTUP_ACTUAL.json')['worker']==expected['worker']
terminal=read('EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json');ending=read('EXPORT_SUPERVISOR_EXIT_ACTUAL.json');producer=read('PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json')
boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
def known(row):
 p=Path('/proc')/str(row['pid'])
 try:raw=(p/'stat').read_text()
 except FileNotFoundError:return dict(expected=row,original_out=True,status='absent')
 f=raw[raw.rfind(')')+2:].split();creation=boot+int(f[19])/os.sysconf('SC_CLK_TCK')
 if creation!=row['creation']:return dict(expected=row,original_out=True,status='reused_PID_no_other_identity_read')
 if f[0]=='Z':return dict(expected=row,original_out=True,status='nonexecuting_zombie')
 actual=dict(pid=row['pid'],creation=creation,exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],root=os.readlink(p/'cwd'));assert actual==row
 return dict(expected=row,original_out=False,status='known_original_executing')
rows=[expected['supervisor'],expected['worker']]
if terminal:
 assert terminal['supervisor']==expected['supervisor'] and terminal['worker']==expected['worker']
 for row in terminal['recorded_tar_pigz']:
  assert row['root']==str(RUN) and row['creation']>=expected['worker']['creation'] and row['argv'][0] in ('/usr/bin/tar','/usr/bin/pigz');rows.append(row)
identities=[known(x) for x in rows];allout=all(x['original_out'] for x in identities);texts=[]
if terminal and ending and allout:
 for p in sorted(RUN.iterdir()):
  if p.suffix not in ('.json','.jsonl','.log','.txt'):continue
  a=p.lstat();assert p.resolve()==p and stat.S_ISREG(a.st_mode);raw=p.read_bytes();z=p.stat();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),stable=(a.st_size,a.st_mtime_ns)==(z.st_size,z.st_mtime_ns)))
passed=bool(terminal and terminal['passed'] and ending and ending['own_lock_released'] and allout and producer and producer['passed'] and all(x['stable'] for x in texts))
if passed:
 assert sum(x['bytes'] for x in producer['chunks'])==producer['compressed_bytes']
 for row in producer['chunks']:
  p=Path(row['path']);assert p.parent==RUN and p.name.startswith('runtime72.tar.gz.chunk') and stat.S_ISREG(p.lstat().st_mode) and p.stat().st_size==row['bytes'] and row['bytes']<=512*1024**2
print(json.dumps(dict(epoch=time.time(),scope='single known export producer admission snapshot, not repeated watcher',terminal_observed=terminal is not None and ending is not None,bundle_passed=passed,producer=producer,terminal=terminal,exit=ending,known_own_identities=identities,all_original_recorded_out=allout,full_original_texts=texts,no_archive_reread_model_GPU_signal_lockdelete_or_server_write=True,elapsed_seconds=time.monotonic()-START,env_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'),compat_inventory=dict(logical_bytes=None,partial_time_bound='not_rescanned'))))
'''
s=s.replace(literal,repr(code)).replace('KNOWN72_ENV_PORTABILITY_V3_MISSING_TEXT','PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION')
oldrun="shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -S -c '+shlex.quote(CODE)"
root='/home/lc01/Zonglin Li/zonglin2';argv=[root+'/compat/glibc240/ld-linux-x86-64.so.2','--library-path',root+'/compat/glibc240:'+root+'/envs/mod4/lib',root+'/envs/mod4/bin/python','-S','-B','-u','-c']
newrun=repr(' '.join(shlex.quote(x) for x in argv)+' ')+'+shlex.quote(CODE)';assert s.count(oldrun)==1;s=s.replace(oldrun,newrun)
s=s.replace("env_logical_bytes=v['env_inventory']['logical_bytes'],compat_logical_bytes=v['compat_inventory']['logical_bytes'],env_partial=v['env_inventory']['partial_time_bound'],compat_partial=v['compat_inventory']['partial_time_bound']","bundle_passed=v['bundle_passed'],terminal_observed=v['terminal_observed'],compressed_bytes=v['producer']['compressed_bytes'] if v['producer'] else None")
ast.parse(s);ast.parse(code);entry=B/'read_proven72_runtime_export_terminal_producer_fulltext_UNUSED_once_v1.py'
with entry.open('x',encoding='utf8') as f:f.write(s)
(B/'reports').mkdir(exist_ok=True)
proof=dict(epoch=time.time(),source_AST_passed=True,remote_AST_passed=True,original_recorded_identities_exact=True,source_code_only_no_network_or_status_query=True,source_explicit_loader_no_old_launcher_side_effect=True,one_single_snapshot_no_automatic_retry_or_loop=True,only_new_export_outputs_read=True,actual_collection_not_yet_executed=True)
with (B/'SOURCE_AST_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
with (B/'HANDOFF_FROZEN_UNUSED_EXPORT_READER_V1.md').open('x',encoding='utf8') as f:f.write('One UNUSED read_proven72_runtime_export_terminal_producer_fulltext_UNUSED_once_v1.py after globalSSH lease/freshCIM. Knownexport sup603115/create1793183927.14 andworker603116/.49, recordedtar/pigz only. Originalboundedpack1800s from1793183927.73174; execute at originalending unless concrete artifact-transfer admission requires this one earlier snapshot. No automatic loop/5minpoll/retry; if not terminal, preserve pending snapshot without calling packingfailed. Exactexplicitglibc240 loader -S bypasses source launcher mkdir/chmod; no GPU/model/archive content/hash or sourcewrites/signals. If complete, fulltext+producer/chunk metadata and allownout collected; no chunk data downloaded here. Actualtransfer requires fresh localF capacity and sourcefullSHA streaming; close72 beforesecure86ROOT-onlyreceiver.\n')
index=B/'FROZEN_UNUSED_EXPORT_PRODUCER_READER_INDEX_V1.json';files=[]
for p in sorted(B.rglob('*')):
 if p.is_file():files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),frozen_unused=True,files=files),f,indent=2)
print(json.dumps(dict(passed=True,entry=str(entry),entry_SHA=hashlib.sha256(entry.read_bytes()).hexdigest(),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest())))
