"""Only own H1 complete-update storage/time engineering bound; no learning input changes."""
import math
H1_MAX_COMPLETE_UPDATES=24
H1_EXIT_STORAGE_RESERVE_BYTES=8*1024**3
def should_save_stop(phase,completed,free_bytes):
 if phase not in ('production','precheck128','precheck20k') or not isinstance(completed,int) or completed<0 or not isinstance(free_bytes,(int,float)) or not math.isfinite(free_bytes) or free_bytes<0:raise ValueError('Unknown/invalid own finite storage state')
 return phase=='production' and (completed>=H1_MAX_COMPLETE_UPDATES or free_bytes<H1_EXIT_STORAGE_RESERVE_BYTES)
