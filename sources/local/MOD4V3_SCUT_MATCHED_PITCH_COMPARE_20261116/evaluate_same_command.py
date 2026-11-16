"""Exact same command/timing/material reference alongside speed-calibrated tests."""
from pathlib import Path
import argparse,json,contextlib,time,traceback
import numpy as np
from backends import Adapter,COLUMNS
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['scut','mod4'],required=True);args=p.parse_args();A=Path(__file__).resolve().parent;O=A/'evidence'/('same_command_'+args.kind);O.mkdir(parents=True,exist_ok=False);rows=[];started=time.monotonic();adapter=Adapter(args.kind,O,materials='uniform1',contact='soft')
try:
 with(O/'backend.log').open('w',encoding='utf8')as log,contextlib.redirect_stdout(log):
  for family in ['flat','rough']:
   for height in [.28,.4]:
    for direction in [1,-1]:
     for amplitude in [1.2,2.2]:
      key=f'{family}_h{height:.2f}_dir{direction}_cmd{amplitude:.1f}';control=adapter.create(family,height,direction);trace=[]
      try:
       for k in range(250):
        trace.append(adapter.step(direction*amplitude if 100<=k<150 else 0.,0 if k<100 else 1 if k<150 else 2))
        if adapter.failed:break
       z=np.asarray(trace);np.savez_compressed(O/(key+'.npz'),trace=z);rows.append(dict(kind=args.kind,family=family,height_command=height,direction=direction,command_amplitude=amplitude,complete=not adapter.failed and len(z)==250,failure=adapter.failed,control=control,trajectory=key+'.npz'))
       (O/'RESULT.json').write_text(json.dumps(dict(complete=False,columns=COLUMNS,rows=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
      finally:adapter.close()
 (O/'RESULT.json').write_text(json.dumps(dict(complete=True,columns=COLUMNS,rows=rows,wall_seconds=time.monotonic()-started),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('SAME_COMMAND_COMPLETE',args.kind,len(rows),sum(q['complete']for q in rows),flush=True)
except Exception:
 (O/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise
