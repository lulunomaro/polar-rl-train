"""Type/MRO/code-origin metadata for ALREADY created objects, never creates SDK.

No file IO/import of SDK/Torch/inspect, instance getter, method invocation,
registry or SimulationContext query. Passing objects is not construction or
execution authorization. A future caller must supply its original objects.
"""
import types

METHODS={'robot':('_apply_actuator_model','write_data_to_sim'),
         'legs':('compute','_clip_effort'),'wheels':('compute','_clip_effort')}
FIELDS={'robot':('_joint_effort_target_sim',),
        'legs':('stiffness','damping','effort_limit','velocity_limit','_saturation_effort',
                '_vel_at_effort_lim','_joint_vel','episode_scale','step_scale')}
FIELDS['wheels']=FIELDS['legs']


def class_label(cls):
    # Bypass user/metaclass attribute hooks; metadata from intrinsic type slots.
    return dict(module=type.__getattribute__(cls,'__module__'),
                qualname=type.__getattribute__(cls,'__qualname__'))


def method_owner(cls,name):
    chain=type.__getattribute__(cls,'__mro__')
    for owner in chain:
        slots=type.__getattribute__(owner,'__dict__')
        if name not in slots:continue
        value=slots[name];kind=type(value).__name__
        if type(value) in (classmethod,staticmethod):
            fn=value.__func__;ordinary=False
        elif type(value) is types.FunctionType:
            fn=value;ordinary=True
        else:
            return dict(method=name,status='UNKNOWN_UNSUPPORTED_DESCRIPTOR_OR_NATIVE',
                        owner=class_label(owner),descriptor_kind=kind,
                        no_descriptor_bound_or_called=True)
        if type(fn) is not types.FunctionType:
            return dict(method=name,status='UNKNOWN_NON_PYTHON_FUNCTION',owner=class_label(owner),descriptor_kind=kind)
        code=fn.__code__;abstract=fn.__dict__.get('__isabstractmethod__',False)
        if type(abstract)is not bool:
            return dict(method=name,status='UNKNOWN_NONBOOL_ABSTRACT_FLAG',owner=class_label(owner))
        result=dict(method=name,status='EXISTING_PYTHON_FUNCTION_OWNER_OBSERVED',
            owner=class_label(owner),descriptor_kind=kind,
            is_ordinary_instance_function=ordinary,is_abstract=abstract,
            code_filename=code.co_filename,code_firstlineno=code.co_firstlineno,
            code_name=code.co_name,arguments=list(code.co_varnames[:code.co_argcount+code.co_kwonlyargcount]),
            positional_only_count=code.co_posonlyargcount,defaults_count=len(fn.__defaults__ or ()),
            has_varargs=bool(code.co_flags&4),has_varkw=bool(code.co_flags&8),
            no_method_or_descriptor_call=True,source_bytes_AST_not_read_or_bound=True)
        result['candidate_for_later_exact_source_pin']=ordinary and not abstract
        return result
    return dict(method=name,status='UNKNOWN_METHOD_ABSENT_FROM_ACTUAL_MRO')


def plain_field_types(obj,names):
    cls=type(obj)
    descriptor=None
    for owner in type.__getattribute__(cls,'__mro__'):
        slots=type.__getattribute__(owner,'__dict__')
        if '__dict__'in slots:
            descriptor=slots['__dict__'];break
    if type(descriptor)is not types.GetSetDescriptorType:
        return dict(status='UNKNOWN_NO_STANDARD_INSTANCE_DICT',field_values_not_accessed=True)
    values=descriptor.__get__(obj,cls)
    return dict(status='EXISTING_PLAIN_INSTANCE_DICT_FIELD_TYPES_ONLY',fields={n:
        dict(present=n in values,type=class_label(type(values[n]))if n in values else None)
        for n in names},shape_device_tensor_contents_properties_not_read=True)


def record_existing_instances(robot,legs,wheels,*,already_retained_manager_name=None,
                              manager_name_origin='UNKNOWN'):
    objects=dict(robot=robot,legs=legs,wheels=wheels);rows={}
    for name,obj in objects.items():
        cls=type(obj)
        rows[name]=dict(concrete_type=class_label(cls),
            actual_MRO=[class_label(c)for c in type.__getattribute__(cls,'__mro__')],
            methods=[method_owner(cls,m)for m in METHODS[name]],
            plain_field_types=plain_field_types(obj,FIELDS[name]))
    qualified=all(m.get('candidate_for_later_exact_source_pin',False)
                  for row in rows.values()for m in row['methods'])
    return dict(status='EXISTING_INSTANCE_OWNER_METADATA_ONLY',objects=rows,
        already_retained_manager_name=already_retained_manager_name,
        manager_name_origin=manager_name_origin,
        manager_context_not_queried=True,declared_registry_not_called_or_assumed=True,
        ordinary_nonabstract_owner_names_available=qualified,
        actual_source_bytes_AST_semantics_and_compute_apply_timing_passed=False,
        runtime_hook_installable=False,actual_GPU_fullstate_or_skill_ready=False,
        constructor_getter_actor_effort_or_physics_calls=0,
        actual_sdk_or_Torch_module_imports=0)
