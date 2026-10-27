from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=HERE/'PRIVATE_PHASE_FRAME_FROZEN_INDEX_V1.json';assert not out.exists()
 original=json.loads((HERE/'INDEX.json').read_bytes())
 names=['private_phase_frame_v1.py','check_private_phase_frame_tiny_CPU_once_v1.py','PRIVATE_PHASE_FRAME_TINY_CPU_ACTUAL_V1.json',
  'freeze_private_frame_source_once_v1.py','HANDOFF.md','INDEX.json','PRIVATE_FRAME_SCOPE_HANDOFF.md',Path(__file__).name]
 rows=[dict(relative=n,bytes=(HERE/n).stat().st_size,SHA=H(HERE/n)) for n in names]
 foreign=[r for r in original['files'] if r['relative']=='native_flat_jump_adapter_v1.py'];assert len(foreign)==1
 with out.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),schema='mod4.flat.private_frame.only.source_frozen.v1',
  files=rows,only_explicit_private_frame_files_frozen=True,whole_shared_folder_frozen=False,root_native_adapter_mutable_and_excluded=True,
  original_mixed_index_scope_error_preserved=True,foreign_file_historical_snapshot_only=foreign,
  foreign_current_bytes_not_reread=True,actual_runtime_integration_pending=True,Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(private_scope_index_SHA=H(out),private_source_SHA=H(HERE/'private_phase_frame_v1.py'),files=len(rows),root_adapter_not_frozen=True)))
if __name__=='__main__':main()
