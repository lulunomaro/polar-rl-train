from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;p=D/'stage_slope_snapshot_full_receipts_once.py';assert not p.exists()
s=(D/'stage_slope_snapshot_actual_receipts_once.py').read_text().replace('SNAPSHOT_ACTUAL_RECEIPTS_','SNAPSHOT_FULL_RECEIPTS_')
assert 'assert len(startup)==7' in s;s=s.replace('assert len(startup)==7','assert len(startup)==8 and "SENSOR_RESUME_STARTUP_VERIFIED.json" in startup')
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/SNAPSHOT_RECEIPT_COUNT_READER_REVIEW.json').write_text(json.dumps(dict(epoch=time.time(),original_count_assertion_rejection_preserved=True,large_sensor_receipt_omitted_from_old_bounded_reader=True,actual_remote_full_inventory_eight_receipts=True,old_stage_no_remote_newroot_or_GPU_write=True),indent=2))
