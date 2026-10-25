"""Deterministic packet-fragmentation reproduction of original HTTP/Paramiko ownership bug."""
from pathlib import Path
import ast,hashlib,hmac,http.client,json,sys,time,traceback
import paramiko
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
F=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'
H=lambda b:hashlib.sha256(b).hexdigest()
try:
 F.mkdir();(F/'reports').mkdir()
 original=N/'payloads/recovery/forwarded_original_owner_control_v1.py';text=original.read_text('utf8')
 ADAPTER='''
class _ResponseOwnedChannelSocket:
    """HTTPConnection may close its socket before HTTP/1.0 response-body read.

    The outer send() owns this raw SSH channel through body authentication;
    HTTPConnection.close() only drops its borrowed view. Always close the raw
    channel in send() finally. Credentials and protocol signatures are unchanged.
    """
    def __init__(self,channel):self.channel=channel
    def sendall(self,data):return self.channel.sendall(data)
    def makefile(self,*args,**kwargs):return self.channel.makefile(*args,**kwargs)
    def close(self):pass
'''
 needle="def send(spec,row,port):";assert text.count(needle)==1
 new=text.replace(needle,ADAPTER+'\n'+needle,1)
 needle="connection.sock=channel";assert new.count(needle)==1
 new=new.replace(needle,"connection.sock=_ResponseOwnedChannelSocket(channel)",1)
 needle="   elif channel is not None:channel.close()";assert new.count(needle)==1
 new=new.replace(needle,"   if channel is not None:channel.close()",1)
 ast.parse(new)
 with (F/'forwarded_original_owner_control_v2.py').open('x',encoding='utf8') as f:f.write(new)
 ns={};exec(ADAPTER,ns);Adapter=ns['_ResponseOwnedChannelSocket']
 # Synthetic key only. No real owner token/password/model/SSH or GPU is used.
 token=b'CPU-SYNTHETIC-NON-CREDENTIAL';body=b'{"go":null,"stop":false}'
 signature=hmac.new(token,body,hashlib.sha256).hexdigest()
 headers=('HTTP/1.0 200 OK\r\nX-Own-Signature: '+signature+'\r\n\r\n').encode()
 class FragmentedChannel:
  def __init__(self,chunks):self.chunks=list(chunks);self.closed=False;self.close_count=0
  def recv(self,n):
   if self.closed or not self.chunks:return b''
   out=self.chunks[0][:n];self.chunks[0]=self.chunks[0][n:]
   if not self.chunks[0]:self.chunks.pop(0)
   return out
  def sendall(self,data):assert not self.closed
  def makefile(self,*args,**kwargs):return paramiko.ChannelFile(self,*args,**kwargs)
  def close(self):self.closed=True;self.close_count+=1;self.chunks.clear()
 def response(use_adapter,chunks):
  channel=FragmentedChannel(chunks);c=http.client.HTTPConnection('127.0.0.1',29754);c.sock=Adapter(channel) if use_adapter else channel
  c.request('POST','/',body=b'{}');r=c.getresponse();closed_before_read=channel.closed
  result=r.read();sig=r.getheader('X-Own-Signature');valid=bool(sig and hmac.compare_digest(sig,hmac.new(token,result,hashlib.sha256).hexdigest()))
  c.close();channel.close()
  return dict(body_bytes=len(result),valid_HMAC=valid,raw_channel_closed_before_read=closed_before_read,raw_channel_closed_finally=channel.closed)
 old=response(False,[headers,body]);assert old['raw_channel_closed_before_read'] and not old['valid_HMAC'] and old['body_bytes']==0
 fixed=response(True,[headers,body]);assert not fixed['raw_channel_closed_before_read'] and fixed['valid_HMAC'] and fixed['body_bytes']==len(body) and fixed['raw_channel_closed_finally']
 together=response(False,[headers+body]);assert together['valid_HMAC']
 fragmented=response(True,[headers]+[bytes([c]) for c in body]);assert fragmented['valid_HMAC']
 bad=response(True,[headers,b'{"go":null,"stop":true}']);assert not bad['valid_HMAC']
 missing=response(True,[b'HTTP/1.0 200 OK\r\n\r\n',body]);assert not missing['valid_HMAC']
 short=response(True,[headers,body[:4]]);assert not short['valid_HMAC']
 expected=text.replace('def send(spec,row,port):',ADAPTER+'\n'+'def send(spec,row,port):',1).replace('connection.sock=channel','connection.sock=_ResponseOwnedChannelSocket(channel)',1).replace('   elif channel is not None:channel.close()','   if channel is not None:channel.close()',1)
 assert ast.dump(ast.parse(new))==ast.dump(ast.parse(expected))
 errors=list((N/'current_pair_closed_text/recovery').glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'));kinds={}
 for p in errors:
  e=json.loads(p.read_bytes())['error'];kind='HMAC_response_assertion' if 'hmac.compare_digest(signature' in e else 'other_transport_error'
  kinds[kind]=kinds.get(kind,0)+1
 report=dict(epoch=time.time(),passed_CPU_reproduction_and_fix=True,paramiko_version=paramiko.__version__,actual70_control_errors=len(errors),actual_error_kinds=kinds,
  mechanism='HTTP/1.0 response has will_close=True. HTTPConnection.getresponse closes its socket before caller reads body. Normal socket.makefile keeps underlying FD alive; Paramiko ChannelFile does not defer raw Channel.close. Body delivered in same packet may pass, split packet yields empty/truncated body and original HMAC assert. Borrowed socket view defers raw channel close to outer send finally without changing HMAC or stop rules.',
  old_split_response_reproduced=old,old_single_packet_may_pass=together,fixed_split_response=fixed,fixed_byte_fragments=fragmented,tamper_still_rejected=not bad['valid_HMAC'],missing_signature_still_rejected=not missing['valid_HMAC'],truncated_body_still_rejected=not short['valid_HMAC'],
  original_module_path=str(original),original_module_SHA=H(original.read_bytes()),new_module_path=str(F/'forwarded_original_owner_control_v2.py'),new_module_SHA=H(new.encode()),
  exact_module_change='Add borrowed channel view; bind HTTPConnection.sock to it; always close raw channel in finally. All other AST including signatures/SSH pins/dependencies/timeouts/HTTP bytes unchanged.',
  no_remote_SSH_HTTP_owner_model_raw_GPU_or_training_action=True,new_source_only_not_installed=True)
 with (R/'CONTROL_HTTP10_PARAMIKO_LIFETIME_REPRODUCTION_AND_FIX_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 with (F/'reports/CONTROL_RESPONSE_LIFETIME_FIX_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed=True,actual70_error_kinds=kinds,old_split_packet_HMAC_passed=old['valid_HMAC'],new_split_packet_HMAC_passed=fixed['valid_HMAC'],tamper_rejected=True,no_remote_action=True)))
except BaseException:
 with (R/('CONTROL_LIFETIME_DIAGNOSTIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),original_failures_retained=True,no_retry_same_once=True),f,indent=2)
 raise
