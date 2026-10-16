from pathlib import Path
import json,time,ast,copy
N=Path(__file__).resolve().parent;R=N/'reports';E=N/'curb275_final87_frozen3060_v1'
def main():
 v=json.loads((R/'ACTUAL_3060_FRESH_EXACT_DESKTOP_ROLE_SIGNATURES_0109_READONLY.json').read_bytes());expected={};publishers={'gameviewerserver.exe':'NetEase','gameviewer.exe':'NetEase','deepseek harness.exe':'DeepSeek','workbuddy.exe':'Tencent','qq.exe':'Tencent','copilotapp.exe':'Microsoft','copilotapphost.exe':'Microsoft'}
 for row in v['exact_new_desktop_roles']:
  name=row['name'];assert row['authenticode']['Status']=='Valid' and publishers[name] in row['authenticode']['Subject'];assert not any(Path(c['exe'].replace('\\','/')).name.lower().startswith(('python','kit.exe','jupyter')) for c in row['children']+row['parent_children'])
  if name in ('deepseek harness.exe','workbuddy.exe','qq.exe','copilotapp.exe'):assert '--type=gpu-process' in row['process']['argv'] and not any(a.startswith('--type=') for a in row['parent']['argv'])
  if name=='copilotapphost.exe':assert 'connect-to-browser' in row['process']['argv'] and '--browser-owned' in row['process']['argv'] and Path(row['parent']['exe'].replace('\\','/')).name.lower()=='copilotapp.exe'
  if name=='gameviewerserver.exe':assert Path(row['process']['exe'].replace('\\','/')).as_posix().casefold()=='C:/Program Files/Netease/GameViewer/bin/GameViewerServer.exe'.casefold()
  expected[name]={k:row[k] for k in ('process','parent','binary_SHA')}
 assert set(expected)==set(publishers);bad=0
 for name,row in expected.items():
  for change in ('pid','parent','hash','argv'):
   x=copy.deepcopy(row)
   if change=='pid':x['process']['pid']+=1
   elif change=='parent':x['parent']['pid']+=1
   elif change=='hash':x['binary_SHA']='0'*64
   else:x['process']['argv'].append('unexpected-worker.py')
   assert x!=row;bad+=1
 source='''"""Exact fresh signed GUI identities only; unknown compute still rejected."""
from pathlib import Path
import json
import transport_249_exact_desktop_role_stdin_fresh2233_v7 as base
PY=base.PY;ROOT='D:/MOD4_async_eval/'+Path(__file__).resolve().parent.parent.name+'/'+Path(__file__).resolve().parent.name;connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():
 base.base.ROOT=ROOT;s=base.guard_code();v=json.loads((Path(__file__).resolve().parent.parent/'reports/ACTUAL_3060_FRESH_EXACT_DESKTOP_ROLE_SIGNATURES_0109_READONLY.json').read_bytes());expected={r['name']:{k:r[k] for k in ('process','parent','binary_SHA')} for r in v['exact_new_desktop_roles']};marker="  if name=='gameviewerserver.exe':";assert s.count(marker)==1
 insert="""  if name in FRESH_EXACT_SIGNED_DESKTOP:
   import hashlib
   def identity(p):return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),parent=p.ppid())
   parent=process.parent();assert parent is not None
   actual=dict(process=identity(process),parent=identity(parent),binary_SHA=hashlib.sha256(Path(exe).read_bytes()).hexdigest())
   assert actual==FRESH_EXACT_SIGNED_DESKTOP[name], 'Fresh signed desktop identity changed; unknown compute rejected'
   desktop.append(dict(pid=pid,creation=process.create_time(),exe=exe,role='Exact current OS-signature-verified desktop graphics/remote-control/browser bridge identity; untouched; not evaluation ownership or a general executable allowlist'))
  elif name=='gameviewerserver.exe':""".replace('FRESH_EXACT_SIGNED_DESKTOP',repr(expected))
 s=s.replace(marker,insert,1);compile(s,'<fresh exact signed desktop role guard>','exec');return s
''';ast.parse(source);p=E/'transport_249_fresh_signed_desktop_exact_0112_v8.py';assert not p.exists();p.write_text(source,encoding='utf8')
 old=E/'dispatch_curb275_final87_parentguard_v8_unused_case_once.py';s=old.read_text('utf8');assert 'transport_249_exact_desktop_role_stdin_fresh2233_v7 as t' in s;s=s.replace('transport_249_exact_desktop_role_stdin_fresh2233_v7 as t','transport_249_fresh_signed_desktop_exact_0112_v8 as t');p=E/'dispatch_CURB275_final87_fresh_signed_desktop_v9_unused_once.py';assert not p.exists();p.write_text(s,encoding='utf8')
 out=dict(epoch=time.time(),passed_CPU_identity_negative_fixture_only=True,negative_cases=bad,fresh_exact_signed_reference=v['epoch'],changed_actual_roles=list(expected),old_guard_rejection_and_UTF8_reader_error_retained=True,all_unknown_compute_and_CPU_Python_Kit_and_shared_OS_lock_guards_unchanged=True,no_UI_process_binary_SDK_or_remote_runtime_mutation=True,new_native_full_owncase_still_unused_and_actual_resource_admission_required=True);p=R/'FRESH_SIGNED_EXACT_DESKTOP_GUARD_7ROLES_28NEGATIVES_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
