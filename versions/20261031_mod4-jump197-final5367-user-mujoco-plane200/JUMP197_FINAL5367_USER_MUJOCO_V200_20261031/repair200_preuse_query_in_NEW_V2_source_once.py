"""Preserve source-preparation refusal; repair only a preuse text lookup in new V2."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;V=B.with_name(B.name+'_V2');R=B/'reports'
assert not V.exists()
old=B/'prepare200_frozen_new_capture_and_display_once.py';raw=old.read_bytes();text=raw.decode('utf8')
needle='oldquery="\'install_capture200_original_course_frozen_once|'
replacement='oldquery="\'install_capture200_final197_literal_jump_plane_once|'
assert text.count(needle)==1
new=text.replace(needle,replacement).replace("ROOT='/mnt/mod4_linux_durable_20261013/MOD4_JUMP197_FINAL5367_USER_VIEW_20261031v200'","ROOT='/mnt/mod4_linux_durable_20261013/MOD4_JUMP197_FINAL5367_USER_VIEW_20261031v200_v2'")
ast.parse(new);V.mkdir();(V/'prepare200_frozen_new_capture_and_display_once.py').write_text(new,encoding='utf8',newline='\n')
(V/'capture200_final197_literal_jump_plane_once.py').write_bytes((B/'capture200_final197_literal_jump_plane_once.py').read_bytes())
with (R/'ROOT200_V1_PREPARE_QUERY_LOOKUP_ORIGINAL_FAILURE_AND_NEW_V2_SOURCE.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),original_entry=str(old),original_OS_RC=1,
        original_error='Traceback: prepare200_frozen_new_capture_and_display_once.py line50: assert oldquery in install; AssertionError',
        cause='Install entry name had already been renamed before exact oldquery substring lookup',
        original_partial_TASK_launcher_postcopy_source_preserved=True,
        remote_or_SDK_model_raw_reads_before_failure=0,
        new_source_dir=str(V),repair='Fix only preuse exact lookup prefix and distinct unused remote namespace',
        original_source_SHA=hashlib.sha256(raw).hexdigest(),new_source_SHA=hashlib.sha256(new.encode('utf8')).hexdigest(),
        no_reward_physics_model_viewer_math_change=True,no_original_entry_replay=True),f,indent=2)
print(json.dumps(dict(prepared_new_V2=True,path=str(V),new_remote_source_unused=True)))
