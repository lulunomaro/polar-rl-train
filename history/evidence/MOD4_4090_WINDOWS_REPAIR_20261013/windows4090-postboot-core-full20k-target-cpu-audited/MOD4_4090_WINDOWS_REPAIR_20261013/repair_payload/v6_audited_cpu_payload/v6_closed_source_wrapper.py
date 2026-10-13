"""Exact V5 source loader with explicit closed CPU-reviewable wrapper transforms."""
from pathlib import Path
import ast,hashlib
ORIGINAL_SHA={
 'windows4090_repair_worker.py':'150161d9c58a03f374a0da08f3b56c1f9eae26c3a820b910f8331dfbddd027fe',
 'windows4090_training_runtime.py':'90639bcbe2ee7f8c5d50deb1c333c0ca3292eca5acbb6e2ce05715d12a725ad1',
 'run_windows4090_stage_once.py':'a1cffa984231d4ca67ba86f0045fe0c0c552b7c968591138f1da1425d21c0460',
 'prepare_windows20k_sdk_manifest_cpu_once.py':'6d870186d5466065b55bdc546ae7190b3c528ecc9892f94fdfffd061d9d1d7c8',
}
def load_original(name):
 p=Path(__file__).resolve().parent/name;b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==ORIGINAL_SHA[name],'V5 original bytes changed'
 return p,ast.parse(b.decode('utf8'))
def run_closed(name,namespace,transform):
 path,tree=load_original(name);tree=transform(tree)
 exec(compile(ast.fix_missing_locations(tree),str(path)+'#new-independent-V6-closed-wrapper','exec'),namespace)
