from pathlib import Path

root = Path(__file__).resolve().parent
t = (root / 'contact_control_baseline.py').read_text(encoding='utf-8')
t = t.replace("p.add_argument('--freeze_leg_after'", "p.add_argument('--solver_pos',type=int,default=16);p.add_argument('--solver_vel',type=int,default=4)\np.add_argument('--freeze_leg_after'")
t = t.replace("app=AppLauncher(args).app", "os.environ['RM_SOLVER_POS']=str(args.solver_pos)\nos.environ['RM_SOLVER_VEL']=str(args.solver_vel)\napp=AppLauncher(args).app")
t = t.replace("robot=env.scene['robot'];dev=env.device;n=env.num_envs", """robot=env.scene['robot'];dev=env.device;n=env.num_envs
    solver_cfg=cfg.scene.robot.spawn.articulation_props
    solver_readback={'position':solver_cfg.solver_position_iteration_count,'velocity':solver_cfg.solver_velocity_iteration_count}
    assert solver_readback=={'position':args.solver_pos,'velocity':args.solver_vel}
    import hashlib
    source_audit={k:hashlib.sha256(Path(__file__).with_name(k).read_bytes()).hexdigest() for k in ['env.json','mod4_task.py','mod4_env.py','skills_isaac.py']}
    checkpoint_sha=hashlib.sha256(Path(args.checkpoint).read_bytes()).hexdigest() if args.checkpoint else None""")
t = t.replace("'approximation':str(prim.GetAttribute('physics:approximation').Get())", """'approximation':str(prim.GetAttribute('physics:approximation').Get()),
          'authored_contact_offset':prim.GetAttribute('physxCollision:contactOffset').Get(),
          'authored_rest_offset':prim.GetAttribute('physxCollision:restOffset').Get()""")
t = t.replace("robot.data.applied_torque[:,wheel_joint_ids],robot.data.joint_vel[:,wheel_joint_ids]],dim=1)", """robot.data.applied_torque[:,wheel_joint_ids],robot.data.joint_vel[:,wheel_joint_ids],
                robot.data.computed_torque[:,leg_joint_ids],robot.data.joint_pos_target[:,leg_joint_ids],
                robot.data.joint_vel_target[:,wheel_joint_ids],f[:,:,:2].reshape(n,4),
                robot.data.body_lin_vel_w[:,wheelids,:2].reshape(n,4)],dim=1)""")
t = t.replace("['wheel_torque_l','wheel_torque_r','wheel_qd_l','wheel_qd_r']", """['wheel_torque_l','wheel_torque_r','wheel_qd_l','wheel_qd_r']+[f'leg_computed_torque_{i}' for i in range(4)]+[f'leg_pd_target_{i}' for i in range(4)]+['wheel_vel_target_l','wheel_vel_target_r','left_fx','left_fy','right_fx','right_fy','left_center_vx','left_center_vy','right_center_vx','right_center_vy']""")
t = t.replace("'checkpoint':args.checkpoint,", "'checkpoint':args.checkpoint,'checkpoint_sha256':checkpoint_sha,'source_sha256':source_audit,'solver_cfg_readback':solver_readback,'diagnostic_only':True,")
t = t.replace("'contract':task.contract_report(),", "'contract':task.contract_report(),'leg_order':list(task.LEG_ORDER),'wheel_order':list(task.WHEEL_ORDER),")
(root/'contact_probe_v2.py').write_text(t,encoding='utf-8')
compile(t,'contact_probe_v2.py','exec')
print('Generated contact_probe_v2.py: syntax passed')
