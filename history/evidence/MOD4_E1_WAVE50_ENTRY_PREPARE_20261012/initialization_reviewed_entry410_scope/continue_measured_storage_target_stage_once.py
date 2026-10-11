"""Preserve the 8GiB rejection; size new short-scope storage against actual prior output."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'continue_verified_predecessor_target_stage_once.py').read_text()
anchor="s=s.replace('previous.m.','previous.prior.')"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''\ns=s.replace("assert mem>8*1024**3 and disk.free>8*1024**3 and not D.exists()", "prior_bytes=sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file());required_free=2*prior_bytes+2*1024**3;assert mem>8*1024**3 and disk.free>required_free and not D.exists(),dict(actual_free=disk.free,prior_bytes=prior_bytes,required_free=required_free)")\ns=s.replace("disk_free_bytes=disk.free)","disk_free_bytes=disk.free,prior_full_scope_actual_bytes=prior_bytes,new_short_scope_storage_required_bytes=required_free,original8GiB_rejection_preserved=True,no_evidence_or_cache_deletion=True)")''')
exec(compile(s,'<measured-storage-unexecuted-target-stage>','exec'),{'__file__':str(D/'continue_verified_predecessor_target_stage_once.py'),'__name__':'__main__'})
