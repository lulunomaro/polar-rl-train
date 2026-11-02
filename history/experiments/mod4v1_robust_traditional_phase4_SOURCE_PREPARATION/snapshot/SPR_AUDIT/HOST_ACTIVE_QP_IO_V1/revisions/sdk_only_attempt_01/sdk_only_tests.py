"""Only encoding/decoder/lifecycle evidence. Production QP I/O remains UNTESTED."""
from pathlib import Path
import ast,hashlib,json,os,struct,sys,time,traceback
import active_qp_stdio as api
HERE=Path(__file__).resolve().parent;SEALED=HERE.parent/'ACTIVE_BOX_QP_V3'
checks=0;failures=[];ledger=[]
def check(condition,label):
 global checks
 checks+=1
 if not condition:failures.append(label)
def expect_error(label,function,kinds=(Exception,)):
 try:function()
 except kinds as error:check(True,label);ledger.append({'name':label,'expected_error':type(error).__name__,'message':str(error)})
 else:check(False,label+' did not fail')
def bits(value):return struct.pack('<f',value)
def reply(status=0,**changes):
 values={r['name']:0 for r in api.SCHEMA['reply_fields']};values.update(status=status,valid=int(status==0),fatal=int(status in api.FATAL_SOLVER or status>=1000),request_n=1,result_n=int(status==0),diagnostic_valid=int(status==0));values.update(changes)
 tokens=[format(values[r['name']],'.9g') if r['type']=='f32' else str(values[r['name']]) for r in api.SCHEMA['reply_fields']]
 return 'ABQPIO 1 '+('E' if status>=1000 else 'R')+' 1 42 '+' '.join(tokens)+'\n'
def main():
 ast.parse((HERE/'active_qp_stdio.py').read_text());check(struct.calcsize('P')==8,'Python64');boot='ABQPIO 1 B 0 8 16 32 64 24 QPC RN_NO_FTZ_DAZ '+api.SCHEMA['core_sha256']+' '+api.SCHEMA['header_sha256']+'\n';check(api.decode_boot(boot)['clock_source']=='QPC','boot real QPC')
 for label,line in [('test_clock_not_prod',boot.replace('QPC','TEST_LOGICAL')),('wrong_bitness',boot.replace('16 32 64','16 64 64')),('wrong_source',boot.replace(api.SCHEMA['core_sha256'],'0'*64)),('truncated_boot',boot[:-1])]:expect_error(label,lambda line=line:api.decode_boot(line),(api.ProtocolError,))
 baseline=api.decode_reply(reply(z0=.25,cost=-.1),1);check(baseline['valid'] and baseline['z']==[.25] and baseline['status']==0,'baseline accepted')
 for status in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1001,1008,1009]:
  r=api.decode_reply(reply(status),1);check(not r['valid'] and not any(r['z16']) and r['status']==status,'invalid zero '+str(status))
 mutated=[('unknown_status',reply(999)),('false_valid',reply(1,valid=1)),('false_converged',reply(0,valid=0)),('nonzero_failed_z',reply(2,z0=.1)),('nonzero_failed_KKT',reply(2,kkt_upper=.1)),('nonfinite',reply(cost=float('nan'))),('uint64_counter_overflow',reply().replace('ABQPIO 1 R 1 42','ABQPIO 1 R 18446744073709551616 42')),('duplicate_wrong_sequence',reply().replace(' R 1 ',' R 2 ')),('bad_count',reply().replace(' 42 ',' 41 ',1)),('negative_integer',reply().replace(' R 1 ',' R -1 ')),('truncated_reply',reply()[:-1]),('clock_interval',reply(start_us=100,last_us=99)),('unflagged_diagnostic',reply(1,diagnostic_kkt_upper=1)),('fatal_mismatch',reply(2,fatal=1)),('clock_failure_converged',reply(0,clock_failed=1))]
 for label,line in mutated:expect_error(label,lambda line=line:api.decode_reply(line,1),(api.ProtocolError,))
 for value in [0,1,(1<<53)+1024,(1<<64)-1]:check(api._uint_token(str(value))==value,'uint64 exact '+str(value))
 for value in [-1,1<<64,1.0,True]:expect_error('integer reject '+repr(value),lambda value=value:api.integer(value),(ValueError,))
 for value in [float('nan'),float('inf'),-float('inf'),1e100]:expect_error('finite reject '+repr(value),lambda value=value:api.f32(value),(ValueError,))
 # Every prepared frame is explicitly NOT SENT. This is not numerical replay.
 source=(SEALED/'PROBLEMS.json');data=json.loads(source.read_text());count=0;prepared=HERE/'PREPARED_UNSENT_186_FRAMES.jsonl'
 with prepared.open('x',encoding='utf-8') as out:
  for case_id,q in enumerate(data['cases']):
   for mode in [0,1]:
    warm=q['warm'] if mode else None;tokens,summary=api.encode_problem(q['H'],q['f'],q['lo'],q['hi'],warm,64,.002,0);expected=[x for row in q['H'] for x in row]+q['f']+q['lo']+q['hi']+(q['warm'] if mode else []);actual=[float(x) for x in tokens[7:]];check(len(actual)==len(expected),'prepared count');
    for a,b in zip(actual,expected):check(bits(a)==bits(b),'prepared input bitexact')
    check(int(tokens[4])==mode and summary['warm_present']==mode,'warm not substituted');count+=1;frame=f'ABQPIO 1 S {count} {len(tokens)} '+' '.join(tokens)+'\n';out.write(json.dumps({'case_id':case_id,'name':q['name'],'mode':mode,'sequence':count,'frame':frame,'execution':'UNSENT_PRODUCTION_BINARY_MISSING'})+'\n')
 check(count==186,'186 prepared only');ledger.append({'name':'93 cases both modes','prepared_frames':count,'sent_frames':0,'solver_acceptance_evidence':'NONE'})
 fixture=HERE/'sdk_fault_fixture.exe';check(fixture.is_file(),'lifecycle fixture exists');old_mode=os.environ.get('AQ_IO_TEST_MODE')
 try:
  invalid=[('invalid_warm_allfixed',[[1.]], [0.],[0.],[0.],[float('nan')],{}),('invalid_warm_max0',[[1.]], [0.],[-1.],[1.],[float('inf')],{'max_pivots':0}),('ragged',[[1.,0.]],[0.],[-1.],[1.],None,{}),('maxpivot_overflow',[[1.]],[0.],[-1.],[1.],None,{'max_pivots':1<<32}),('budget_overflow',[[1.]],[0.],[-1.],[1.],None,{'budget_us':1<<64})]
  for label,H,f,lo,hi,warm,options in invalid:
   os.environ['AQ_IO_TEST_MODE']='stall';client=api.ActiveQPLocal(fixture,timeout_s=.5)
   expect_error(label,lambda:client.solve(H,f,lo,hi,warm,**options),(ValueError,));check(client.closed and client.process.poll() is not None,'owned worker stopped '+label);check(not client._writer.is_alive() and not client._reader.is_alive(),'reader writer stopped '+label)
  os.environ['AQ_IO_TEST_MODE']='stall';client=api.ActiveQPLocal(fixture,timeout_s=.2);H=[[-1.2345670461654663e-35*(1+(i+j)*.01) for j in range(16)] for i in range(16)];v=[1.2345670163631439e-30]*16;tokens,_=api.encode_problem(H,v,[-1.1234567165374756e30]*16,[1.1234567165374756e30]*16,v,64,.002,0);size=len(' '.join(tokens));start=time.perf_counter_ns();expect_error('stalled owned pipe timeout',lambda:client.solve(H,v,[-1.1234567165374756e30]*16,[1.1234567165374756e30]*16,v),(TimeoutError,));wall=time.perf_counter_ns()-start;check(client.closed and client.process.poll() is not None,'timeout owned child stopped');check(not client._writer.is_alive() and not client._reader.is_alive(),'timeout threads stopped');ledger.append({'name':'stall timeout lifecycle','configured_timeout_s':.2,'payload_chars':size,'observed_wall_ns':wall,'fixed_robot_wall_gate':False,'solver_process':False})
  os.environ['AQ_IO_TEST_MODE']='eof';client=api.ActiveQPLocal(fixture,timeout_s=.5);expect_error('worker unexpected EOF',lambda:client.solve([[1.]],[0.],[-1.],[1.]),(EOFError,OSError));check(client.closed and client.process.poll() is not None,'EOF worker stopped')
 finally:
  if old_mode is None:os.environ.pop('AQ_IO_TEST_MODE',None)
  else:os.environ['AQ_IO_TEST_MODE']=old_mode
 report={'status':'SDK_ONLY_PARTIAL_NOT_NUMERICAL_IO_QUALIFICATION','checks':checks,'failures':failures,'ledger':ledger,'prepared_frames':count,'production_frames_sent':0,'reference_direct_comparison_executed':False,'raw_malformed_production_worker_tests_executed':False,'logical_earlyabort_worker_test_executed':False,'core_reference_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'Python':sys.version,'Python_pointer_bits':struct.calcsize('P')*8}
 (HERE/'SDK_ONLY_TESTS_01.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'checks':checks,'failures':len(failures),'UNSENT_frames':count,'production_frames_sent':0,'status':report['status']}));return bool(failures)
if __name__=='__main__':
 try:sys.exit(main())
 except Exception:
  (HERE/'sdk_only_exception_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
