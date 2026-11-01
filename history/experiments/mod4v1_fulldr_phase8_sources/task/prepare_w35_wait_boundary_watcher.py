"""One boundedmetadata watcher for the newpreGO-wait case; oldfailed watcher preserved."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;p=R/'watch_w35_resume89aca_wait_actual_boundaries.py';assert not p.exists();s=(R/'watch_w35_resume89aca_actual_boundaries.py').read_text(encoding='utf-8').replace('W35_resume89aca_adaptation_dispatch_','W35_resume89aca_wait_dispatch_').replace('deadline=time.time()+4500','deadline=time.time()+6300').replace('W35_resume89aca_first_actual_update_','W35_resume89aca_wait_first_actual_update_').replace('W35_resume89aca_exit_watch_','W35_resume89aca_wait_exit_watch_');ast.parse(s);p.write_text(s,encoding='utf-8');print(p)
