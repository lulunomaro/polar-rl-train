from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=HERE/'INDEX.json';assert not out.exists();r=HERE/'reports';r.mkdir(exist_ok=True)
 source=HERE/'first_contact_metadata_and_exact_new_root_probe_once.py';tree=ast.parse(source.read_bytes())
 remote=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='REMOTE_SOURCE' for x in n.targets))
 ast.parse(remote.replace('__PROBE_ID_JSON__',json.dumps('SOURCE_AST_ONLY_NOT_EXECUTED')))
 with (r/'SOURCE_AST_ONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,client_and_remote_AST_passed=True,
  source_SHA=H(source),network_or_remote_mkdir_or_credentials_not_executed=True,no_fixture_or_model_or_SDK_or_GPU=True,
  actual_probe_pending_root_stdin=True),f,indent=2)
 rows=[dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.rglob('*')) if p.is_file()]
 with out.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_frozen=True,files=rows,actual_probe_pending=True,Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(entry=str(source),source_SHA=H(source),index_SHA=H(out),source_only=True,actual_probe_not_executed=True)))
if __name__=='__main__':main()
