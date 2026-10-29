from pathlib import Path
import ast,hashlib
B=Path(__file__).resolve().parent
old=B/"run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py"
s=old.read_text(encoding="utf-8")
pairs=[
("read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py","collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py"),
("818f73503e2554442db603e6a7b48f4ba6536cd4d8e1f1ed9bb255951780567e","b9f93729e2310b54325c77d06b2630600b55ff72fc5a7de91a79ef1dd36b8c29"),
("FIRST","TERMINAL"),
("time.time()-start>470","time.time()-start>950")]
for a,b in pairs:
 assert a in s,a
 s=s.replace(a,b)
ast.parse(s)
target=B/"run_NEW_E2_V4_TERMINAL_reviewed_secure_ingress_UNUSED_once.py"
with target.open("x",encoding="utf8",newline="\n") as f:f.write(s)
print(hashlib.sha256(target.read_bytes()).hexdigest())

