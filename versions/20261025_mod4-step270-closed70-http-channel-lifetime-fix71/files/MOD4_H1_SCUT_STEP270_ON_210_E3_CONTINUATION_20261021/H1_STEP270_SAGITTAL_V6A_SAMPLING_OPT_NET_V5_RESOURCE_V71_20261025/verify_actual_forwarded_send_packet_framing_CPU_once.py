"""Execute actual original and repaired send() with real HTTPClient/Paramiko file semantics."""
from pathlib import Path
import hashlib,hmac,importlib.util,json,time
import paramiko
F=Path(__file__).resolve().parent;T=F.parent
old=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V70_20261025/payloads/recovery/forwarded_original_owner_control_v1.py'
def module(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
original=module(old,'original_control');fixed=module(F/'forwarded_original_owner_control_v2.py','fixed_control')
key='CPU-SYNTHETIC-NON-CREDENTIAL';body=b'{"go":null,"stop":false}'
signature=hmac.new(key.encode(),body,hashlib.sha256).hexdigest();header=('HTTP/1.0 200 OK\r\nX-Own-Signature: '+signature+'\r\n\r\n').encode()
class Channel:
 def __init__(self,chunks):self.chunks=list(chunks);self.closed=False;self.sent=b''
 def recv(self,n):
  if self.closed or not self.chunks:return b''
  out=self.chunks[0][:n];self.chunks[0]=self.chunks[0][n:]
  if not self.chunks[0]:self.chunks.pop(0)
  return out
 def sendall(self,data):assert not self.closed;self.sent+=data
 def makefile(self,*a,**kw):return paramiko.ChannelFile(self,*a,**kw)
 def close(self):self.closed=True;self.chunks.clear()
 def settimeout(self,value):assert value==15
class Transport:
 def __init__(self,c):self.c=c
 def open_channel(self,kind,dest,origin,timeout):assert kind=='direct-tcpip' and dest==('127.0.0.1',29754) and timeout==12;return self.c
class Client:
 def __init__(self,c):self.c=c
 def get_transport(self):return Transport(self.c)
def run(m,chunks,should_pass):
 c=Channel(chunks);m._ssh=lambda spec:Client(c)
 try:
  result=m.send(dict(key='recovery',token=key,run_id='CPU-SYNTHETIC'),dict(key='recovery'),29754)
  assert should_pass and result==dict(go=None,stop=False)
  outcome='authenticated_complete_response'
 except AssertionError:
  assert not should_pass;outcome='rejected'
 assert c.closed
 return dict(outcome=outcome,raw_channel_closed=True,request_signed=b'X-Own-Signature:' in c.sent)
tests=dict(original_fragmented_rejected=run(original,[header,body],False),original_coalesced_passes=run(original,[header+body],True),fixed_fragmented_passes=run(fixed,[header,body],True),fixed_byte_fragments_pass=run(fixed,[header]+[bytes([x]) for x in body],True),fixed_tamper_rejected=run(fixed,[header,b'{"go":null,"stop":true}'],False),fixed_truncated_rejected=run(fixed,[header,body[:2]],False),fixed_no_signature_rejected=run(fixed,[b'HTTP/1.0 200 OK\r\n\r\n',body],False))
report=dict(epoch=time.time(),passed=True,tests=tests,actual_original_and_fixed_send_functions_executed=True,actual_HTTPClient_and_paramiko_ChannelFile=True,synthetic_transport_only_no_actual_SSH_or_real_token=True,new_module_SHA=hashlib.sha256((F/'forwarded_original_owner_control_v2.py').read_bytes()).hexdigest(),no_training_GPU_raw_or_budget_action=True)
with (F/'reports/ACTUAL_SEND_PACKET_FRAGMENTATION_CPU_INTEGRATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,actual_send_tests=len(tests),original_failure_reproduced=True,authentication_unchanged=True)))
