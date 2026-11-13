"""Remove only a safely closed owned native job's reproducible terrain cache."""
from pathlib import Path
import json,shlex
from remote_run import execute

def cleanup_closed_cache(c,root,job,python):
 code='from pathlib import Path;import json,shutil;root=Path('+repr(root)+').resolve();job=Path('+repr(job)+').resolve();p=job/"kit_isolation"/"DerivedDataCache";assert job.is_relative_to(root) and (job/"SAFE_CLOSED.json").exists();assert p.resolve()==p and p.name=="DerivedDataCache" and p.parent.name=="kit_isolation";existed=p.exists();shutil.rmtree(p) if existed else None;u=shutil.disk_usage(root);print(json.dumps({"job":str(job),"removed_only_derived_cache":existed,"free_bytes":u.free,"models_logs_sources_preserved":True}))'
 return json.loads(execute(c,shlex.quote(python)+' -c '+shlex.quote(code)))
