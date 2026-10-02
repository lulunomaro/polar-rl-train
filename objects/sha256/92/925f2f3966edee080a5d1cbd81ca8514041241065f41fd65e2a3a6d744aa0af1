function run_mod4_wbr()
% MOD4 read-only MATLAB study based on HelloWorld whole-body dynamics.
here = fileparts(mfilename('fullpath'));
root = fileparts(here);
out = fullfile(here,'results');
figDir = fullfile(out,'figures');
if ~isfolder(out), mkdir(out); end
if ~isfolder(figDir), mkdir(figDir); end
logPath = fullfile(out,'progress.txt');
write_progress(logPath,'START: loading real MOD4 CAD mass and geometry');
P = jsondecode(fileread(fullfile(here,'mod4_extracted_parameters.json')));
if ~isfile(fullfile(here,'wbr_linear_matrices.m'))
    write_progress(logPath,'SYMBOLIC: generating upstream whole-body linearizer');
    build_wbr_linearizer(fullfile(root,'reference_repos','WBR_simulation_20260917'),here);
end
Ts = .002;
% Bryson-style initial tuning, explicitly an engineering design choice.
Q = diag([120,500,100,30,450,15,450,15,9000,150]);
R = diag([12,12,1.5,1.5]);
poses = P.poses;
[~,nominalIndex] = min(abs([poses.leg_length_m]-.275));
nom = poses(nominalIndex);
sys = make_system(P,nom,nom,Ts,Q,R);
assert(sys.controllability_rank==10,'Nominal whole-body model is not fully controllable.');
assert(sys.max_discrete_pole < 1,'Nominal discrete controller is unstable.');
write_progress(logPath,'LQR: sweeping 6x6 left/right actual leg lengths');
indices = unique(round(linspace(1,numel(poses),6)));
schedule = struct([]);
for il=indices
    for ir=indices
        ss0=make_system(P,poses(il),poses(ir),Ts,Q,R);
        schedule=append_struct(schedule,struct('left_length_m',poses(il).leg_length_m,'right_length_m',poses(ir).leg_length_m, ...
            'K',ss0.K,'Ud',ss0.Ud,'trim_leg_lean_deg',rad2deg(ss0.trim),'trim_body_pitch_deg',0, ...
            'controllability_rank',ss0.controllability_rank,'max_discrete_pole',ss0.max_discrete_pole, ...
            'trim_residual',ss0.trim_residual));
    end
end
write_progress(logPath,'CLOSED LOOP: stand, acceleration, push, sinusoidal yaw, slope load');
caseNames={'stand_recovery','flat_accel_brake','push_20N','yaw_sine_6rad_s','slope_load_12deg','slope_load_12deg_feedforward'};
cases=struct([]);
traces=struct();
for i=1:numel(caseNames)
    [st,tr]=simulate_case(P,nom,sys,caseNames{i},500,500,1,0,1,0);
    cases=append_struct(cases,st);
    traces.(caseNames{i})=tr;
    save_trace(fullfile(out,[caseNames{i} '.csv']),tr);
end
write_progress(logPath,'ROBUSTNESS: 120 seeded model trials with spring 300-700 N');
rng(20260917,'twister');
trials=struct([]);
for i=1:120
    fL=300+400*rand; fR=300+400*rand;
    if mod(i,12)==1, fL=300; fR=700; end
    if mod(i,12)==2, fL=700; fR=300; end
    massScale=.85+.30*rand;
    inertiaScale=.8+.4*rand;
    delay=round(10*rand/2); % 0-10 ms at 2 ms tick
    mu=.45+.55*rand;
    noise=.0015;
    perturbed=P;
    pertNom=nom;
    pertNom.body_mass_kg=nom.body_mass_kg*massScale;
    pertNom.left_leg_mass_kg=nom.left_leg_mass_kg*massScale;
    pertNom.right_leg_mass_kg=nom.right_leg_mass_kg*massScale;
    pertNom.body_pitch_inertia_kg_m2=nom.body_pitch_inertia_kg_m2*inertiaScale;
    pertNom.leg_pitch_inertia_kg_m2=nom.leg_pitch_inertia_kg_m2*inertiaScale;
    pertNom.total_yaw_inertia_kg_m2=nom.total_yaw_inertia_kg_m2*inertiaScale;
    perturbed.total_mass_kg=pertNom.body_mass_kg+pertNom.left_leg_mass_kg+pertNom.right_leg_mass_kg+2*pertNom.wheel_mass_kg;
    actual=make_system(perturbed,pertNom,pertNom,Ts,Q,R);
    % Reuse nominal controller and trim; do not secretly retune for plant DR.
    actual.K=sys.K; actual.Q=Q; actual.R=R;
    actual.trim=sys.trim; actual.trim_body=sys.trim_body; actual.Ud=sys.Ud;
    trimState=zeros(10,1);trimState([5,7])=sys.trim;
    actual.bias=actual.A*trimState+actual.B*sys.Ud+actual.zero_offset_acceleration;
    [st,~]=simulate_case(perturbed,pertNom,actual,'flat_accel_brake',fL,fR,mu,delay,1,noise);
    trials=append_struct(trials,struct('trial',i,'spring_left_n',fL,'spring_right_n',fR, ...
        'mass_scale',massScale,'inertia_scale',inertiaScale,'delay_ms',delay*2,'friction',mu, ...
        'bounded',st.bounded,'speed_rms_error_m_s',st.speed_rms_error_m_s, ...
        'max_body_pitch_deg',st.max_body_pitch_deg,'wheel_peak_nm',max(st.peak_motor_torque_nm(1:2)), ...
        'leg_peak_nm',max(st.peak_motor_torque_nm(3:6)), 'motor_saturation_fraction',st.motor_saturation_fraction));
end
write_progress(logPath,'MECHANICS: gas spring, motor load, smooth terrain and jump energy');
mechanics=mechanical_study(P,poses);
write_progress(logPath,'SPRING UNCERTAINTY: testing unknown 300-700 N force in vertical linkage dynamics');
[heightStudy,heightTraces]=simulate_gas_height(P);
traces.gas_height=heightTraces;
write_progress(logPath,'SIMULINK: checking discrete stand response against MATLAB');
simulinkCheck=build_mod4_balance_model(here,sys,traces.stand_recovery);
springExtremes=struct([]);
for forces=[300 500 700;300 500 700]
    [st,~]=simulate_case(P,nom,sys,'flat_accel_brake',forces(1),forces(2),.75,0,1,0);
    springExtremes=append_struct(springExtremes,st);
end
summary=struct('generated_at',char(datetime('now','Format','yyyy-MM-dd HH:mm:ss')), ...
    'matlab_version',version,'reference_repository',P.reference_repository,'reference_commit',P.reference_commit, ...
    'source_mjcf_sha256',P.source_mjcf_sha256,'total_mass_kg',P.total_mass_kg, ...
    'model_scope','10-state small-angle fixed-leg-length rolling model; no roll, wheel lift-off, step impact or flight contact.', ...
    'gas_scope','Per spring F(q)=Fref-3500*q. Model sweep assumes axial leg-length regulation and correct static force compensation; not sensorless hardware robustness.', ...
    'controller_period_s',Ts,'nominal_pose',nom,'nominal_system',sys,'schedule',schedule,'cases',cases, ...
    'spring_extreme_cases',springExtremes,'robustness_trials',trials, ...
    'robustness',struct('n',numel(trials),'bounded_count',sum([trials.bounded]), ...
        'worst_speed_rms_error_m_s',max([trials.speed_rms_error_m_s]),'worst_body_pitch_deg',max([trials.max_body_pitch_deg]), ...
        'max_motor_saturation_fraction',max([trials.motor_saturation_fraction])), ...
    'mechanics',mechanics,'gas_height_study',heightStudy,'simulink_cross_check',simulinkCheck);
save(fullfile(out,'mod4_wbr_simulation.mat'),'summary','traces','P','-v7.3');
write_json(fullfile(out,'summary.json'),summary);
writematrix(sys.A,fullfile(out,'A_continuous.csv'));
writematrix(sys.B,fullfile(out,'B_continuous.csv'));
writematrix(sys.K,fullfile(out,'K_discrete.csv'));
writematrix(sys.Ud,fullfile(out,'trim_feedforward.csv'));
write_progress(logPath,'PLOTS: exporting MATLAB figures');
make_figures(figDir,summary,traces);
refine_results();
audit_armature();
write_progress(logPath,'DONE: MATLAB simulation and figures saved');
fprintf('MOD4_MATLAB_DONE: %s\n',out);
disp(cases);
end

function S=make_system(P,left,right,Ts,Q,R)
cb=left.body_com_from_hip_xz_m;
lc=norm(cb); phic=atan2(cb(1),cb(2));
param=[9.81,P.wheel_radius_m,P.track_m/2,left.leg_length_m,right.leg_length_m, ...
    norm(left.leg_com_from_wheel_xz_m),norm(right.leg_com_from_wheel_xz_m), ...
    norm(left.leg_com_from_hip_xz_m),norm(right.leg_com_from_hip_xz_m),lc,phic, ...
    left.wheel_mass_kg,left.left_leg_mass_kg,right.right_leg_mass_kg,left.body_mass_kg, ...
    left.wheel_pitch_inertia_kg_m2, ...
    left.leg_pitch_inertia_kg_m2,right.leg_pitch_inertia_kg_m2,left.body_pitch_inertia_kg_m2, ...
    (left.total_yaw_inertia_kg_m2+right.total_yaw_inertia_kg_m2)/2, ...
    left.leg_active_armature_total_kg_m2,right.leg_active_armature_total_kg_m2, ...
    left.wheel_armature_kg_m2,right.wheel_armature_kg_m2];
[M,Bu,Bx,b0,T]=wbr_linear_matrices(param);
E=zeros(3,10);E(1,5)=1;E(2,7)=1;E(3,9)=1;
A=zeros(10); B=zeros(10,4);
A(sub2ind([10,10],1:2:9,2:2:10))=1;
A(2:2:10,:)=T*(M\Bx)*E;
B(2:2:10,:)=T*(M\Bu);
% Hold the body horizontal, shift only the virtual legs to put total COM
% over the axle, and solve the four torque biases. Report the trim residual.
trim_solution=[Bu,Bx*[1;1;0]]\(-b0);
Ud=trim_solution(1:4); trim=trim_solution(5);
trim_residual=norm(Bu*Ud+Bx*[trim;trim;0]+b0);
AB=expm([A B;zeros(4,14)]*Ts);
Ad=AB(1:10,1:10); Bd=AB(1:10,11:14);
[K,Sric,poles]=dlqr(Ad,Bd,Q,R);
Eforce=zeros(10,1);Eforce(2:2:10)=T*(M\[0;0;1;0;0]);
zeroOffset=zeros(10,1);zeroOffset(2:2:10)=T*(M\b0);
ctrl=ctrb(A,B);singularValues=svd(ctrl);
rankC=sum(singularValues>max(size(ctrl))*eps(singularValues(1)));
S=struct('A',A,'B',B,'Ad',Ad,'Bd',Bd,'K',K,'Q',Q,'R',R,'Ud',Ud,'trim',trim,'trim_body',0, ...
    'trim_residual',trim_residual,'mass_matrix_condition',cond(M), ...
    'controllability_rank',rankC,'max_discrete_pole',max(abs(poles)), ...
    'pole_real',real(poles),'pole_imag',imag(poles),'riccati_matrix',Sric,'Eforce',Eforce,'Ts',Ts, ...
    'zero_offset_acceleration',zeroOffset,'bias',zeros(10,1));
end

function [stats,tr]=simulate_case(P,pose,S,name,fL,fR,mu,delay,torqueScale,noise)
dt=S.Ts; duration=12; n=round(duration/dt)+1;
t=(0:n-1)'*dt;
v=zeros(n,1); omega=zeros(n,1); force=zeros(n,1);
if strcmp(name,'stand_recovery')
    v(:)=0;
else
    v=1.2*smoothstep((t-1)/2).*(1-smoothstep((t-7)/2));
end
if strcmp(name,'push_20N'),v=.6*smoothstep((t-1)/2);force(t>=5&t<5.3)=20;end
if strcmp(name,'yaw_sine_6rad_s'),v=.4*smoothstep(t/2);omega=6*sin(2*pi*.20*t).*smoothstep(t);end
if startsWith(name,'slope_load_12deg'),force=-P.total_mass_kg*9.81*sin(deg2rad(12))*smoothstep((t-3)/2);end
ref=zeros(n,10);ref(:,1)=cumtrapz(t,v);ref(:,2)=v;ref(:,3)=cumtrapz(t,omega);ref(:,4)=omega;
feedforward=zeros(n,4);
if endsWith(name,'_feedforward')
    legLean=zeros(10,1);legLean([5,7])=1;
    map=[S.B(2:2:10,:),S.A(2:2:10,:)*legLean];
    correction=(map\(-S.Eforce(2:2:10)*force'))';
    feedforward=correction(:,1:4);ref(:,5)=correction(:,5);ref(:,7)=correction(:,5);
    ref(:,6)=gradient(ref(:,5),dt);ref(:,8)=gradient(ref(:,7),dt);
end
X=zeros(n,10);X(1,9)=deg2rad(5);X(1,5)=deg2rad(2);X(1,7)=deg2rad(2);
if strcmp(name,'yaw_sine_6rad_s'),X(1,:)=0;end
motor=zeros(n,6);virtual=zeros(n,4);requested=zeros(n,6);sat=false(n,6);
J=pose.virtual_jacobian;
gTau=pose.static_gravity_motor_torque_nm(:);
gasF=[fL,fR]-3500*pose.gas_slide_m;
% Replace the static virtual-angle torque by trimmed whole-body Ud.
gravityVirtual=J(1:2,:)'\gTau;
baseL=gTau-J(3,:)'*gasF(1)+J(2,:)'*(S.Ud(3)-gravityVirtual(2));
baseR=gTau-J(3,:)'*gasF(2)+J(2,:)'*(S.Ud(4)-gravityVirtual(2));
Ed=dt*S.Eforce;
failed=false;
for k=1:n-1
    sensed=X(max(1,k-delay),:)';
    sensed([5,7,9])=sensed([5,7,9])+noise*randn(3,1);
    u=S.Ud+feedforward(k,:)'-S.K*(sensed-ref(k,:)');
    wheelV=[X(k,2)-P.track_m/2*X(k,4), X(k,2)+P.track_m/2*X(k,4)]/P.wheel_radius_m;
    wheelCap=motor_cap(P.motor_parameters.wheel_motor,wheelV,torqueScale);
    wheelCap=min(wheelCap,mu*P.total_mass_kg*9.81/2*P.wheel_radius_m);
    wheel=min(max(u(1:2)',-wheelCap),wheelCap);
    legL=baseL+J(2,:)'*(u(3)-S.Ud(3));
    legR=baseR+J(2,:)'*(u(4)-S.Ud(4));
    % Joint velocity along constant-length virtual leg rotation.
    qdotL=J(1:2,:)\[0;X(k,6)-X(k,10)];
    qdotR=J(1:2,:)\[0;X(k,8)-X(k,10)];
    legCapL=motor_cap(P.motor_parameters.leg_motor,qdotL',torqueScale)';
    legCapR=motor_cap(P.motor_parameters.leg_motor,qdotR',torqueScale)';
    appliedL=min(max(legL,-legCapL),legCapL);
    appliedR=min(max(legR,-legCapR),legCapR);
    applied=[wheel,appliedL',appliedR'];
    ask=[u(1:2)',legL',legR'];
    motor(k,:)=applied;requested(k,:)=ask;sat(k,:)=abs(applied-ask)>1e-7;
    deltaL=J(1:2,:)'\(appliedL-baseL);
    deltaR=J(1:2,:)'\(appliedR-baseR);
    actualU=[wheel';S.Ud(3)+deltaL(2);S.Ud(4)+deltaR(2)];
    virtual(k,:)=actualU';
    X(k+1,:)=(S.Ad*X(k,:)'+S.Bd*(actualU-S.Ud)+Ed*force(k)+dt*S.bias)';
    if any(~isfinite(X(k+1,:))) || max(abs(X(k+1,[5,7,9])))>deg2rad(35) || abs(X(k+1,2))>8
        failed=true; X(k+2:end,:)=X(k+1,:);motor(k+1:end,:)=motor(k,:); break
    end
end
motor(n,:)=motor(n-1,:);
trimPitch=rad2deg(X(:,9)+S.trim_body);
pitchError=rad2deg(X(:,9));
acc=gradient(X(:,2),dt);
stats=struct('name',name,'spring_left_n',fL,'spring_right_n',fR,'friction',mu,'delay_ms',delay*dt*1000, ...
    'bounded',~failed,'speed_rms_error_m_s',sqrt(mean((X(:,2)-v).^2)), ...
    'yaw_rate_rms_error_rad_s',sqrt(mean((X(:,4)-omega).^2)), ...
    'max_body_pitch_deg',max(abs(trimPitch)),'max_pitch_error_deg',max(abs(pitchError)), ...
    'final_pitch_error_deg',pitchError(end),'max_acceleration_m_s2',max(abs(acc)), ...
    'peak_motor_torque_nm',max(abs(motor),[],1),'rms_motor_torque_nm',sqrt(mean(motor.^2,1)), ...
    'peak_requested_motor_torque_nm',max(abs(requested),[],1), ...
    'motor_saturation_fraction',mean(sat,'all'),'static_motor_torque_nm',[S.Ud(1:2)',baseL',baseR'], ...
    'post_startup_peak_motor_torque_nm',max(abs(motor(t>=2,:)),[],1), ...
    'post_startup_max_body_pitch_deg',max(abs(trimPitch(t>=2))), ...
    'post_startup_speed_rms_error_m_s',sqrt(mean((X(t>=2,2)-v(t>=2)).^2)), ...
    'steady_speed_rms_error_m_s',sqrt(mean((X(t>=4&t<=6,2)-v(t>=4&t<=6)).^2)), ...
    'post_startup_peak_acceleration_m_s2',max(abs(acc(t>=2))));
tr=struct('t',t,'X',X,'ref',ref,'motor',motor,'requested',requested,'virtual',virtual,'pitch_deg',trimPitch,'force_n',force,'acceleration',acc);
end

function cap=motor_cap(p,omega,scale)
% Conservative symmetric torque-speed cap; regeneration/current/thermal are
% not measured. This is an engineering envelope, not a supplier full curve.
cap=scale*max(0,min(p.peak_torque_nm,p.envelope_intercept_nm-p.envelope_slope_nm_s_rad*abs(omega)));
end

function M=mechanical_study(P,poses)
loads=struct([]);
for pose=poses'
    J=pose.virtual_jacobian; g=pose.static_gravity_motor_torque_nm(:);
    for f=[300,500,700]
        actual=f-3500*pose.gas_slide_m;
        tau=g-J(3,:)'*actual;
        loads=append_struct(loads,struct('leg_length_m',pose.leg_length_m,'hip_rad',pose.hip_rad,'crank_rad',pose.crank_rad, ...
            'force_ref_n',f,'spring_force_at_pose_n',actual,'eye_length_m',pose.spring_eye_length_m, ...
            'hip_static_nm',tau(1),'crank_static_nm',tau(2),'gravity_hip_nm',g(1),'gravity_crank_nm',g(2), ...
            'spring_hip_nm',-J(3,1)*actual,'spring_crank_nm',-J(3,2)*actual));
    end
end
% Smoothed step/undulation demand is an inverse-dynamics estimate. It does
% not include wheel-edge contact, impact, leg inertia or full VMC tracking.
[~,ix]=min(abs([poses.leg_length_m]-.275));nom=poses(ix);
J=nom.virtual_jacobian;g=nom.static_gravity_motor_torque_nm(:);
t=(0:.002:8)'; z=.025*sin(2*pi*.8*t); zdd=-(2*pi*.8)^2*z;
dynamic=struct([]);
for f=[300,500,700]
    base=g-J(3,:)'*(f-3500*nom.gas_slide_m);
    tau=repmat(base',numel(t),1)+(P.total_mass_kg/2*zdd)*J(1,:);
    dynamic=append_struct(dynamic,struct('force_ref_n',f,'peak_hip_nm',max(abs(tau(:,1))), ...
        'peak_crank_nm',max(abs(tau(:,2))),'rms_hip_nm',sqrt(mean(tau(:,1).^2)), ...
        'rms_crank_nm',sqrt(mean(tau(:,2).^2))));
end
low=poses(1); high=poses(end);stroke=high.leg_length_m-low.leg_length_m;
q0=low.gas_slide_m;q1=high.gas_slide_m;
jumps=struct([]);
for f=[300,500,700]
    gasEnergy=2*(f*(q1-q0)-.5*3500*(q1^2-q0^2));
    for rise=[.15,.20,.25,.30]
        v0=sqrt(2*9.81*rise);
        energy=P.total_mass_kg*9.81*rise;
        liftWork=P.total_mass_kg*9.81*stroke;
        averageF=P.total_mass_kg*9.81*(1+rise/stroke);
        % Equal acceleration over the entire available extension stroke;
        % early/late motion and force losses would increase the peak demand.
        required=0;
        maxRpm=0; minMargin=inf;
        for pose=poses'
            Jp=pose.virtual_jacobian;
            tau=pose.static_gravity_motor_torque_nm(:)-Jp(3,:)'*(f-3500*pose.gas_slide_m) ...
                +Jp(1,:)'*(P.total_mass_kg*9.81*rise/(2*stroke));
            required=max(required,max(abs(tau)));
            v= v0*sqrt(max(0,(pose.leg_length_m-low.leg_length_m)/stroke));
            qdot=Jp(1:2,:)\[v;0];
            cap=motor_cap(P.motor_parameters.leg_motor,qdot',1)';
            minMargin=min(minMargin,min(cap-abs(tau)));
            maxRpm=max(maxRpm,max(abs(qdot))*60/(2*pi));
        end
        jumps=append_struct(jumps,struct('force_ref_n',f,'ballistic_rise_m',rise,'required_launch_speed_m_s',v0, ...
            'kinetic_energy_at_takeoff_j',energy,'average_total_ground_force_n',averageF, ...
            'extension_gravity_work_j',liftWork,'total_ideal_extension_work_j',liftWork+energy, ...
            'minimum_motor_work_j',max(0,liftWork+energy-gasEnergy), ...
            'max_estimated_leg_motor_rpm',maxRpm,'min_torque_speed_margin_nm',minMargin, ...
            'available_extension_stroke_m',stroke,'spring_released_energy_j',gasEnergy, ...
            'estimated_peak_leg_motor_nm',required,'leg_peak_limit_nm',40, ...
            'energy_scope','Ideal extension/ballistic budget, not successful landing or competition step clearance.'));
    end
end
M=struct('static_loads',loads,'undulation_inverse_dynamics',dynamic,'jump_budget',jumps, ...
    'undulation_amplitude_m',.025,'undulation_frequency_hz',.8, ...
    'spring_force_definition','Fref at q=0; 3500 N/m slope; not constant through stroke', ...
    'available_extension_stroke_m',stroke);
end

function make_figures(figDir,S,traces)
set(groot,'defaultFigureVisible','off','defaultAxesFontName','Microsoft YaHei', ...
    'defaultAxesFontSize',10,'defaultLineLineWidth',1.5);
names=setdiff(fieldnames(traces),{'gas_height'},'stable');
for i=1:numel(names)
    tr=traces.(names{i});f=figure('Position',[100 100 1200 780],'Color','w');
    tiledlayout(2,2,'TileSpacing','compact');
    nexttile;plot(tr.t,tr.X(:,2),tr.t,tr.ref(:,2),'--');grid on;ylabel('前向速度 (m/s)');legend('实际','指令','Location','best');
    nexttile;plot(tr.t,tr.pitch_deg,tr.t,rad2deg(tr.X(:,5)+S.nominal_system.trim),tr.t,rad2deg(tr.X(:,7)+S.nominal_system.trim));grid on;ylabel('角度 (deg)');legend('车体俯仰','左虚拟腿','右虚拟腿');
    nexttile;plot(tr.t,tr.motor(:,1:2));grid on;ylabel('轮电机输出扭矩 (N m)');xlabel('时间 (s)');legend('左轮','右轮');
    nexttile;plot(tr.t,tr.motor(:,3:6));grid on;ylabel('腿电机输出扭矩 (N m)');xlabel('时间 (s)');legend('左 hip','左 crank','右 hip','右 crank');
    sgtitle(strrep(names{i},'_',' '),'Interpreter','none');
    exportgraphics(f,fullfile(figDir,[names{i} '.png']),'Resolution',180);close(f);
end
f=figure('Position',[100 100 1200 660],'Color','w');tiledlayout(1,2);
tr=traces.yaw_sine_6rad_s;
nexttile;plot(tr.t,tr.X(:,4),tr.t,tr.ref(:,4),'--');grid on;xlabel('时间 (s)');ylabel('偏航角速度 (rad/s)');legend('实际','正弦指令');
nexttile;plot(tr.t,tr.motor(:,1:2));grid on;xlabel('时间 (s)');ylabel('轮电机扭矩 (N m)');legend('左轮','右轮');title('侧向 / roll 动力学未纳入，不能据此认证高速小陀螺');
exportgraphics(f,fullfile(figDir,'yaw_tracking.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1200 600],'Color','w');tiledlayout(1,2);
a=traces.slope_load_12deg;b=traces.slope_load_12deg_feedforward;
nexttile;plot(a.t,a.ref(:,2),'k--',a.t,a.X(:,2),b.t,b.X(:,2));grid on;legend('指令','纯 LQR','坡度前馈 + LQR');xlabel('时间 (s)');ylabel('速度 (m/s)');
nexttile;plot(a.t,a.pitch_deg,b.t,b.pitch_deg);grid on;legend('纯 LQR','坡度前馈 + LQR');xlabel('时间 (s)');ylabel('车体俯仰 (deg)');
sgtitle('12 deg 坡度等效阻力前馈对比，含轮边/腿角力矩分配');
exportgraphics(f,fullfile(figDir,'slope_feedforward_comparison.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1200 700],'Color','w');tiledlayout(2,2);
L=S.mechanics.static_loads;
for idx=1:4
    nexttile;hold on;
    for F=[300,500,700]
        a=L([L.force_ref_n]==F); x=1000*[a.leg_length_m];
        if idx==1,y=[a.hip_static_nm];elseif idx==2,y=[a.crank_static_nm];elseif idx==3,y=[a.spring_force_at_pose_n];else,y=1000*[a.eye_length_m];end
        plot(x,y,'DisplayName',sprintf('%d N',F));
    end
    grid on;xlabel('虚拟腿长 (mm)');legend('Location','best');
    labels={'hip 静态扭矩 (N m)','crank 静态扭矩 (N m)','当前姿态弹簧力 (N)','弹簧眼距 (mm)'};ylabel(labels{idx});
    if idx<3,yline(20,'--','连续 20');yline(-20,'--');yline(40,':','峰值 40');yline(-40,':');end
end
sgtitle('实际 MOD4 几何 + 300/500/700 N 弹簧');
exportgraphics(f,fullfile(figDir,'spring_torque_scan.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1100 600],'Color','w');
plot(real(S.nominal_system.pole_real),S.nominal_system.pole_imag,'x');hold on;a=linspace(0,2*pi,400);plot(cos(a),sin(a),'--');axis equal;grid on;xlabel('实部');ylabel('虚部');title('离散闭环极点，单位圆内才稳定');
exportgraphics(f,fullfile(figDir,'closed_loop_poles.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1200 620],'Color','w');tiledlayout(1,2);
nexttile;scatter([S.robustness_trials.delay_ms],[S.robustness_trials.speed_rms_error_m_s],36,[S.robustness_trials.spring_left_n],'filled');colorbar;grid on;xlabel('观测延迟 (ms)');ylabel('速度 RMS 误差 (m/s)');title('颜色为左弹簧参考力 (N)');
nexttile;scatter([S.robustness_trials.mass_scale],[S.robustness_trials.max_body_pitch_deg],36,[S.robustness_trials.friction],'filled');colorbar;grid on;xlabel('质量倍率');ylabel('最大车体俯仰 (deg)');title('颜色为摩擦系数');
exportgraphics(f,fullfile(figDir,'model_robustness.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1050 560],'Color','w');hold on;
for F=[300,500,700]
    a=S.mechanics.jump_budget([S.mechanics.jump_budget.force_ref_n]==F);
    plot(1000*[a.ballistic_rise_m],[a.estimated_peak_leg_motor_nm],'-o','DisplayName',sprintf('%d N',F));
end
yline(40,'--','40 N m 峰值');yline(20,':','20 N m 连续');grid on;xlabel('离地后的理想质心上升 (mm)');ylabel('估算最大单腿电机扭矩 (N m)');legend('Location','best');title('起跳预算，不代表台阶/飞坡/着陆已通过');
exportgraphics(f,fullfile(figDir,'jump_budget.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1200 720],'Color','w');tiledlayout(2,2);
for useI=[0,1]
    nexttile;hold on;
    for F=[300 500 700]
        h=traces.gas_height.(sprintf('gas_%d_%d_integral_%d',F,F,useI));
        plot(h.t,1000*h.leg_length,'DisplayName',sprintf('%d N',F));
    end
    plot(h.t,1000*h.reference,'k--','DisplayName','目标');grid on;legend('Location','best');ylabel('虚拟腿长 (mm)');xlabel('时间 (s)');title(sprintf('未知弹簧力，高度积分补偿=%d',useI));
end
for useI=[0,1]
    nexttile;hold on;
    for F=[300 500 700]
        h=traces.gas_height.(sprintf('gas_%d_%d_integral_%d',F,F,useI));
        plot(h.t,h.torque(:,2),'DisplayName',sprintf('%d N',F));
    end
    grid on;legend('Location','best');ylabel('单侧 crank 扭矩 (N m)');xlabel('时间 (s)');title(sprintf('高度积分补偿=%d',useI));
end
sgtitle('300-700 N 未知弹簧力的真实输入变化，竖直等效模型');
exportgraphics(f,fullfile(figDir,'gas_height_uncertainty.png'),'Resolution',180);close(f);
end

function y=smoothstep(x)
x=max(0,min(1,x));y=x.^2.*(3-2*x);
end
function items=append_struct(items,item)
if isempty(items),items=item;else,items(end+1)=item;end
end
function save_trace(path,tr)
T=array2table([tr.t,tr.X,tr.ref(:,[2 4]),tr.pitch_deg,tr.motor,tr.force_n], ...
    'VariableNames',{'time_s','s_m','v_m_s','yaw_rad','yaw_rate_rad_s','alpha_left_rad','alpha_left_rate','alpha_right_rad','alpha_right_rate','pitch_error_rad','pitch_rate','speed_command_m_s','yaw_rate_command_rad_s','body_pitch_deg','left_wheel_nm','right_wheel_nm','left_hip_nm','left_crank_nm','right_hip_nm','right_crank_nm','disturbance_force_n'});
writetable(T,path);
end
function write_progress(path,text)
fid=fopen(path,'a','n','UTF-8');fprintf(fid,'%s %s\n',char(datetime('now','Format','HH:mm:ss')),text);fclose(fid);fprintf('%s\n',text);
end
function write_json(path,value)
fid=fopen(path,'w','n','UTF-8');c=onCleanup(@()fclose(fid));fprintf(fid,'%s\n',jsonencode(value,'PrettyPrint',true));
end
