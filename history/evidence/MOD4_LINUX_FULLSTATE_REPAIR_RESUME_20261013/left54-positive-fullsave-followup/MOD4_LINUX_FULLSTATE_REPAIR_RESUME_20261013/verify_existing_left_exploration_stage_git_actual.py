"""Verify already-created objects after original TLS push failure; no record/tag/commit."""
from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;W=D.parent;R=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
tag='trial-20261014-wave50-full80-left-exploration-admitted-formal-started'
head=cap.g('rev-parse',tag+'^{}');obj=cap.g('rev-parse',tag)
assert head=='a50b09697aba74dcccb35e5f1ed322c2d73a9db2' and obj=='5a463e1b7e3473747f050f25e898f734f9f8b64f'
assert cap.g('rev-parse','HEAD')==head and not cap.g('status','--porcelain')
rows=json.loads((R/'history/evidence'/D.name/'left_exploration_full80_formal_stage/REPORT_CAPTURE_INDEX.json').read_bytes())['entries']
old=cap.a.gitio.refs();old.pop('refs/tags/'+tag,None);cap.a.verify(rows,old,head,tag,obj)
p=D/'reports/LEFT_EXPLORATION_FULL80_FORMAL_STAGE_GIT_RECORDED.json';assert not p.exists()
out=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),resumed_original_objects_after_TLS_error=True,no_re_record_tag_or_commit=True,later_receipts_require_ordinary_supplement=True)
p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
