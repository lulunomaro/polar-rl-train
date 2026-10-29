from pathlib import Path
import ast,json
S=Path(__file__).resolve().parent
old=S/"run_NEW_E0_V1_V2_AST_RECOVER_ONLY_reviewed_secure_ingress_UNUSED_once.py";s=old.read_text(encoding="utf8")
pairs=[
("upload_admit_detach_NEW86_E0_final82_long_command_secure_stdin_UNUSED_once_v1.py","read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py"),
("951447d489f6a14e21923e18311c35d0238984421902d8c48f3f3efe6ae2bed8","448a54f54285add3c804af2af0aee3b1e861075a72dd2ea05c9558cc02edf097"),
("NEW86_E0_ADMISSION_ENTRY_CONSUMED_BEFORE_STDIN.json","E0_V4_FIRST_DISTINCT_READ_CONSUMED_BEFORE_STDIN.json"),
("ROOT_E0_V1_V2_","ROOT_E0_V1_FIRST_"),
("NEW_E0_V1_SECURE_SAME_STARTUP_HANDLE","NEW_E0_V1_FIRST_SECURE_SAME_HANDLE"),
("SAME_FINITE_NEW_E0_V1_STARTUP","SAME_FINITE_NEW_E0_V1_FIRST"),
("time.time()-start>650","time.time()-start>470")]
for a,b in pairs:
 assert a in s,a;s=s.replace(a,b)
a='[sys.executable,"-u","-B","-X","utf8",str(ENTRY)]'
b='[sys.executable,"-u","-B","-X","utf8",str(ENTRY),"--actual-startup-json",str(D/"reports/NEW86_E0_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json"),"--actual-startup-SHA","2432827ab7a07d5c6410c7130256c8ac1e9f3154d694cd959901456058ed7b7a"]'
assert s.count(a)==1;s=s.replace(a,b)
compile(s,"E0_FIRST","exec")
p=S/"run_NEW_E0_V1_FIRST360_AST_RECOVER_ONLY_secure_ingress_UNUSED_once.py"
with p.open("x",encoding="utf8",newline="\n") as f:f.write(s)
print(str(p))

