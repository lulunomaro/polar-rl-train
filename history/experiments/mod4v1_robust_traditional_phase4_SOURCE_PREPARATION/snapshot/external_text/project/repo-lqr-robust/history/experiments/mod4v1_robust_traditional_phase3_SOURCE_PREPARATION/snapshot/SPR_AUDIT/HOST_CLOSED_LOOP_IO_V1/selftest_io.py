"""Software IPC roundtrip only. No MuJoCo/plant/network/CAN imports or steps."""
from pathlib import Path
import json,csv,struct,copy,traceback
from p25_stdio import P25Local,DEFAULT,SCHEMA,encode_fields,decode_reply,make_step,f32
HERE=Path(__file__).resolve().parent;V3=HERE.parent/'portable_control_v3_current'
checks=0

def check(value,message):
 global checks
 checks+=1
 if not value:raise AssertionError(message)
def vec32(a):return [f32(x) for x in a]
def dc64(tau,velocity):
 result=[]
 for i,(t,v) in enumerate(zip(tau,velocity)):
  wheel=i in [2,5];peak=5.775909774436091 if wheel else 40.;stall=28.18532894736838 if wheel else 53.3333333333333;no=55.3557 if wheel else 16.755160819145562;limit=no*(1+peak/stall);v=min(limit,max(-limit,v));lo=max(-peak,stall*(-1-v/no));hi=min(peak,stall*(1-v/no));result.append(min(hi,max(lo,t)))
 return result

def fixture(row,layout,index):
 fields=layout['offsets']
 def g(name):
  start,n=fields[name];return [float(x) for x in row[start:start+n]]
 def one(name):return g(name)[0]
 stamp=int(one('STAMP'));now=int(one('NOW'));mode=int(one('MEAN_MODE'));begin=int(one('WINDOW_BEGIN'));dq=g('DQ4');spin=g('SPIN2')
 packet={'sampled_us':stamp,'arrival_us':now,'channel_epoch_us':[stamp]*4,'sequence':int(one('SEQUENCE')),'flags':1,'coherent':1,'mean_valid':1,'mean_weights_valid':mode,'mean_mode':mode,'window_begin_us':begin,'mean_weight_sum_us':stamp-begin,'expected_count':int(one('MEAN_COUNT')),'valid_count':int(one('MEAN_COUNT')),'dropped_count':0,'gyro_body':g('GYRO'),'proper_accel_body':g('ACCEL'),'joint_q4':g('Q4'),'joint_dq4':dq,'wheel_spin2':spin}
 command={'issued_us':now,'expires_us':now+10000,'sequence':index+1,'flags':1,'enable':1,'forward_m_s':one('FORWARD'),'yaw_rad_s':one('YAW_COMMAND')}
 drive={'sampled_us':stamp,'flags':1,'velocity_row6':[dq[0],dq[1],spin[0],dq[2],dq[3],spin[1]]}
 return packet,command,drive,now

def main():
 layout=json.loads((V3/'REFERENCE_LAYOUT.json').read_text());reference=[json.loads(s) for s in (V3/'C_REPLAY_01.jsonl').read_text().splitlines()]
 with (V3/'REFERENCE_VECTORS.csv').open() as f:rows=list(csv.reader(f))[1:]
 check(len(rows)==len(reference)==3200,'fixture row count')
 exe=(HERE/'p25_host_adapter.exe').read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0];machine=struct.unpack_from('<H',exe,pe+4)[0];magic=struct.unpack_from('<H',exe,pe+24)[0]
 check(struct.calcsize('P')==8,'Python64 expected');check(exe[pe:pe+4]==b'PE\0\0' and machine==0x14c and magic==0x10b,'MinGW32 PE32 expected')
 max_guard_error=0.;max_pre_vs_guard=0.;processed=0;scenario_reports=[];client=None;last_case=None;case_count=0
 with (HERE/'ROUNDTRIP_01.jsonl').open('x',encoding='utf-8') as out:
  try:
   for index,(row,expected) in enumerate(zip(rows,reference)):
    case=expected['scenario']
    if case!=last_case:
     if client:client.close();scenario_reports.append({'case':layout['cases'][last_case]['name'],'rows':case_count})
     init=copy.deepcopy(DEFAULT);start=layout['offsets']
     init['ARM']=int(float(row[start['ARM'][0]]));init['ACC_REF']=int(float(row[start['ACCREF'][0]]));init['ACC_CORR']=float(row[start['ACC_CORR'][0]]);init['RADIUS']=float(row[start['RADIUS'][0]]);o=start['OFFSET'][0];init['OFFSET']=[float(v) for v in row[o:o+3]]
     client=P25Local(stderr_path=HERE/f'case_{case}_stderr_01.log');ack=client.initialize(init);check(ack['status']==0 and not ack['valid'],'init is not an actuation');last_case=case;case_count=0
    p,cmd,drive,now=fixture(row,layout,case_count);reply=client.step(p,cmd,drive,now)
    check(reply['status']==0 and reply['valid'],'valid roundtrip status');check(reply['ENQUEUE_DELTA']==1 and reply['DISABLE_DELTA']==0,'single enqueue')
    check(reply['STATE14']==vec32(expected['state14']),'bitwise float32 state14 mismatch row='+str(index));check(reply['MATH_TAU']==vec32(expected['tau']),'bitwise P25 tau mismatch row='+str(index));check(reply['GUARDED_WHEEL_FIRST']==[reply['GUARDED_TAU'][j] for j in [2,5,0,1,3,4]],'explicit row map')
    check(reply['NOW']==now and reply['SAMPLED']==p['sampled_us'] and reply['AGE']==now-p['sampled_us'],'timestamps/age')
    want=dc64(reply['MATH_TAU'],vec32(drive['velocity_row6']));err=max(abs(a-b) for a,b in zip(reply['GUARDED_TAU'],want));max_guard_error=max(max_guard_error,err);check(err<=.00005,'original DC double comparison')
    for i,t in enumerate(reply['GUARDED_TAU']):check(abs(t)<=f32(5.775909774436091 if i in [2,5] else 40.),'absolute peak unchanged')
    max_pre_vs_guard=max(max_pre_vs_guard,max(abs(a-b) for a,b in zip(reply['MATH_TAU'],reply['GUARDED_TAU'])));out.write(json.dumps({'fixture_row':index,'case':case,'reply':reply},allow_nan=False)+'\n');processed+=1;case_count+=1
  finally:
   if client:client.close()
 scenario_reports.append({'case':layout['cases'][last_case]['name'],'rows':case_count})
 basep,basecmd,basedrive,basenow=fixture(rows[0],layout,0);negative=[]
 def run_bad(name,operation,tokens,*,wire_sequence=None,payload_count=None,initialize=True):
  with P25Local(stderr_path=HERE/(name+'_stderr_01.log')) as c:
   if initialize:c.initialize()
   result=c.exchange_raw(operation,tokens,wire_sequence=wire_sequence,payload_count=payload_count,check=False)
   check(result['status']!=0 and result['all_payload_zero'] and not result['valid'],name+' zero fault')
   if operation!='I' or initialize:
    follow=c.exchange_raw('S',encode_fields('STEP',make_step(basep,basecmd,basedrive,basenow)),check=False);check(follow['status']==5 and follow['all_payload_zero'],name+' latched')
   negative.append({'case':name,'status':result['status'],'all_payload_zero':result['all_payload_zero']})
 step_tokens=encode_fields('STEP',make_step(basep,basecmd,basedrive,basenow))
 run_bad('bad_wire_sequence','S',step_tokens,wire_sequence=1)
 run_bad('reinitialization','I',encode_fields('INIT',DEFAULT))
 run_bad('step_before_init','S',step_tokens,initialize=False)
 bad=step_tokens.copy();bad[SCHEMA['STEP']['MEAN_VALID']['offset']]='0';run_bad('invalid_mean','S',bad)
 run_bad('unknown_operation','X',[])
 run_bad('wrong_field_count','S',step_tokens[:-1],payload_count=len(step_tokens))
 bad=step_tokens.copy();bad[SCHEMA['STEP']['GYRO']['offset']]='nan';run_bad('nonfinite_token','S',bad)
 p=copy.deepcopy(basep);cmd=copy.deepcopy(basecmd);drive=copy.deepcopy(basedrive);now=10000;p['sampled_us']=p['arrival_us']=p['window_begin_us']=now;p['channel_epoch_us']=[now]*4;p['mean_weight_sum_us']=0;p['expected_count']=p['valid_count']=1;p['mean_mode']=p['mean_weights_valid']=0;cmd['issued_us']=now;cmd['expires_us']=now+10000;drive['sampled_us']=now
 bad=encode_fields('STEP',make_step(p,cmd,drive,now,now,now-1));run_bad('logical_clock_rollback','S',bad)
 with P25Local(stderr_path=HERE/'large_u64_stderr_01.log') as c:
  c.initialize();t=(1<<53)+1024;p['sampled_us']=p['arrival_us']=p['window_begin_us']=t;p['channel_epoch_us']=[t]*4;cmd['issued_us']=t;cmd['expires_us']=t+10000;drive['sampled_us']=t
  r=c.step(p,cmd,drive,t);check(r['NOW']==t and r['SAMPLED']==t and r['ESTIMATED']==t,'exact uint64 beyond double integer precision')
 with P25Local(stderr_path=HERE/'truncated_EOF_stderr_01.log') as c:
  c.initialize();c.process.stdin.write('PC3IO 1 S 2 51 0 0');c.process.stdin.flush();c.process.stdin.close();line=c._lines.get(timeout=5);check(isinstance(line,str),'truncated EOF reply');r=decode_reply(line,2);check(r['status']==1008 and r['all_payload_zero'],'truncated EOF zero fault');code=c.process.wait(timeout=5);check(code==2,'truncated EOF terminates promptly');negative.append({'case':'truncated_EOF','status':r['status'],'all_payload_zero':True,'process_exit':code})
 report={'checks':checks,'failures':0,'fixture_rows_roundtripped':processed,'scenarios':scenario_reports,'math_state_float32_bit_mismatches':0,'math_tau_float32_bit_mismatches':0,'max_guarded_vs_original_DC64_Nm':max_guard_error,'max_pre_DC_math_minus_guarded_Nm':max_pre_vs_guard,'negative_cases':negative,'large_uint64_exact':True,'python_pointer_bits':struct.calcsize('P')*8,'executable_machine':hex(machine),'executable_optional_magic':hex(magic),'ctypes_used':False,'network_or_CAN':False,'new_physics_steps':0,'hardware_binding':False,'clock':'externally supplied logical simulation time, not measured host/ARM WCET','PH3':'pending'}
 (HERE/'SELFTEST_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'selftest_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
