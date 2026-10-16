"""Same verified role/guard; send larger own source through stdin, not argv."""
import json,base64
import transport_249_exact_desktop_role_fresh2233_v6 as base
PY=base.PY;ROOT=base.ROOT;connect=base.connect;close=base.close;ps=base.ps;guard_code=base.guard_code
def py(c,source,timeout=60):
 compile(source,'<owned explicit 249 stdin operation>','exec');command='"'+PY+'" -B -X utf8 -c "import sys;exec(compile(sys.stdin.read(),\'<owned stdin operation>\',\'exec\'))"';stdin,stdout,stderr=c.exec_command(command,timeout=timeout);stdin.write(source.encode('utf8'));stdin.flush();stdin.channel.shutdown_write();raw=stdout.read();err=stderr.read();rc=stdout.channel.recv_exit_status();assert rc==0,(rc,base64.b64encode(err).decode(),err.decode('utf8','replace')[-6000:]);return json.loads(raw)
