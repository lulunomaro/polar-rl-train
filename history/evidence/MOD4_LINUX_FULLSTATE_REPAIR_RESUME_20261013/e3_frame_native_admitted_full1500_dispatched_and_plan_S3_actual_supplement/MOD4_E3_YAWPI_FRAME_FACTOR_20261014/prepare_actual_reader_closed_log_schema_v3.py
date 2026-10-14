"""Independent finalized-log classification; preserves strict old reader errors."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;s=(D/'yawpi_actual_reader_components_v2.py').read_text()
s=s.replace('def actual_row(rows,suffix):','def actual_row(rows,suffix,allow_closed_log_flag=False):')
s=s.replace("assert x['remote_local_byteSHA_exact'] is True and not x.get('mutable_pending',False)","assert x['remote_local_byteSHA_exact'] is True and (not x.get('mutable_pending',False) or (allow_closed_log_flag and suffix=='worker.log'))")
old=" stdout=actual_row(files,'worker.log');log=Path(stdout['local_path']).read_bytes();assert all(x not in log for x in (b'Contacts have been dropped',b'buffer overflow detected',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))"
new=" stdout=actual_row(files,'worker.log',allow_closed_log_flag=True);log=Path(stdout['local_path']).read_bytes();assert b'SimulationContext cleared' in log\n assert all(x not in log for x in (b'Contacts have been dropped',b'buffer overflow detected',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))"
assert s.count(old)==1;s=s.replace(old,new);p=D/'yawpi_actual_reader_components_v3.py';assert not p.exists();p.write_text(s,encoding='utf8')
for name in ('review_yawpi_own_native_or_full_actual_CPU','review_yawpi_direct_same_WORLD_prefix_actual_CPU'):
 s=(D/(name+'_v2.py')).read_text().replace('import yawpi_actual_reader_components_v2 as m','import yawpi_actual_reader_components_v3 as m');p=D/(name+'_v3.py');assert not p.exists();p.write_text(s,encoding='utf8')
o=D/'reports/ACTUAL_READER_V3_CLOSED_LOG_SCHEMA_REPAIR_PREPARED.json';assert not o.exists();o.write_text(json.dumps(dict(epoch=time.time(),original_V2_source_and_error_retained=True,why='Collector permanently marks worker.log mutable_pending by suffix. Independent wholedata+parentEXIT0+all actual PIDs out+sharedOSlockfree+SimulationContext cleared proves closure. Allow only worker.log original suffix flag after existing actual boundary checks, still size and twohostSHA exact. Raw/query/probe/factor receipts remain nonmutable required.',no_GPU_SSH_PPO=True,Git_pending_root=True),indent=2),encoding='utf8')
