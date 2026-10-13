from pathlib import Path
import json,time,hashlib,shutil
D=Path(__file__).resolve().parent;OLD=D.parent/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013';R=D/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=D/'read_local_continue_actual.py';assert not p.exists();text=(OLD/'read_local_training_actual.py').read_text(encoding='utf8');assert text.count('temporary_train128_v10_sameidentity_saved_source')==1;text=text.replace('temporary_train128_v10_sameidentity_saved_source','same128_continue_second7200_v1').replace("D/'LOCAL_GPU_EXCLUSIVE.lock'","Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock')");compile(text,str(p),'exec');p.write_text(text,encoding='utf8')
 rows=[]
 for original in sorted((OLD/'runtime').rglob('*')):
  if not original.is_file() or '__pycache__' in original.parts:continue
  copied=D/'runtime'/original.relative_to(OLD/'runtime');assert copied.is_file() and H(original)==H(copied);rows.append(dict(old_path=str(original),path=str(copied),bytes=copied.stat().st_size,sha256=H(copied)))
 p=R/'LOCAL_CONTINUE_RUNTIME_OLD_ALL_BYTE_SHA_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,files=rows,actual_after_dispatch_source_comparison=True,no_running_source_mutation=True,assets_and_geometry_original_exact=True),indent=2),encoding='utf8')
 original=D.parent/'prepare_local128_continue_20261013_once.py';p=D/'original_prepare_source_actual.py';assert not p.exists();shutil.copy2(original,p)
 print(json.dumps(dict(passed=True,readonly_observer_prepared=True,runtime_all_old_bytes_exact=len(rows),producer_actual_SHA=H(p))))
if __name__=='__main__':main()
