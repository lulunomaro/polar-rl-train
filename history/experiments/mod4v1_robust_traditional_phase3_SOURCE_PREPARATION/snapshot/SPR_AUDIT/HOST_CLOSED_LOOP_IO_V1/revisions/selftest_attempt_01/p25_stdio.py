"""Python64 -> resident MinGW32 C P25 via local ASCII stdio, no ctypes.
No physics/BSP imports. C/kernel faults are surfaced; never restart/rearm silently.
"""
from pathlib import Path
import json,math,numbers,struct,subprocess,threading,queue
HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'PROTOCOL_SCHEMA.json').read_text(encoding='utf-8'))
DEFAULT=json.loads((HERE/'DEFAULT_INIT_P25.json').read_text(encoding='utf-8'))['fields']
class ProtocolError(RuntimeError):pass
class ControllerFault(RuntimeError):
 def __init__(self,reply):self.reply=reply;super().__init__(f"C P25 fault status={reply['status']} wire_sequence={reply['sequence']}; zero payload, new process required")
def f32(value):
 value=float(value)
 if not math.isfinite(value):raise ValueError('finite float32 required')
 try:value=struct.unpack('<f',struct.pack('<f',value))[0]
 except OverflowError as error:raise ValueError('float32 range') from error
 if not math.isfinite(value):raise ValueError('finite float32 required')
 return value
def integer(value,kind):
 if not isinstance(value,numbers.Integral):raise ValueError(f'{kind} requires an integer, not a float timestamp')
 value=int(value);lo=-(1<<63) if kind=='i64' else 0;hi=(1<<63)-1 if kind=='i64' else ((1<<64)-1 if kind=='u64' else (1<<32)-1)
 if not lo<=value<=hi:raise ValueError(kind+' range')
 return value
def encode_fields(kind,fields):
 definitions=SCHEMA[kind]
 if set(fields)!=set(definitions):raise ValueError(f'{kind} field set mismatch missing={set(definitions)-set(fields)} extra={set(fields)-set(definitions)}')
 tokens=[]
 for name,spec in definitions.items():
  values=[fields[name]] if spec['count']==1 else list(fields[name])
  if len(values)!=spec['count']:raise ValueError(name+' vector length')
  for value in values:tokens.append(format(f32(value),'.9g') if spec['type']=='f32' else str(integer(value,spec['type'])))
 return tokens
def decode_reply(line,expected_sequence):
 tokens=line.split()
 if len(tokens)<6 or tokens[:3]!=['PC3IO','1','R']:raise ProtocolError('invalid reply header: '+repr(line))
 try:sequence=int(tokens[3]);status=int(tokens[4]);count=int(tokens[5])
 except ValueError as error:raise ProtocolError('invalid integer header') from error
 if sequence!=expected_sequence or count!=len(SCHEMA['REPLY_fields']) or len(tokens)!=6+count:raise ProtocolError('reply sequence/count mismatch')
 values=[]
 for token,spec in zip(tokens[6:],SCHEMA['REPLY_fields']):
  if spec['type']=='f32':value=f32(float(token))
  else:
   if any(c not in '-0123456789' for c in token):raise ProtocolError('bad integer payload')
   value=integer(int(token),spec['type'])
  values.append(value)
 if status!=0 and any(v!=0 for v in values):raise ProtocolError('nonzero fault payload')
 result={'sequence':sequence,'status':status,'all_payload_zero':all(v==0 for v in values)}
 for name,spec in SCHEMA['REPLY'].items():
  subset=values[spec['offset']:spec['offset']+spec['count']];result[name]=subset[0] if spec['count']==1 else subset
 result['tau_row6']=result['GUARDED_TAU'];result['tau_math_row6']=result['MATH_TAU'];result['valid']=bool(result['VALID']);return result

def make_step(packet,command,drive,now_us,clock_before_us=None,clock_after_us=None):
 """All packet/mean metadata is explicit; this is not a sampling collector."""
 return {'NOW':now_us,'CLOCK_BEFORE':now_us if clock_before_us is None else clock_before_us,'CLOCK_AFTER':now_us if clock_after_us is None else clock_after_us,
  'SAMPLED':packet['sampled_us'],'ARRIVAL':packet['arrival_us'],'EPOCH':packet['channel_epoch_us'],'WINDOW_BEGIN':packet['window_begin_us'],'WEIGHT_SUM':packet['mean_weight_sum_us'],
  'PSEQ':packet['sequence'],'PFLAGS':packet['flags'],'EXPECTED':packet['expected_count'],'VALID_COUNT':packet['valid_count'],'DROPPED':packet['dropped_count'],
  'COHERENT':packet['coherent'],'MEAN_VALID':packet['mean_valid'],'WEIGHTS_VALID':packet['mean_weights_valid'],'MEAN_MODE':packet['mean_mode'],
  'GYRO':packet['gyro_body'],'ACCEL':packet['proper_accel_body'],'Q4':packet['joint_q4'],'DQ4':packet['joint_dq4'],'SPIN2':packet['wheel_spin2'],
  'CMD_ISSUED':command['issued_us'],'CMD_EXPIRES':command['expires_us'],'CMD_SEQ':command['sequence'],'CMD_FLAGS':command['flags'],'CMD_ENABLE':command['enable'],
  'FORWARD':command['forward_m_s'],'YAW':command['yaw_rad_s'],'DRIVE_STAMP':drive['sampled_us'],'DRIVE_FLAGS':drive['flags'],'DRIVE_VEL':drive['velocity_row6']}

def from_v4_packet(p,*,sequence,window_begin_us,mean_weight_sum_us,expected_count,valid_count,dropped_count,mean_mode,mean_valid,mean_weights_valid):
 """Duck-type a frozen V4 SensorPacket. Quality/aperture are CALLER declarations;
 no invented 2kHz sampling, timeweighting or real-CAN synchronization here."""
 stamp=int(round(float(p.time_s)*1e6));arrival=int(round(float(p.arrival_s)*1e6))
 return {'sampled_us':stamp,'arrival_us':arrival,'channel_epoch_us':[stamp]*4,'sequence':sequence,'flags':1 if p.validity else 0,'coherent':1,
  'window_begin_us':window_begin_us,'mean_weight_sum_us':mean_weight_sum_us,'expected_count':expected_count,'valid_count':valid_count,'dropped_count':dropped_count,
  'mean_mode':mean_mode,'mean_valid':int(mean_valid),'mean_weights_valid':int(mean_weights_valid),'gyro_body':list(p.gyro_body),'proper_accel_body':list(p.accel_proper_body),
  'joint_q4':list(p.joint_pos4),'joint_dq4':list(p.joint_vel4),'wheel_spin2':list(p.wheel_vel2)}

class P25Local:
 def __init__(self,executable=None,*,timeout_s=5.0,stderr_path=None):
  self.timeout=float(timeout_s);self.sequence=0;self.initialized=False;self.fault_reply=None;self.closed=False;self._stderr=open(stderr_path,'w',encoding='utf-8') if stderr_path else None
  self.process=subprocess.Popen([str(Path(executable or HERE/'p25_host_adapter.exe').resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self._stderr,text=True,encoding='ascii',errors='strict',bufsize=1)
  self._lines=queue.Queue();self._lock=threading.Lock();self._reader=threading.Thread(target=self._read_lines,daemon=True);self._reader.start()
 def _read_lines(self):
  try:
   for line in self.process.stdout:self._lines.put(line)
  except Exception as error:self._lines.put(error)
  finally:self._lines.put(None)
 def exchange_raw(self,operation,tokens,*,wire_sequence=None,payload_count=None,check=True):
  """Low-level entry for protocol selftests; ordinary callers use initialize/step."""
  with self._lock:
   if self.closed:raise ProtocolError('client closed')
   sequence=self.sequence+1 if wire_sequence is None else int(wire_sequence);count=len(tokens) if payload_count is None else int(payload_count)
   line='PC3IO 1 '+str(operation)+' '+str(sequence)+' '+str(count)+(' '+' '.join(str(x) for x in tokens) if tokens else '')+'\n'
   try:
    self.process.stdin.write(line);self.process.stdin.flush();answer=self._lines.get(timeout=self.timeout)
    if answer is None:raise EOFError('adapter EOF before reply')
    if isinstance(answer,Exception):raise answer
    reply=decode_reply(answer,sequence)
   except queue.Empty as error:
    self.terminate();raise TimeoutError('resident adapter response timeout') from error
   except (OSError,EOFError,ProtocolError,ValueError) as error:
    self.terminate();raise ProtocolError(str(error)) from error
   self.sequence=sequence
   if reply['status']!=0:self.fault_reply=reply
   if check and reply['status']!=0:raise ControllerFault(reply)
   return reply
 def initialize(self,fields=None):
  if self.initialized:raise ProtocolError('initialize once per process')
  if self.fault_reply:raise ControllerFault(self.fault_reply)
  try:tokens=encode_fields('INIT',DEFAULT if fields is None else fields)
  except Exception:self.terminate();raise
  reply=self.exchange_raw('I',tokens);self.initialized=True;return reply
 def step(self,packet,command,drive,now_us,*,clock_before_us=None,clock_after_us=None):
  if self.fault_reply:raise ControllerFault(self.fault_reply)
  try:fields=make_step(packet,command,drive,now_us,clock_before_us,clock_after_us);tokens=encode_fields('STEP',fields)
  except Exception:self.terminate();raise
  return self.exchange_raw('S',tokens)
 def terminate(self):
  if self.closed:return
  self.closed=True
  if self.process.poll() is None:self.process.terminate()
  try:self.process.wait(timeout=2)
  except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=2)
  for stream in [self.process.stdin,self.process.stdout]:
   try:stream.close()
   except OSError:pass
  if self._stderr:self._stderr.close()
 def close(self):
  if self.closed:return
  try:self.exchange_raw('Q',[],check=False);self.process.stdin.close();self.process.wait(timeout=self.timeout)
  except (ProtocolError,TimeoutError,OSError,subprocess.TimeoutExpired):self.terminate();return
  self.closed=True;self.process.stdout.close()
  if self._stderr:self._stderr.close()
 def __enter__(self):return self
 def __exit__(self,*unused):self.close()
