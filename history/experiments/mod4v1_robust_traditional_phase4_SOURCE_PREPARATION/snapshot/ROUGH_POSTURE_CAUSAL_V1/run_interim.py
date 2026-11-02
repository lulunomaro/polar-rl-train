from pathlib import Path
import hashlib,traceback,json,sys
R=Path(__file__).resolve().parent;n=1
while (R/'attempts'/f'{n:03d}').exists():n+=1
out=R/'attempts'/f'{n:03d}';out.mkdir(parents=True);raw=(R/'interim.py').read_bytes();(out/'interim_source.py').write_bytes(raw);(out/'SOURCE_SHA.json').write_text(json.dumps({'SHA':hashlib.sha256(raw).hexdigest(),'no_newphysics':True})+'\n',encoding='utf-8');sys.path.insert(0,str(R))
try:
 import interim
 interim.main()
except Exception:
 (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
