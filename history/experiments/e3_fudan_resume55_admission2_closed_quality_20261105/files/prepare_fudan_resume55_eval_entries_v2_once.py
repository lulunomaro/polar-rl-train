"""New unused entry builder fixes observed Root3 ancestor-fragment whitespace only; no physical retry."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;s=(D/'prepare_fudan_resume55_eval_entries_once.py').read_text(encoding='utf8')
a="assert 'ancestral_N4096_checkpoint' not in s and 'ancestor_N4096_reads' not in s"
replacement='''start=s.index('    source_receipt = f["source_checkpoint"]');stop=s.index('    init, update = ',start)
s=s[:start]+\'''    source_receipt = f["source_checkpoint"]
    need(source_receipt["source_sha256"] == LEARNER_SHA == lineage["source_sha256"] == lineage["source_binding"]["sha256"] and
         source_receipt["base_counters"] == BASE and source_receipt["source_path"] == lineage["source_path"] == lineage["source_binding"]["path"] and
         source_receipt["source_bytes"] == lineage["source_bytes"] == lineage["source_binding"]["bytes"] and
         source_receipt["source_run"] == lineage["source_run"] == lineage["source_binding"]["run"] and
         f["ancestral_mother_checkpoint"]["source_sha256"] == MOTHER_SHA and f["original_mother_reads"] == 0 and
         f["learner_source_reads"] == source_receipt["learner_source_reads"] == 1 and source_receipt["original_mother_reads"] == 0,
         "Actual complete source55 and separate historical mother metadata required")
\'''+s[stop:]
s=''.join(line for line in s.splitlines(keepends=True)if '("ancestral_N4096_checkpoint",'not in line)
s=s.replace(' and latest["ancestor_N4096_reads"] == 0','')
assert 'ancestral_N4096_checkpoint' not in s and 'ancestor_N4096_reads' not in s'''
assert s.count(a)==1;s=s.replace(a,replacement)
a="available={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}|set(values)"
b="available={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}|{t.id for n in tree.body if isinstance(n,(ast.Assign,ast.AnnAssign)) for t in (n.targets if isinstance(n,ast.Assign)else [n.target]) if isinstance(t,ast.Name)}"
assert s.count(a)==1;s=s.replace(a,b)
ast.parse(s);exec(compile(s,str(D/'prepare_fudan_resume55_eval_entries_v2_once.py'),'exec'),{'__name__':'__main__','__file__':str(D/'prepare_fudan_resume55_eval_entries_v2_once.py')})
