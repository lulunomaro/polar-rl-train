"""Retain stdlib-only reader rejection; use the admitted CPU PyTorch environment."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
old=D/'review_seed_final_closeout_actual.py';new=D/'review_seed_final_cpu_environment_actual.py';assert not new.exists()
text=old.read_text(encoding='utf8')
helper='''def target_json(n,code):
 import shlex
 _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=90)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 assert rc==0,(raw+err).decode(errors='replace')
 return json.loads(raw)
'''
text=text.replace('def main():',helper+'\ndef main():',1).replace('v=io.linux_json(n,','v=target_json(n,',1)
ast.parse(text);new.write_text(text,encoding='utf8')
error=max(R.glob('ENTRY_FINAL_READER_ERROR_[0-9]*.json'),key=lambda p:int(p.stem.removeprefix('ENTRY_FINAL_READER_ERROR_')))
assert 'ModuleNotFoundError: No module named' in json.loads(error.read_bytes())['error']
p=R/'ENTRY_FINAL_READER_CPU_ENVIRONMENT_REVIEW.json';assert not p.exists()
p.write_text(json.dumps(dict(epoch=time.time(),original_error=str(error),old_source=str(old),old_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_source=str(new),new_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_reader_environment_changed=True,read_only_no_GPU_or_training_or_CAS=True,original_rejection_not_physical_failure=True),indent=2),encoding='utf8')
print(json.dumps(dict(new_reader=str(new),read_only=True)))
