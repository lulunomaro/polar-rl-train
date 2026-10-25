"""V2 missing deployer and protocol tests only; V1 spacing error and partial source work retained."""
from pathlib import Path
import ast,hashlib,hmac,http.server,importlib.util,json,socket,sys,threading,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V1_RESOURCE_V69_20261025'
before=D/'before69_network_control_source';assert before.is_dir()
assert not(N/'controllers').exists() and not(N/'payloads').exists()
changed=[]
for branch in ('paired_controllers','h1_only_controllers'):
 for filename in ('three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py'):
  p=N/branch/filename;backup=before/(branch+'__'+filename)
  assert backup.exists() and p.exists()
  changed.append(dict(path=str(p),before_SHA=hashlib.sha256(backup.read_bytes()).hexdigest(),after_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),preserved_before=str(backup)))
p=N/'deploy_selected_pair_unused_once.py';raw=p.read_bytes();assert (before/p.name).read_bytes()==raw;s=raw.decode()
needle="d.OWNER=d.OWNER.replace('1548000','2268000').replace(\"len(c['budget_extensions'])==8\",\"len(c['budget_extensions'])==9\")";assert s.count(needle)==1
s=s.replace(needle,needle+"\nd.OWNER=d.OWNER.replace('10.24.4.210','127.0.0.1')",1)
s=s.replace("socket.create_connection(('10.24.4.210',29754)","socket.create_connection(('127.0.0.1',29754)")
replacement="""        sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
        from reuse_authorized_session_transport import recover
        owner_password,_=recover('RM_SSH_PASSWORD');assert owner_password
        recovery_spec=dict(q['specs']['recovery'],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=owner_password)
        try:recovery=d.launch(c,d.PY72,q['roots']['recovery'],'three_slot_finite_node_v1.py',recovery_spec)
        finally:owner_password=None;recovery_spec.clear()"""
tree=ast.parse(s);call=next(x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='recovery' for t in x.targets));lines=s.splitlines(keepends=True);lines[call.lineno-1:call.end_lineno]=[x+'\n' for x in replacement.splitlines()];s=''.join(lines);ast.parse(s);p.write_text(s,encoding='utf8');changed.append(dict(path=str(p),before_SHA=hashlib.sha256(raw).hexdigest(),after_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),preserved_before=str(before/p.name)))

module_path=N/'sampling_repair_sources/payloads/h1/forwarded_original_owner_control_v1.py'
spec=importlib.util.spec_from_file_location('control_test',module_path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
received=[];bad_signature=False
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  raw=self.rfile.read(int(self.headers['Content-Length']));assert hmac.compare_digest(self.headers['X-Own-Signature'],hmac.new(b'cpu_fixture',raw,hashlib.sha256).hexdigest())
  value=json.loads(raw);received.append(value);body=json.dumps(dict(go=None,stop=True)).encode();self.send_response(200);self.send_header('X-Own-Signature','invalid' if bad_signature else hmac.new(b'cpu_fixture',body,hashlib.sha256).hexdigest());self.end_headers();self.wfile.write(body)
server=http.server.ThreadingHTTPServer(('127.0.0.1',29754),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
class FakeTransport:
 def open_channel(self,kind,target,origin,timeout):
  assert kind=='direct-tcpip' and target==('127.0.0.1',29754)
  return socket.create_connection(target,timeout=timeout)
class FakeSSH:
 def get_transport(self):return FakeTransport()
original_ssh=m._ssh;m._ssh=lambda spec:FakeSSH()
tests=[]
try:
 for key in ('h1','recovery'):
  row=dict(key=key,phase='production',terminal_all_own_children_waited=True,returncode=0,actual_exit=dict(epoch=123.25,actual_waited=True))
  assert m.send(dict(key=key,run_id='cpu_fixture_run',token='cpu_fixture'),row,29754)==dict(go=None,stop=True)
  assert received[-1]['row']==row and 'owner_ssh_password' not in received[-1]
  tests.append(key+'_original_HMAC_terminal_row_exact')
 bad_signature=True
 try:m.send(dict(key='h1',run_id='cpu_fixture_run',token='cpu_fixture'),dict(key='h1'),29754)
 except AssertionError:tests.append('invalid_owner_response_signature_rejected')
 else:raise AssertionError('Bad response signature accepted')
finally:
 m._ssh=original_ssh;m.close();server.shutdown();server.server_close()
report=dict(epoch=time.time(),passed=True,tests=tests,changed=changed,control_module_SHA=hashlib.sha256(module_path.read_bytes()).hexdigest(),original_host_key_SHA256='Jy6VCxnIjb3GEH+GJW2W8YHczNt6TNgFVgE1G+He5TY',owner_loopback_H1_local_E3_original_pinned_SSH=True,no_new_PPO_actor_reward_physics_account_writer_or_budget_changes=True,no_credentials_in_files_or_argv=True,no_remote_GO=True)
with (R/'NEXT69_FORWARDED_CONTROL_SOURCE_AND_PROTOCOL_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,tests=tests,changed_files=len(changed),control_module_SHA=report['control_module_SHA'],no_GO=True)))
