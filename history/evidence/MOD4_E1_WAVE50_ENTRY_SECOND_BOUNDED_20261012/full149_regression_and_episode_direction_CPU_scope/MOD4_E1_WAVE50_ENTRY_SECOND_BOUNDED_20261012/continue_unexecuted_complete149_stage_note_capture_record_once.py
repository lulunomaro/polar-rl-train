"""Continue note/capture/record not yet executed after immutable prior note-name refusal."""
from entry_second_io import *
text=(D/'archive_complete149_direction_CPU_real_stage_once.py').read_text()
text=text.replace("note=R/'ENTRY_INITIALIZATION_REPAIR_STAGE_REPORT.md'","note=R/'COMPLETE149_DIRECTION_CPU_STAGE_REPORT.md'")
old="save('COMPLETE149_DIRECTION_CPU_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))"
new="assert json.loads((R/'COMPLETE149_DIRECTION_CPU_STAGE_ARCHIVE_STARTED.json').read_bytes())['trial_id']==ID"
assert text.count(old)==1;text=text.replace(old,new)
assert not (R/'COMPLETE149_DIRECTION_CPU_STAGE_GIT_RECORDED.json').exists()
exec(compile(text,'<unexecuted-complete149-unique-note-capture-record>', 'exec'),{'__file__':str(D/'continue_unexecuted_complete149_stage_note_capture_record_once.py'),'__name__':'__main__'})
