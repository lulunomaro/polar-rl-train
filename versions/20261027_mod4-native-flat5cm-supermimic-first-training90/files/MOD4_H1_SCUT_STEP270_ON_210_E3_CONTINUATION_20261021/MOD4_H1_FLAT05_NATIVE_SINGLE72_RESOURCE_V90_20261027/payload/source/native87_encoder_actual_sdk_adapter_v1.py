"""Pinned actual ObservationManager6.1.14 API; no observation compute or scene."""
from pathlib import Path
import ast,copy,hashlib,json
from types import SimpleNamespace
EXPECTED_OBSERVATION_MANAGER_SHA='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8'
def require(v,message):
 if not v:raise ValueError(message)

def actual_encoder_joint_names(env,names,*,expected_leg_order=None):
 """Read resolved observation term IDs, separate from actuator physical order.

 The pinned SDK exposes active_terms as a property and stores matching resolved
 term configs in _group_obs_term_cfgs. _prepare_terms resolves each term BEFORE
 appending its name/config to these parallel lists. No get_term_cfg exists.
 """
 from actual_DR_memory_getter_v1 import indices
 names=tuple(names);require(len(names)==30 and len(set(names))==30,'actual30 unique robot names required')
 manager=env.observation_manager
 groups=manager.active_terms
 require(isinstance(groups,dict) and 'policy' in groups,'actual SDK policy observation group absent')
 term_names=groups['policy'];term_cfgs=manager._group_obs_term_cfgs['policy']
 require(isinstance(term_names,list) and isinstance(term_cfgs,list) and len(term_names)==len(term_cfgs),'actual SDK parallel term name/config layout differs')
 require(term_names.count('leg_pos')==1,'exactly one actual policy leg_pos term required')
 cfg=term_cfgs[term_names.index('leg_pos')]
 require(isinstance(cfg.params,dict) and 'asset_cfg' in cfg.params,'actual leg_pos resolved asset config absent')
 asset=cfg.params['asset_cfg']
 require(asset.name=='robot' and asset.preserve_order is True,'original robot preserve_order encoder configuration required')
 ids=indices(asset.joint_ids,len(names))
 require(len(ids)==4 and all(type(i) is int for i in ids) and len(set(ids))==4 and all(0<=i<len(names) for i in ids),'four unique resolved encoder joint IDs required')
 result=tuple(names[i] for i in ids)
 if expected_leg_order is None:
  import mod4_task as original_task
  expected_leg_order=tuple(original_task.LEG_ORDER)
 require(result==tuple(expected_leg_order),'actual resolved encoder order differs from original preserve_order LEG_ORDER')
 return result

def _literal(source,name):
 t=ast.parse(source)
 values=[n.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id==name for a in n.targets)]
 require(len(values)==1,'one original literal '+name+' required');return ast.literal_eval(values[0])

def actual_source_view(source):
 """Execute ONLY exact SDK property and field-init/append AST fragments.

 This skips ManagerBase/scene construction and term resolution. Fixture term
 configs are already resolved metadata and are explicitly not runtime evidence.
 """
 tree=ast.parse(source);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ObservationManager')
 require(not any(isinstance(n,ast.FunctionDef) and n.name=='get_term_cfg' for n in cls.body),'reviewed SDK unexpectedly has get_term_cfg')
 prop=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='active_terms')
 require(any(isinstance(d,ast.Name) and d.id=='property' for d in prop.decorator_list),'actual active_terms must be property')
 prep=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_prepare_terms')
 attrs=('_group_obs_term_names','_group_obs_term_cfgs')
 def attr(node,name):return isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self' and node.attr==name
 initial=[];group_init=[];append=[]
 for name in attrs:
  a=[n for n in prep.body if isinstance(n,ast.AnnAssign) and attr(n.target,name)]
  b=[n for n in ast.walk(prep) if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Subscript) and attr(n.targets[0].value,name)]
  c=[n for n in ast.walk(prep) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='append' and isinstance(n.value.func.value,ast.Subscript) and attr(n.value.func.value.value,name)]
  require(len(a)==len(b)==len(c)==1,'actual SDK field-init/append source is ambiguous '+name)
  initial+=a;group_init+=b;append+=c
 resolve=[n for n in ast.walk(prep) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='_resolve_common_term_cfg']
 require(len(resolve)==1 and all(n.lineno>resolve[0].lineno for n in append),'actual SDK must resolve cfg before appending')
 args=lambda names:ast.arguments(posonlyargs=[],args=[ast.arg(arg=n) for n in names],vararg=None,kwonlyargs=[],kw_defaults=[],kwarg=None,defaults=[])
 init=ast.FunctionDef(name='__init__',args=args(['self','group_name']),body=initial+group_init,decorator_list=[])
 add=ast.FunctionDef(name='append_resolved_metadata_fixture',args=args(['self','group_name','term_name','term_cfg']),body=append,decorator_list=[])
 view=ast.ClassDef(name='ActualSourceObservationManagerView',bases=[],keywords=[],body=[prop,init,add],decorator_list=[])
 module=ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(view)],type_ignores=[]))
 ns={};exec(compile(module,'<pinned_actual_ObservationManager_API_fragments>','exec'),ns)
 lineage=dict(active_terms_lines=[prop.lineno,prop.end_lineno],prepare_terms_resolve_line=resolve[0].lineno,
              actual_field_fragment_lines=[[n.lineno,n.end_lineno] for n in initial+group_init+append],
              exact_fragment_AST_SHA=hashlib.sha256(ast.dump(ast.Module(body=[prop,*initial,*group_init,*append],type_ignores=[])).encode()).hexdigest())
 return ns['ActualSourceObservationManagerView'],lineage

def source_API_CPU_check(observation_manager_path,expected_SHA,mod4_task_source_path,joint_names):
 path=Path(observation_manager_path);raw=path.read_bytes();SHA=hashlib.sha256(raw).hexdigest()
 require(expected_SHA==EXPECTED_OBSERVATION_MANAGER_SHA==SHA,'actual installed SDK observation_manager source SHA differs')
 view,lineage=actual_source_view(raw)
 order=tuple(_literal(Path(mod4_task_source_path).read_bytes(),'LEG_ORDER'))
 require(len(order)==4 and len(set(order))==4,'original LEG_ORDER must be four unique names')
 names=tuple(joint_names);require(all(n in names for n in order),'source expected30 names omit original encoder joint')
 manager=view('policy')
 manager.append_resolved_metadata_fixture('policy','before',SimpleNamespace(params={}))
 manager.append_resolved_metadata_fixture('policy','leg_pos',SimpleNamespace(params=dict(asset_cfg=SimpleNamespace(name='robot',preserve_order=True,joint_ids=[names.index(n) for n in order]))))
 manager.append_resolved_metadata_fixture('policy','after',SimpleNamespace(params={}))
 result=actual_encoder_joint_names(SimpleNamespace(observation_manager=manager),names,expected_leg_order=order)
 require(result==order,'actual-source API fixture encoder mapping differs')
 return dict(passed=True,actual_installed_observation_manager_source_SHA=SHA,actual_installed_source_path=str(path),
   actual_source_API_fragments_checked=True,source_fragment_lineage=lineage,expected_encoder_names=list(order),
   actual_encoder_source_fixture_names=list(result),fixture_only=True,actual_scene_or_runtime_encoder_resolution=False,
   no_get_term_cfg_no_observation_compute_no_model_or_GPU=True)
