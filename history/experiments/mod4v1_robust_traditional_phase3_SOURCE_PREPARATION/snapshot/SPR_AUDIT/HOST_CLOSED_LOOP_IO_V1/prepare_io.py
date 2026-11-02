"""Freeze read-only V3 dependencies and emit typed local ASCII schema/data."""
from pathlib import Path
import json,hashlib,ast
HERE=Path(__file__).resolve().parent;V3=HERE.parent/'portable_control_v3_current';WORK=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 assert not (HERE/'DEPENDENCY_FREEZE.json').exists()
 records={}
 for r in load(V3/'INDEX.json')['files']:
  p=V3/r['path'];assert sha(p)==r['sha256'];records[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for n in ['INDEX.json','VALIDATION.json','MANIFEST.json','index_validation_01.log']:
  p=V3/n;records[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for r in load(V3/'MANIFEST.json')['deliverables']:assert sha(V3/r['path'])==r['sha256']
 old=load(V3/'SOURCE_FREEZE.json')
 for r in old['old_sealed_snapshot']+old['sources']+old['fixed_train_inputs']:
  p=Path(r['path']);assert sha(p)==r['sha256'];records[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 dump('DEPENDENCY_FREEZE.json',{'mode':'local_host_P25_only_no_physics','read_only_files':list(records.values()),'hardware_binding':False,'PH3':'pending','PH2_scope_extended':False})
 init=[('PROFILE','u32',1),('BIND_MODE','u32',1),('BIND_MASK','u32',1),('DRIVE_MAX_AGE','u32',1),('ARM','u32',1),('ACC_REF','u32',1),('ACC_CORR','f32',1),('WHEEL_STD','f32',1),('ACC_STD','f32',1),('INNOV_LIMIT','f32',1),('MAX_RATE','f32',1),('MAX_GAP','u32',1),('MAX_AGE','u32',1),('TRACK','f32',1),('RADIUS','f32',1),('EPS','f32',1),('OFFSET','f32',3),('PINS','f32',32)]
 step=[('NOW','u64',1),('CLOCK_BEFORE','u64',1),('CLOCK_AFTER','u64',1),('SAMPLED','u64',1),('ARRIVAL','u64',1),('EPOCH','u64',4),('WINDOW_BEGIN','u64',1),('WEIGHT_SUM','u64',1),('PSEQ','u32',1),('PFLAGS','u32',1),('EXPECTED','u32',1),('VALID_COUNT','u32',1),('DROPPED','u32',1),('COHERENT','u32',1),('MEAN_VALID','u32',1),('WEIGHTS_VALID','u32',1),('MEAN_MODE','u32',1),('GYRO','f32',3),('ACCEL','f32',3),('Q4','f32',4),('DQ4','f32',4),('SPIN2','f32',2),('CMD_ISSUED','u64',1),('CMD_EXPIRES','u64',1),('CMD_SEQ','u32',1),('CMD_FLAGS','u32',1),('CMD_ENABLE','u32',1),('FORWARD','f32',1),('YAW','f32',1),('DRIVE_STAMP','u64',1),('DRIVE_FLAGS','u32',1),('DRIVE_VEL','f32',6)]
 reply=[('VALID','u32',1),('NOW','u64',1),('SAMPLED','u64',1),('ESTIMATED','u64',1),('AGE','u64',1),('EXPIRES','u64',1),('ENQUEUE_DELTA','u32',1),('DISABLE_DELTA','u32',1),('MATH_TAU','f32',6),('GUARDED_TAU','f32',6),('GUARDED_WHEEL_FIRST','f32',6),('STATE14','f32',14),('ROLL','f32',1),('LATERAL_PROXY','f32',1),('ATTITUDE_CONF','f32',1),('WHEEL_INNOV','f32',1),('CONTACT_PROXY','f32',1),('COV4','f32',4),('REF14','f32',14),('SHAPER_V','f32',1),('SHAPER_W','f32',1),('SHAPER_A','f32',1),('YAW_I','f32',1),('HEADING_PHASE','f32',1),('HEADING_TURNS','i64',1),('APERTURE','u64',1),('MEAN_COUNT','u32',1)]
 header=['#ifndef PC3_LOCAL_IO_PROTOCOL_H','#define PC3_LOCAL_IO_PROTOCOL_H','#define PCIO_VERSION 1u','#define PCIO_MAX_LINE 16384u','#define PCIO_MAX_TOKENS 256u']
 schema={'magic':'PC3IO','version':1,'request_header':['magic','version','operation I/S/Q','wire_sequence_u32','payload_count_u32'],'reply_header':['magic','version','R','wire_sequence_u32','status_i32','payload_count_u32'],'types':{'f32':'finite IEEE754 binary32 parsed from ASCII, response %.9g roundtrip','u64':'exact base10 unsigned64; never through double','u32':'exact base10 unsigned32','i64':'exact base10 signed64'},'INIT':{},'STEP':{},'REPLY':{}}
 for prefix,fields,title in [('I',init,'INIT'),('S',step,'STEP'),('R',reply,'REPLY')]:
  offset=0;all_fields=[]
  for name,kind,count in fields:
   header.append(f'#define IO_{prefix}_{name} {offset}u');schema[title][name]={'offset':offset,'type':kind,'count':count};all_fields.extend([{'name':name if count==1 else f'{name}_{j}','type':kind} for j in range(count)]);offset+=count
  header.append(f'#define PCIO_{title}_FIELDS {offset}u');schema[title+'_fields']=all_fields
 assert len(schema['INIT_fields'])==51 and len(schema['STEP_fields'])==51 and len(schema['REPLY_fields'])==71
 header+=['enum {IO_FORMAT=1001,IO_VERSION=1002,IO_OPERATION=1003,IO_COUNT=1004,IO_NUMBER=1005,IO_SEQUENCE=1006,IO_STATE=1007,IO_TRUNCATED_EOF=1008,IO_TOO_LONG=1009,IO_PROFILE=1010};','#endif']
 (HERE/'io_protocol.h').write_text('\n'.join(header)+'\n',encoding='utf-8');dump('PROTOCOL_SCHEMA.json',schema)
 values={}
 for node in ast.parse((WORK/'robot_geometry_constants_v1.py').read_text(encoding='utf-8')).body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name):values[target.id]=ast.literal_eval(node.value)
 pins=[values['PINS'][s][k][a] for s in ['left','right'] for k in ['O','K','P','A','B','C','D','W'] for a in [0,1]]
 default={'PROFILE':25,'BIND_MODE':1,'BIND_MASK':511,'DRIVE_MAX_AGE':50000,'ARM':1,'ACC_REF':1,'ACC_CORR':1.5,'WHEEL_STD':.065,'ACC_STD':.5,'INNOV_LIMIT':1.,'MAX_RATE':30.,'MAX_GAP':100000,'MAX_AGE':50000,'TRACK':values['TRACK'],'RADIUS':load(WORK/'nominal_gain_v1.json')['wheel_chart_radius_m'],'EPS':.001,'OFFSET':[.03,0,.04],'PINS':pins}
 dump('DEFAULT_INIT_P25.json',{'mode':'LOCAL_STDIO_MOCK_ONLY','hardware_binding':False,'geometry':'nominal chart values, not measured calibration','logical_clock':'explicit simulation time only; not real execution deadline measurement','fields':default})
 print(json.dumps({'dependency_files_frozen':len(records),'INIT_fields':51,'STEP_fields':51,'REPLY_fields':71,'profile':'P25','hardware_binding':False,'physics_steps':0}))
if __name__=='__main__':main()
