"""Select old replay arrays only with adjacent closed producer reports; no deletion."""
from pathlib import Path
import collections,hashlib,json,re,stat,time,traceback,zipfile,zlib
W=Path('C:/Users/lulu/Desktop/claude/mjcf').resolve();B=Path(__file__).resolve().parent;R=B/'reports'
H=lambda data:hashlib.sha256(data).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def records(value):
 if isinstance(value,dict):
  if any(k in value for k in ('path','file')) and any(k in value for k in ('SHA','sha256','sha')):yield value
  for x in value.values():yield from records(x)
 elif isinstance(value,list):
  for x in value:yield from records(x)
def main():
 inv=json.loads((R/'WORKSPACE_SIZE_AND_LARGE_TRAINING_ARTIFACT_INVENTORY_ACTUAL.json').read_bytes());selected=[];excluded=[];report_sources={};bycat=collections.defaultdict(lambda:dict(files=0,bytes=0))
 candidates=[x for x in inv['large_files'] if Path(x['path']).name in ('retention_full_control_substep_actual.npz','route_raw.npz')]
 for row in candidates:
  p=Path(row['path']);rel=p.relative_to(W);top=rel.parts[0];date=re.search(r'_(2026\d{4})(?:$|_)',top)
  if not top.startswith('MOD4_') or not date or int(date.group(1))>=20261019 or any(part.lower() in ('runtime','payload','source','source_snapshot','.venv','site-packages') for part in rel.parts):excluded.append(dict(path=str(p),reason='protected recent source/runtime or unqualified scope'));continue
  complete=p.parent/'COMPLETE_ACTUAL.json';probe=p.parent/'probe.json'
  if not complete.is_file() or not probe.is_file():excluded.append(dict(path=str(p),reason='no adjacent complete/probe proof'));continue
  raw=complete.read_bytes();v=json.loads(raw);matches=[]
  for r in records(v):
   name=str(r.get('path',r.get('file',''))).replace('\\','/').split('/')[-1];sha=r.get('SHA',r.get('sha256',r.get('sha')));size=r.get('bytes',r.get('size'))
   if name==p.name and size==row['bytes'] and isinstance(sha,str) and re.fullmatch('[0-9a-fA-F]{64}',sha):matches.append(r)
  if len(matches)!=1:excluded.append(dict(path=str(p),reason='producer SHA/size/path not uniquely bound'));continue
  # Complete data-contract result is retained verbatim, including failure/false outcomes.
  if 'passed_data_contract' not in v:excluded.append(dict(path=str(p),reason='not the closed replay data contract schema'));continue
  s=p.stat();assert s.st_size==row['bytes'] and s.st_mtime_ns==row['mtime_ns'];assert not (getattr(s,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT)
  entry=dict(row,category='old_closed_frozen_replay_array',producer=matches[0],producer_report=str(complete),producer_report_SHA=H(raw),numerical_summary=str(probe),numerical_summary_SHA=H(probe.read_bytes()),original_case_id=v.get('case_id'),checkpoint_SHA=v.get('checkpoint_sha256'),original_passed_data_contract=v['passed_data_contract'],not_a_new_success_or_reclassification=True,remote_original_retention_not_queried_or_claimed=True,approved_by_current_user_workspace_cleanup=True)
  selected.append(entry);bycat[entry['category']]['files']+=1;bycat[entry['category']]['bytes']+=row['bytes']
  for q in (complete,probe):report_sources[str(q)]=dict(path=str(q),bytes=q.stat().st_size,SHA=H(q.read_bytes()))
 # A redundant transport zip is removable only after every archived member exactly
 # matches the still-kept extracted wheel file (size and ZIP CRC32).
 zip_path=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr/TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013.zip';folder=zip_path.with_suffix('');members=[]
 if zip_path.is_file() and folder.is_dir():
  with zipfile.ZipFile(zip_path) as z:
   for info in z.infolist():
    if info.is_dir():continue
    dest=folder/info.filename;assert dest.resolve().is_relative_to(folder.resolve())
    if not dest.is_file():
     # Some producers include the directory name in the zip.
     dest=folder.parent/info.filename
    assert dest.resolve().is_relative_to(folder.resolve()) and dest.is_file() and dest.stat().st_size==info.file_size
    crc=0
    with dest.open('rb') as f:
     while block:=f.read(8*1024**2):crc=zlib.crc32(block,crc)
    assert crc&0xffffffff==info.CRC
    members.append(dict(kept_file=str(dest),bytes=info.file_size,ZIP_CRC32=format(info.CRC,'08x')))
  assert members;s=zip_path.stat();entry=dict(path=str(zip_path),relative=zip_path.relative_to(W).as_posix(),bytes=s.st_size,mtime_ns=s.st_mtime_ns,category='redundant_zip_all_extracted_members_verified',all_extracted_members=members,kept_extracted_folder=str(folder),original_zip_SHA=None,SHA_status='not rehashed; exact extracted member size/CRC verified',approved_by_current_user_workspace_cleanup=True);selected.append(entry);bycat[entry['category']]['files']+=1;bycat[entry['category']]['bytes']+=s.st_size
 plan=dict(epoch=time.time(),workspace=str(W),human_request='本机存储了大量无用训练残废数据你清理一下，注意只清理工作区的',scope='Only enumerated old closed replay NPZ arrays (stage dates<=20261018) and one verified redundant ZIP, no recursive directory deletion.',selected=selected,excluded=excluded,producer_reports_and_summaries_retained=list(report_sources.values()),categories=bycat,total_files=len(selected),total_logical_bytes=sum(x['bytes'] for x in selected),protected=['polar-rl-train including Git history and staging','all text reports/source/errors/indexes','all complete/source/preupdate checkpoint PT files','all 20261019 and 20261020 stages including active E3 source and closing helpers','MOD4_RESET_COLLISION_BANK.npz and all runtime/assets/SDK/env/terrain/CAD','MOD4_LOCAL_MUJOCO_DRIVE_20261008 and all local player files','workspace-external files and reparse targets','permission-denied paths (no permission changes)'],no_remote_or_training_or_account_write=True,deletion_not_yet_executed=True)
 put('EXACT_WORKSPACE_OBSOLETE_REPLAY_AND_REDUNDANT_ZIP_CLEANUP_PLAN_ACTUAL.json',plan);print(json.dumps(dict(selected_files=len(selected),logical_GiB=plan['total_logical_bytes']/1024**3,categories=bycat,excluded=len(excluded),retained_report_count=len(report_sources),verified_extracted_zip_members=len(members))))
if __name__=='__main__':
 try:main()
 except BaseException:put('CLEANUP_PLAN_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),nothing_deleted=True));raise
