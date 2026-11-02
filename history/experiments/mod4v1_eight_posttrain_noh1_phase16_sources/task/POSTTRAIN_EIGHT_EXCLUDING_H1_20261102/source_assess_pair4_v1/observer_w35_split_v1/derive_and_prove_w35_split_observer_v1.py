"""Unused future-pair4 observer overlay. Source text/AST + stateless row tests only.
Never imports SDK/torch/old row writer; never opens model/JSONL/NPZ/raw/pendingcase.
"""
from pathlib import Path
import ast,copy,difflib,hashlib,json,math,sys
B=Path(__file__).resolve().parent;D=B.parents[1]
sys.path.insert(0,str(B));sys.path.insert(0,str(B.parent))
import rm70_published_split_observer_v1 as helper
import assess_pair4_retention_closed_metadata_v1 as assessor
OLD=D/'PAIR1_RETENTION_EVAL_SOURCE_V3'

def once(text,a,b):assert text.count(a)==1,a;return text.replace(a,b,1)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(path):
    raw=Path(path).read_bytes();return dict(path=str(path),bytes=len(raw),SHA=sha(raw))
def put(name,value):
    with (B/name).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2)

def main():
    original=(OLD/'rm70_intervals227.py').read_text(encoding='utf-8-sig')
    new=once(original,'from positional_rows227 import PositionalRows227 as Rows227',
        'from positional_rows227 import PositionalRows227 as Rows227\nfrom rm70_published_split_observer_v1 import empty_counts,observe_row,publish_counts')
    new=once(new,'  def zeros(dtype=None):return t.zeros(n,device=device,dtype=dtype or t.float32)',
        '  self._published_split_counts=empty_counts();self._published_book_constructor_label=model\n  def zeros(dtype=None):return t.zeros(n,device=device,dtype=dtype or t.float32)')
    emit_lines=[line for line in new.splitlines()if line.lstrip().startswith('for i in range(len(cpu')]
    assert len(emit_lines)==1
    anchor=emit_lines[0];indent=anchor[:len(anchor)-len(anchor.lstrip())]
    header=anchor.partition(':')[0]+':'
    tree_now=ast.parse(new);book_node=next(n for n in tree_now.body if isinstance(n,ast.ClassDef))
    emit_node=next(n for n in book_node.body if isinstance(n,ast.FunctionDef)and n.name=='emit_columns')
    original_dict=emit_node.body[1].body[0].value.args[0]
    new=once(new,anchor,header+'\n'+indent+' row='+ast.unparse(original_dict)+'\n'+indent+' self._published_split_counts=observe_row(self._published_split_counts,row)\n'+indent+' self.rows.append(row)')
    finish_lines=[line for line in new.splitlines()if 'timeout_environment_controls=self.timeout_controls,producer=self.rows.finish(),diagnostic_errors=self.errors,'in line]
    assert len(finish_lines)==1
    anchor=finish_lines[0];indent=anchor[:len(anchor)-len(anchor.lstrip())]
    new=once(new,anchor,anchor+'\n'+indent+'published_moving_standing_counts=publish_counts(self._published_split_counts,self.events,self._published_book_constructor_label),')
    book=B/'rm70_intervals227_split_metadata_v1.py';book.write_text(new,encoding='utf-8')
    worker_original=(OLD/'worker_five_original_n80.py').read_text(encoding='utf-8-sig')
    worker_new=once(worker_original,'from rm70_intervals227 import RM70Intervals227','from rm70_intervals227_split_metadata_v1 import RM70Intervals227')
    worker=B/'worker_five_original_n80.py';worker.write_text(worker_new,encoding='utf-8')
    # Unique module name avoids silently importing an old runtime/lib module
    # after the worker prepends those search paths. No edits to any old library.
    changes=list(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile=str(OLD/'rm70_intervals227.py'),tofile=book.name))
    changes+=list(difflib.unified_diff(worker_original.splitlines(True),worker_new.splitlines(True),fromfile=str(OLD/'worker_five_original_n80.py'),tofile=worker.name))
    (B/'W35_SPLIT_OBSERVER_MINIMAL_SOURCE_DIFF_V1.patch').write_text(''.join(changes),encoding='utf-8')
    trees=[ast.parse(t)for t in(original,new)]
    classes=[next(n for n in t.body if isinstance(n,ast.ClassDef)and n.name=='RM70Intervals227')for t in trees]
    methods=[{n.name:n for n in c.body if isinstance(n,ast.FunctionDef)}for c in classes]
    untouched=[name for name in methods[0]if name not in('__init__','emit_columns','finish')]
    assert all(ast.dump(methods[0][name],include_attributes=False)==ast.dump(methods[1][name],include_attributes=False)for name in untouched)
    assert helper.ROW_FIELD_MAPPING==assessor.SPLIT_MAPPING
    # Load only class definitions; __init__, close/terminal, SDK and row writer
    # are never called. emit_columns runs against already-host synthetic columns.
    cls=[]
    for node in classes:
        ns=dict(math=math,empty_counts=helper.empty_counts,observe_row=helper.observe_row,publish_counts=helper.publish_counts)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'SOURCE_ONLY_BOOK_CLASS','exec'),ns)
        cls.append(ns['RM70Intervals227'])
    class Column:
        def __init__(self,x):self.x=x
        def detach(self):return self
        def cpu(self):return self
        def tolist(self):return copy.deepcopy(self.x)
    class Rows:
        def __init__(self):self.data=[]
        def append(self,r):self.data.append(copy.deepcopy(r))
        def finish(self):return dict(SYNTHETIC_ONLY=True,rows=len(self.data))
    records=dict(env_id=[0,1,2,3],standing=[True,False,False,False],
        natural_complete_nonterminal_interval=[True,True,False,True],complete_interval_bounds_fact=[True,False,False,True],
        # Inverted speed values prove grouping does not infer a new speed test.
        nominal_speed=[99.,0.,0.,0.],source_SHA=['OLD_PRODUCER_LABEL']*4)
    old=cls[0].__new__(cls[0]);patch=cls[1].__new__(cls[1]);old.rows=Rows();patch.rows=Rows()
    patch._published_split_counts=helper.empty_counts();patch._published_book_constructor_label='BOOK_LABEL_NOT_POLICY_LOAD_PROOF'
    columns={k:Column(v)for k,v in records.items()};extra=dict(record_type='same_UID_original_RM70_command',end_reason='original_resample')
    old.emit_columns(columns,extra);patch.emit_columns(columns,extra)
    assert old.rows.data==patch.rows.data
    assert patch._published_split_counts==dict(moving_complete=dict(count=2,original_bounds_met=1),standing_complete=dict(count=1,original_bounds_met=1))
    assert all(r['source_SHA']=='OLD_PRODUCER_LABEL'for r in patch.rows.data)
    initial=helper.empty_counts();r=copy.deepcopy(old.rows.data[0]);before=copy.deepcopy(r)
    observed=helper.observe_row(initial,r);assert initial==helper.empty_counts()and r==before and observed!=initial
    untouched_counts=copy.deepcopy(observed);helper.observe_row(observed,dict(record_type='same_episode_original_catalog_route'));assert observed==untouched_counts
    for obj in(old,patch):
        obj.ids=[];obj.close=lambda *a:None;obj.close_routes=lambda *a:None;obj.events=dict(natural_complete_intervals=3,complete_kinematic_bounds_met=2)
        obj.reason_counts={};obj.term_controls=0;obj.timeout_controls=0;obj.errors=[]
    old_final=old.finish();new_final=patch.finish();published=new_final.pop('published_moving_standing_counts')
    assert old_final==new_final and published['source_row_field_mapping']==assessor.SPLIT_MAPPING
    assert published['book_constructor_model_label']=='BOOK_LABEL_NOT_POLICY_LOAD_PROOF'
    assert published['phase_reference_root_vs_COM_worldgetter_gap_still_unresolved']is True
    proof=dict(kind='SOURCE_ONLY_STATELESS_SYNTHETIC_OBSERVER_TESTS_NOT_SDK_OR_ACTUAL_PAIR4',all_passed=True,
        unchanged_original_methods_AST=untouched,original_close_kinematic_acceptance_and_group_label_AST_unchanged=True,
        original_emitted_rows_before_writer_identical=True,record_counted_at_existing_append_point=True,
        natural_complete_and_accepted_booleans_not_recomputed=True,standing_label_not_speed_proxy=True,
        stateless_row_and_input_counts_unchanged=True,partial_and_route_rows_not_accepted=True,
        published_to_existing_book_finish_dict=True,source_row_SHA_unchanged_not_actor_identity=True,
        actual_Torch_SDK_PT_NPZ_JSONL_oldraw_SSH_C_GO_or_Git_operations=0,
        original_sources_edited=False,future_pair4_only_not_pair2_pair3_rerun=True)
    put('W35_SPLIT_OBSERVER_STDLIB_SOURCE_PROOF_V1.json',proof)
    files=[book,worker,B/'rm70_published_split_observer_v1.py']
    index=dict(kind='UNUSED_FUTURE_PAIR4_METADATA_OBSERVER_OVERLAY_NOT_DEPLOYED_NOT_ACTUAL_ASSESSMENT',
        original_book=row(OLD/'rm70_intervals227.py'),original_worker=row(OLD/'worker_five_original_n80.py'),
        overlay_sibling_files=[row(p)for p in files],book_module_name='rm70_intervals227_split_metadata_v1',
        integration='After copying original parent software to a NEW unused pair4 source directory and BEFORE packaging/hash Task/worker manifests, overlay exactly these three siblings. Never edit consumed PAIR1_RETENTION_EVAL_SOURCE_V3/V8/pair2/pair3.',
        import_resolution='Only W35 branch imports unique additive module; avoids old runtime/lib rm70_intervals227 shadowing without editing shared libraries',
        row_field_origin=dict(group='original book.open L84 cmd.is_standing_env -> close L155 standing',
            eligibility='original close L150 complete=natural&known&~term&~timeout -> L162 natural_complete_nonterminal_interval',
            accepted='original close L142 kin unchanged -> L163 complete_interval_bounds_fact=complete&kin',
            record='original close L166 record_type same_UID_original_RM70_command'),
        published_location='FINAL.skill.original_RM70_interval_route_facts.published_moving_standing_counts',
        evidence_scope='Original counts only, no matched baseline UID/predicate/worldgetter validation, no full-RM70 graduation; assessor remains conservative when reference gaps persist',
        assessor_sha=row(B.parent/'assess_pair4_retention_closed_metadata_v1.py')['SHA'],
        proof=row(B/'W35_SPLIT_OBSERVER_STDLIB_SOURCE_PROOF_V1.json'),
        actual_overlay_deployed=False,actual_best_report_published=False,source_test_executed_only=True)
    put('FINAL_W35_SPLIT_OBSERVER_SOURCE_INDEX_V1.json',index)
    print(json.dumps(dict(index=str(B/'FINAL_W35_SPLIT_OBSERVER_SOURCE_INDEX_V1.json'),overlay_files=index['overlay_sibling_files'],
        original_metric_reset_RNG_action_reward_clock_changes=0,actual_SDK_model_raw_or_best_operations=0),indent=2))
if __name__=='__main__':main()
