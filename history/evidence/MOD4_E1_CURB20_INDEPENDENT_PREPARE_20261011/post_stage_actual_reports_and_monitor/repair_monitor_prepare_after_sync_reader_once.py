"""Continue only unexecuted monitor preparation after actual sync receipt exists."""
from curb_io import *
import ast

def main():
    old=D/'prepare_curb_complete_native_monitor_once.py'
    text=old.read_text(encoding='utf8')
    line="prior=a['prompt'];old=R/'MONITOR_PREVIOUS_CURB132_PENDING_ACTUAL_PROMPT.md';assert not old.exists();old.write_bytes(prior.encode())"
    replacement="prior=a['prompt'];old=R/'MONITOR_PREVIOUS_CURB132_PENDING_ACTUAL_PROMPT.md';assert old.read_bytes()==prior.encode()"
    assert text.count(line)==1 and (R/'CURB132_COMPLETE_NATIVE_METADATA_SYNCED.json').is_file()
    path=D/'prepare_curb_native_monitor_after_sync_review_once.py';assert not path.exists()
    text=text.replace(line,replacement);ast.parse(text);path.write_text(text,encoding='utf8')
    save('CURB_MONITOR_PREPARE_SYNC_RECEIPT_PENDING_READER_ERROR.json',dict(epoch=time.time(),trial_id='E1-CURB20-MONITOR-PENDING-READER-06',
        original_source=str(old.resolve()),original_source_SHA=H(old.read_bytes()),error='FileNotFoundError: CURB132_COMPLETE_NATIVE_METADATA_SYNCED.json',
        source_of_error='Local monitor preparation was invoked while the genuine metadata sync process was still completing; it stopped at read before creating new prompt or modifying automation.',
        original_prior_prompt_file_preserved=True,actual_sync_now_complete=True,repair_source=str(path.resolve()),no_old_prepare_or_sync_replay=True,not_a_GPU_or_physics_failure=True))
    print(str(path))
if __name__=='__main__':main()
