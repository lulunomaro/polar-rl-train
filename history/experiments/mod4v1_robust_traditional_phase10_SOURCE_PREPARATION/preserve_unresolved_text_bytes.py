"""Append exact already-admitted small C source bytes, without guessing a charset.
No original report edit, asset/lib/object read, SDK/compile/Git, or source-root write.
"""
from pathlib import Path
import hashlib,json,sys,datetime,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def new(p,x):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 dest=P/'UNRESOLVED_TEXT_BYTE_PRESERVATION.json';assert not dest.exists(),'No replay'
 mf=json.loads((P/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
 targets=[e for e in mf['entries']if e['kind']=='undecodable_metadata_only']
 expected_by_name={'cmsis_os.c':(53434,'d42eb9080c54e8ec9b2cd5cb1d8ccc5a7b29fada172065ccbe019cbe09b7e366'),'cmsis_os.h':(53065,'51420495a86c8aea829f63a156c475c225bf9c51429e0bb210eb35db0b1fd1ba')}
 assert sorted(Path(e['path']).name for e in targets)==['cmsis_os.c','cmsis_os.c','cmsis_os.h']
 assert all((e['bytes'],e['observed_source_SHA_before'])==expected_by_name[Path(e['path']).name]for e in targets)
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 rows=[]
 for e in targets:
  src=Path(e['path']);st=src.stat();raw=src.read_bytes();after=src.stat()
  expected=e['observed_source_SHA_before'];actual=sha(raw)
  assert actual==expected==expected_by_name[src.name][1]
  assert (st.st_size,st.st_mtime_ns)==(after.st_size,after.st_mtime_ns)==(e['bytes'],e['mtime_ns'])
  # One-byte view only for ASCII credential detection, not a charset claim or transcode.
  clean,removed=redact(raw.decode('latin1'));assert removed==0 and clean.encode('latin1')==raw
  out=P/'exact_small_source_bytes'/e['source_relative'];out.parent.mkdir(parents=True,exist_ok=True)
  with out.open('xb')as f:f.write(raw)
  assert sha(out.read_bytes())==actual
  rows.append({'path':str(src),'source_relative':e['source_relative'],'bytes':len(raw),'SHA':actual,
   'source_SHA_before':expected,'source_SHA_after':actual,'snapshot_path':out.relative_to(WT).as_posix(),
   'snapshot_SHA':actual,'original_manifest_entry_retained':True,'encoding':'UNRESOLVED_NOT_TRANSCODED',
   'credential_scan':'latin1_byte_view_for_ASCII_only_not_source_charset','redactions':0,
   'classification':'already_admitted_small_C_text_exact_bytes_not_library_asset_or_raw_trace'})
 new(dest,{'status':'APPEND_ONLY_EXACT_SMALL_C_SOURCE_BYTES_PRESERVED_NO_CHARSET_GUESS',
  'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,
  'initial_manifest_and_decode_events_unchanged':True,'sourceRoot_modified':False,
  'small_source_reads':len(rows),'new_raw_asset_lib_obj_ZIP_reads_or_hashes':0,'Git_SDK_compile_PHY_QA_calls':0})
 print(json.dumps({'status':'EXACT_SMALL_SOURCE_BYTES_PRESERVED','sources':len(rows),'bytes_total':sum(x['bytes']for x in rows),'SHA_records':[{k:x[k]for k in ('source_relative','bytes','SHA')}for x in rows]},ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  err=traceback.format_exc();n=1
  while (P/f'ENCODING_PRESERVATION_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'ENCODING_PRESERVATION_FAILURE_{n:03d}.txt').write_text(err,encoding='utf-8')
  (P/f'ENCODING_PRESERVATION_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes())
  raise
