"""New fixed data fixtures only: saved C3 facts, algebraic vectors, old H15. No SDK."""
from pathlib import Path
import json,csv,hashlib,random,struct,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def cf(v):return float(f32(v)).hex()+'f'
def vec(a):return '{'+','.join(cf(x)for x in a)+'}'
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 rev=HERE/'revisions/reference_attempt_01';rev.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),rev/Path(__file__).name)
 layout=json.loads((ROOT/'SPR_AUDIT/portable_control_v3_current/REFERENCE_LAYOUT.json').read_text())['offsets']
 with(ROOT/'SPR_AUDIT/portable_control_v3_current/REFERENCE_VECTORS.csv').open()as f:rows=list(csv.reader(f))[1:]
 c3=[json.loads(s)for s in (ROOT/'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/ROUNDTRIP_01.jsonl').read_text().splitlines()];assert len(c3)==len(rows)==3200
 fixtures=[];previous=None
 for k,(r,line)in enumerate(zip(c3,rows)):
  b=r['reply'];assert b['valid']and b['VALID']==1
  def group(n):i,count=layout[n];return [f32(float(s))for s in line[i:i+count]]
  dq=group('DQ4');sp=group('SPIN2');drive=[dq[0],dq[1],sp[0],dq[2],dq[3],sp[1]]
  fixtures.append(dict(name='saved_C3_'+str(k),family='saved_C3',reset=int(previous!=r['case']),case=r['case'],valid=1,enabled=1,state=b['STATE14'],reference=b['REF14'],math_tau=b['MATH_TAU'],guarded=b['GUARDED_TAU'],drive=drive,shaper=b['SHAPER_V'],epoch=b['SAMPLED'],start_ns=0,initial_last_u=0.,initial_warm=[0.]*15))
  previous=r['case']
 rng=random.Random(20261102);eq=[f32(x)for x in json.loads((HERE/'MODEL_EXPORT.json').read_text())['arrays']['nm1_eq']]
 for k in range(512):
  # Explicit independent numerical tuples, not a new P25/robot trajectory.
  x=eq.copy();ref=eq.copy()
  for i in range(14):x[i]=f32(x[i]+rng.uniform(-1,1)*(.15 if i<7 else .5));ref[i]=f32(ref[i]+rng.uniform(-1,1)*(.1 if i<7 else .2))
  x[8]=f32(rng.uniform(-1.9,1.9));x[2]=f32(rng.uniform(-.24,.24))
  mt=[f32(v)for v in fixtures[k%3200]['math_tau']];guard=fixtures[k%3200]['guarded'];drive=[0.]*6;drive[2]=f32(rng.uniform(-80,80));drive[5]=f32(rng.uniform(-80,80))
  fixtures.append(dict(name='independent_algebra_'+str(k),family='independent_algebra',reset=1,case=100+k,valid=1,enabled=1,state=x,reference=ref,math_tau=mt,guarded=guard,drive=drive,shaper=f32(rng.uniform(-1.5,1.5)),epoch=123,start_ns=0,initial_last_u=rng.uniform(-2,2),initial_warm=[f32(rng.uniform(-1,1))for _ in range(15)]))
 # All valid source paths, fixed inputs; invalid typed paths are native unit tests.
 base=fixtures[0]
 import copy
 for name,changes in [('invalid_base',{'valid':0}),('disabled',{'enabled':0}),('domain_yaw',{'state':dict(index=8,value=2.01)}),('domain_pitch',{'state':dict(index=2,value=.251)}),('overspeed_opposed',{'drive':[0.,0.,100.,0.,0.,-100.]})]:
  a=copy.deepcopy(base);a.update(name=name,family='branch_fixture',reset=1,case=1000+len(fixtures),initial_warm=[0.]*15)
  for n,v in changes.items():
   if isinstance(v,dict):a[n][v['index']]=f32(v['value'])
   else:a[n]=v
  fixtures.append(a)
 header='/* Fixed inputs only, no oracle or simulator. */\n#include "nm1_supervisor.h"\n'
 header+='typedef struct {nm1_input input;unsigned reset;double initial_last_u;float initial_warm[15];} nm1_fixture;\n'
 header+=f'#define NM1_FIXTURE_COUNT {len(fixtures)}u\nstatic const nm1_fixture nm1_fixtures[NM1_FIXTURE_COUNT]={{\n'
 for a in fixtures:
  arrays=','.join(vec(a[n])for n in ['state','reference','math_tau','guarded','drive'])
  header+='{{'+arrays+','+cf(a['shaper'])+f',UINT64_C({a["epoch"]}),UINT64_C({a["epoch"]}),UINT64_C({a["start_ns"]}),{a["valid"]},{a["enabled"]}'+'},'+str(a['reset'])+','+float(a['initial_last_u']).hex()+','+vec(a['initial_warm'])+'},\n'
 header+='};\n'
 problems=json.loads((ROOT/'SPR_AUDIT/ACTIVE_BOX_QP_V3/PROBLEMS.json').read_text())['cases'];real=[x for x in problems if x['family']=='real_H15'];assert len(real)==18
 header+='typedef struct {float f[15],lo[15],hi[15],warm[15];} nm1_old_case;\nstatic const nm1_old_case nm1_old_cases[18]={\n'+''.join('{'+','.join(vec(a[n])for n in ['f','lo','hi','warm'])+'},\n'for a in real)+'};\n'
 (HERE/'nm1_fixtures.h').write_text(header,encoding='utf-8')
 with(HERE/'REFERENCE_INPUTS.jsonl').open('x',encoding='utf-8')as f:
  for a in fixtures:f.write(json.dumps(a,allow_nan=False)+'\n')
 dump('REFERENCE_GENERATION.json',dict(rows=len(fixtures),saved_C3=3200,independent_algebra=512,branch_fixtures=5,old_H15_cases=18,source_only_no_SDK=True,independent_algebra_not_controller_or_robot_trajectory=True,warm_seed_random_is_not_closed_loop_warm=True,new_physics_steps=0))
 print(json.dumps(dict(rows=len(fixtures),saved_C3=3200,raw_H15_cold_warm=36,status='NEW_REFERENCE_INPUTS_READY')))
if __name__=='__main__':main()
