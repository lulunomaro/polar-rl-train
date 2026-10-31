from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;R=N/'reports'
with (R/'ARCHIVE195_V1_ORIGINAL_BACKUP_SOURCE_SUFFIX_REJECTION.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_error='AssertionError at archive195_E0_start_source_ordinary194_once.py line29: known Python source backup tui_rescue.py.bak-20260929-2315-pre-metrics not in suffix whitelist',
  scope='Archive reader refused before staging/commit/push; own partial pack preserved',
  source_backup_names=['tui_rescue.py.bak-20260929-2315-pre-metrics','tui_rescue.py.before_speed','tui_rich.py.bak-20260929-2315-pre-metrics','validate_rescue.py.bak_20260929_162905_pre_window_gate','validate_rescue.py.bak_20260929_164139_pre_failcounts','validate_rescue.py.before_reboot_audit_20260929'],
  original_source_or_training_modified=False,models_raw_or_GPU_read=False,
  repair='Distinct V2 accepts these known Python backup source names; resumes only this own untracked archive dir, existing files must match exactly'),f,indent=2)
s=(N/'archive195_E0_start_source_ordinary194_once.py').read_text('utf8')
s=s.replace("assert not git('status','--porcelain') and not D.exists()", "status=git('status','--porcelain');prefix='?? '+D.relative_to(G).as_posix()+'/'\nassert not status or all(line==prefix for line in status.splitlines())\nassert not git('diff','--cached','--name-only') and D.is_dir() and not (D/'CAPTURE_INDEX.json').exists()")
s=s.replace("ARCHIVE195_SOURCE_ONLY_ORDINARY194_ONCE_CONSUMED.json","ARCHIVE195_SOURCE_ONLY_ORDINARY194_V2_ONCE_CONSUMED.json")
s=s.replace("D.mkdir();rows=[];selected=[]","D.mkdir(exist_ok=True);rows=[];selected=[]")
s=s.replace("assert p.suffix in ('.py','.json','.txt','.md','.xml','.sh'),str(p)","assert p.suffix in ('.py','.json','.txt','.md','.xml','.sh') or '.py.' in p.name,str(p)")
s=s.replace("dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)","dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True)\n if dest.exists():assert dest.read_bytes()==raw,'Original partial source changed '+str(dest)\n else:dest.write_bytes(raw)")
with (N/'archive195_E0_start_source_ordinary194_V2_once.py').open('x',encoding='utf8') as f:f.write(s)
print(json.dumps(dict(prepared=True,original_pack_preserved=True,no_training_or_budget_or_model_work=True)))
