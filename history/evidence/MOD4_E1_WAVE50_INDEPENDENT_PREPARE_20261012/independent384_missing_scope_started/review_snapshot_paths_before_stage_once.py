from wave50_io import *
import shutil,ast
P=D/'payload';C=P/'isaac/mod4'
old=D/'local_preCPU_snapshot_list_original';assert not old.exists();old.mkdir()
paths=[C/'train_wave50_full_resume_ppo.py',C/'train_wave50_fresh_preflight_ppo.py']
rows=[]
for p in paths:
 raw=p.read_bytes();shutil.copy2(p,old/p.name);t=raw.decode()
 # The guard lives at the controller root and is in the complete E1 source freeze;
 # src_snapshot lists only module-directory files. Preserve the rejected original list.
 bad="'g4_sdk_placement.py','wave50_fullscope_source_guard.py'"
 if bad in t:t=t.replace(bad,"'g4_sdk_placement.py'")
 ast.parse(t);p.write_text(t,encoding='utf8');rows.append(dict(path=str(p),original_SHA=H(raw),reviewed_SHA=H(p.read_bytes()),root_guard_still_in_full_source_map=True))
save('SNAPSHOT_FILENAME_PRECPU_REVIEW.json',dict(epoch=time.time(),original_list_missing_module_directory_guard_rejected=True,original_lists_preserved=str(old),rows=rows,before_target_CPU_GPU_or_root_deployment=True,no_old_source_hotpatch=True))
print(json.dumps(dict(reviewed=True,old_originals_preserved=True)))
