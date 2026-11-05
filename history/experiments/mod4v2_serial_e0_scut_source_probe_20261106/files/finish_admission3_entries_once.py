"""Finish only the unpublished A3 CLI entries after a local source-anchor failure."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;source=(D/'prepare_admission3_native_gate_once.py').read_text(encoding='utf8');tree=ast.parse(source);loop=next(n for n in tree.body if isinstance(n,ast.For)and isinstance(n.target,ast.Tuple)and [x.id for x in n.target.elts]==['old','new']);tail=''.join(source.splitlines(keepends=True)[loop.lineno-1:]);lines=tail.splitlines(keepends=True)
for i,line in enumerate(lines):
 if 'start=t.index('in line and 'archive=D/'in line:
  indent=line[:len(line)-len(line.lstrip())]
  lines[i]=indent+"parsed=ast.parse(t);segments=t.splitlines(keepends=True);an=next(n for n in ast.walk(parsed)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='archive'for x in n.targets));en=next(n for n in ast.walk(parsed)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='mkdirs'and n.lineno>an.lineno);t=''.join(segments[:an.lineno-1]+segments[en.lineno-1:])\n"
  break
else:raise AssertionError('Observed local anchor line missing')
closed=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=closed['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert closed['closed']is True and end['all_own_children_waited']is end['original_cost_settled']is end['original_private_finite_authority_leases_released']is True and outer['original_owner_reaped']is True
assert(D/'source_owner_v2_native_gate/migration_nine_original_owner_v1.py').is_file()and(D/'stage_nine_nonpt_runtime_v2.py').is_file()
exec(compile(''.join(lines),str(Path(__file__)),'exec'),dict(globals()))
