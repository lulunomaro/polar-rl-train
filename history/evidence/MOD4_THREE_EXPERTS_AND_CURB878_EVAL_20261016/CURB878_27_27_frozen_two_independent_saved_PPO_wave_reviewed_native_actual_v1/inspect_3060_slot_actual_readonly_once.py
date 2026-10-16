from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as t
def main():
 p=R/'ACTUAL_3060_RESOURCE_SLOT_BEFORE_NEW_CURB878_NATIVE.json';assert not p.exists();t.ROOT='D:/MOD4_async_eval/'+D.name;c=None
 try:c=t.connect();v=t.py(c,t.guard_code(),60)
 finally:t.close(c)
 p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('ACTUAL_3060_RESOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_launch_or_process_action=True),indent=2));raise
