function result = run_directional_spin_study
% MATLAB study: differential-drive WORLD-directed translation while spinning.
% Scope: exact kinematics + planar no-slip actuator model, NOT the MOD4 PPO,
% full closed-chain balancing/contact physics, or real-robot certification.
% Does not clear the user's workspace, close existing figures, or touch PPO.
D = fileparts(mfilename('fullpath'));
P = jsondecode(fileread(fullfile(D,'PARAMETERS.json')));
fprintf('MATLAB PID %d: directional-spin study started.\n',feature('getpid'));
Vs = [.15 .30 .50]; ws = [1 -1 2 -2];
ideal = struct([]); dynamic = struct([]); demo = []; stress_demo=[]; corrected_demo=[]; n = 0;
% Exact, unclipped kinematics: vary heading and requested world direction.
for V = Vs
    for w = ws
        for alpha = [0 pi/3]
            for phi0 = [0 pi/4 pi/2]
                n = n+1;
                tr = kinematic(V,w,alpha,alpha+phi0,'world',inf);
                m = metrics(tr,alpha,0);
                entry = struct('target_m_s',V,'yaw_rad_s',w, ...
                    'world_direction_rad',alpha,'initial_relative_heading_rad',phi0, ...
                    'full_turn_count',m.full_turn_count, ...
                    'cycle_along_m_s',m.cycle_along_m_s, ...
                    'cycle_cross_m_s',m.cycle_cross_m_s, ...
                    'body_speed_peak_m_s',max(abs(tr.u)), ...
                    'cross_peak_to_peak_m',range(tr.cross), ...
                    'analytic_position_max_error_m',tr.analytic_error);
                if n==1, ideal=entry; else, ideal(n)=entry; end
            end
        end
    end
end
fprintf('Exact kinematics: %d cases including both spin directions.\n',n);
% Negative controls: constant BODY velocity and wrong WORLD direction.
controls.constant_body = metrics(kinematic(.5,2,0,0,'body',inf),0,0);
controls.wrong_direction = metrics(kinematic(.5,2,pi,0,'world',inf),0,0);
controls.body_clipped = metrics(kinematic(.5,2,0,0,'world',.6),0,0);
assert(max(abs([ideal.cycle_along_m_s]-[ideal.target_m_s]))<1e-7);
assert(max(abs([ideal.cycle_cross_m_s]))<1e-7);
assert(abs(controls.constant_body.cycle_along_m_s)<1e-7);
assert(abs(controls.constant_body.cycle_cross_m_s)<1e-7);
assert(abs(controls.wrong_direction.cycle_along_m_s+.5)<1e-7);
assert(controls.body_clipped.cycle_along_m_s<.5);
assert(max([ideal.analytic_position_max_error_m])<1e-6);
% Simplified planar dynamics, actual motor torque-speed clipping.
% Each stress case uses fixed nominal controller, changed plant and lag.
profiles = {'nominal','mass_inertia_plus7p5_gain_minus7p5_lag150ms', ...
    'same_stress_with_world_position_feedback'};
for ip = 1:numel(profiles)
    q = P;
    if ip>=2
        q.mass_kg=P.mass_kg*1.075; q.yaw_inertia_kg_m2=P.yaw_inertia_kg_m2*1.075;
        q.motor_gain=.925; q.actuator_lag_s=.15;
    end
    q.world_feedback_enabled=(ip==3);
    for V = Vs
        for w = ws
            tr = simulate_planar(V,w,q,P,.004);
            m = metrics(tr,q.world_direction_rad,0);
            s = metrics(tr,q.world_direction_rad,3);
            k = numel(dynamic)+1;
            entry=struct('profile',profiles{ip},'world_feedback_enabled',q.world_feedback_enabled, ...
                'target_m_s',V,'yaw_rad_s',w, ...
                'all_turn_count',m.full_turn_count,'all_cycle_along_m_s',m.cycle_along_m_s, ...
                'all_cycles',m.cycles,'steady_turn_count',s.full_turn_count, ...
                'steady_cycle_along_m_s',s.cycle_along_m_s, ...
                'steady_cycle_cross_m_s',s.cycle_cross_m_s,'steady_cycles',s.cycles, ...
                'body_speed_peak_m_s',max(abs(tr.u)), ...
                'wheel_speed_peak_rad_s',max(abs(tr.wheel_speed),[],'all'), ...
                'wheel_torque_peak_Nm',max(abs(tr.torque),[],'all'), ...
                'wheel_torque_rms_Nm',sqrt(mean(tr.torque.^2,1)), ...
                'motor_envelope_clip_fraction',mean(tr.clipped), ...
                'continuous_rating_exceed_fraction',mean(any(abs(tr.torque)>P.continuous_torque_Nm,2)), ...
                'traction_utilization_peak',max(tr.traction_utilization,[],'all'), ...
                'minimum_quasistatic_wheel_normal_N',min(tr.wheel_normal,[],'all'), ...
                'steady_cross_peak_to_peak_m',range(tr.cross(tr.t>=3)), ...
                'all_finite',all(isfinite(tr.z),'all'), ...
                'conditional_planar_feasible',all(isfinite(tr.z),'all') && ...
                    all(tr.wheel_normal>0,'all') && all(tr.traction_utilization<=1,'all') && ...
                    all(abs(tr.torque)<=P.continuous_torque_Nm,'all'));
            if k==1, dynamic=entry; else, dynamic(k)=entry; end
            fprintf('%-8s V=%.2f yaw=%+.1f -> cycle %.6f m/s; wheel %.2f rad/s; torque %.3f Nm; traction %.3f\n', ...
                profiles{ip},V,w,s.cycle_along_m_s,dynamic(k).wheel_speed_peak_rad_s, ...
                dynamic(k).wheel_torque_peak_Nm,dynamic(k).traction_utilization_peak);
            if ip==1 && V==.5 && w==2, demo=tr; end
            if ip==2 && V==.5 && w==2, stress_demo=tr; end
            if ip==3 && V==.5 && w==2, corrected_demo=tr; end
        end
    end
end
% Time-step convergence, actual complete-yaw-turn metrics (not speed norm).
fine = simulate_planar(.5,2,P,P,.002);
fine_m = metrics(fine,P.world_direction_rad,3);
demo_m = metrics(demo,P.world_direction_rad,3);
convergence = struct('coarse_dt_s',.004,'fine_dt_s',.002, ...
    'cycle_along_difference_m_s',abs(fine_m.cycle_along_m_s-demo_m.cycle_along_m_s), ...
    'final_position_difference_m',norm(interp1(fine.t,fine.z(:,1:2),demo.t(end))-demo.z(end,1:2)));
assert(convergence.cycle_along_difference_m_s<1e-4);
assert(convergence.final_position_difference_m<1e-3);
assert(all([dynamic.all_finite]));
result = struct('version','world_directional_spin_planar_matlab_v1', ...
    'matlab_release',version('-release'),'matlab_pid',feature('getpid'), ...
    'created_at',char(datetime('now','Format','yyyy-MM-dd HH:mm:ss')), ...
    'scope','Exact differential-drive kinematics plus CONDITIONAL planar no-slip dynamics; no trained policy or full MOD4 balance/contact model.', ...
    'parameters',P,'ideal',ideal,'negative_controls',controls, ...
    'dynamic',dynamic,'time_step_convergence',convergence, ...
    'tests_passed',true,'all_requested_planar_cases_feasible',all([dynamic.conditional_planar_feasible]));
write_json(fullfile(D,'RESULTS.json'),result);
save(fullfile(D,'TRAJECTORIES.mat'),'demo','fine','stress_demo','corrected_demo','result');
tab = struct2table(rmfield(dynamic,{'all_cycles','steady_cycles','wheel_torque_rms_Nm'}));
writetable(tab,fullfile(D,'CASE_SUMMARY.csv'));
writetable(table(demo.t,demo.along,demo.cross,demo.u,demo.z(:,3),demo.z(:,5), ...
    demo.wheel_speed(:,1),demo.wheel_speed(:,2),demo.torque(:,1),demo.torque(:,2), ...
    'VariableNames',{'t_s','along_m','cross_m','body_v_m_s','heading_rad','yaw_rad_s', ...
    'wheel_L_rad_s','wheel_R_rad_s','torque_L_Nm','torque_R_Nm'}),fullfile(D,'DEMO_TRACE.csv'));
make_figures(D,P,result,demo,stress_demo,corrected_demo);
fprintf('PASS: analytic identities, negative controls, and RK4 convergence.\n');
fprintf('Conditional planar feasibility: %d/%d cases. No PPO/full balance/real-robot claim.\n', ...
    sum([dynamic.conditional_planar_feasible]),numel(dynamic));
fprintf('Files saved in %s\n',D);
end

function tr = kinematic(V,w,alpha,theta0,mode,limit)
N=24000; T=4*2*pi/abs(w); t=linspace(0,T,N+1)'; theta=theta0+w*t;
if strcmp(mode,'body'), u=V+zeros(size(t)); else, u=2*V*cos(theta-alpha); end
u=max(-limit,min(limit,u));
xy=cumtrapz(t,u.*[cos(theta) sin(theta)]);
e=[cos(alpha);sin(alpha)]; f=[-sin(alpha);cos(alpha)];
tr=struct('t',t,'z',[xy theta],'u',u,'along',xy*e,'cross',xy*f);
phi=theta-alpha; phi0=theta0-alpha;
exact=[V*t+V/(2*w)*(sin(2*phi)-sin(2*phi0)), ...
    V/(2*w)*(cos(2*phi0)-cos(2*phi))];
tr.analytic_error=max(abs([tr.along tr.cross]-exact),[],'all');
end

function tr = simulate_planar(V,w,P,C,dt)
T=3+5*2*pi/abs(w); t=(0:dt:T)';
z=zeros(numel(t),7); z(1,3)=P.world_direction_rad+pi/3;
for k=1:numel(t)-1
    a=rhs(t(k),z(k,:)',V,w,P,C);
    b=rhs(t(k)+dt/2,z(k,:)'+dt*a/2,V,w,P,C);
    c=rhs(t(k)+dt/2,z(k,:)'+dt*b/2,V,w,P,C);
    d=rhs(t(k)+dt,z(k,:)'+dt*c,V,w,P,C);
    z(k+1,:)=z(k,:)+dt*(a+2*b+2*c+d)'/6;
end
torque=zeros(numel(t),2); wheels=torque; normal=torque; util=torque; clipped=zeros(numel(t),1);
for k=1:numel(t)
    [dz,audit]=rhs(t(k),z(k,:)',V,w,P,C);
    torque(k,:)=audit.torque; wheels(k,:)=audit.wheels; clipped(k)=audit.clipped;
    % Quasi-static roll support and friction-circle CONSISTENCY check.
    ay=z(k,4)*z(k,5); total_fy=P.mass_kg*ay;
    normal(k,:)=[P.mass_kg*P.g/2-P.mass_kg*ay*P.com_height_m/P.track_m, ...
        P.mass_kg*P.g/2+P.mass_kg*ay*P.com_height_m/P.track_m];
    fx=[P.mass_kg*dz(4)/2-P.yaw_inertia_kg_m2*dz(5)/P.track_m, ...
        P.mass_kg*dz(4)/2+P.yaw_inertia_kg_m2*dz(5)/P.track_m];
    fy=total_fy*normal(k,:)/(P.mass_kg*P.g);
    util(k,:)=hypot(fx,fy)./(P.mu*normal(k,:));
end
e=[cos(P.world_direction_rad);sin(P.world_direction_rad)];
f=[-sin(P.world_direction_rad);cos(P.world_direction_rad)];
tr=struct('t',t,'z',z,'u',z(:,4),'along',z(:,1:2)*e,'cross',z(:,1:2)*f, ...
    'torque',torque,'wheel_speed',wheels,'wheel_normal',normal,'traction_utilization',util,'clipped',clipped);
end

function [dz,audit] = rhs(t,z,V,w,P,C)
[A,Ad]=ramp(t-.75,1.5); [B,Bd]=ramp(t,1.5);
phi=z(3)-P.world_direction_rad;
uref=2*V*A*cos(phi); urefdot=2*V*(Ad*cos(phi)-A*sin(phi)*z(5));
if P.world_feedback_enabled
    e=[cos(P.world_direction_rad);sin(P.world_direction_rad)];
    f=[-sin(P.world_direction_rad);cos(P.world_direction_rad)];
    along=z(1:2)'*e; cross=z(1:2)'*f;
    s=max(0,min(1,(t-.75)/1.5));
    target_along=V*(1.5*(s^3-.5*s^4)+max(0,t-2.25));
    va=V*A+P.world_position_gain_s_inv*(target_along-along);
    vc=-P.world_position_gain_s_inv*cross;
    vad=V*Ad+P.world_position_gain_s_inv*(V*A-z(4)*cos(phi));
    vcd=-P.world_position_gain_s_inv*z(4)*sin(phi);
    uref=2*(va*cos(phi)+vc*sin(phi));
    urefdot=2*(vad*cos(phi)+vcd*sin(phi)+z(5)*(-va*sin(phi)+vc*cos(phi)));
end
au=urefdot+C.speed_gain_s_inv*(uref-z(4));
aw=w*Bd+C.yaw_gain_s_inv*(w*B-z(5));
Me=C.mass_kg+2*C.wheel_equivalent_inertia_kg_m2/C.radius_m^2;
Ie=C.yaw_inertia_kg_m2+C.wheel_equivalent_inertia_kg_m2*C.track_m^2/(2*C.radius_m^2);
common=C.radius_m*Me*au/2; diff=C.radius_m*Ie*aw/C.track_m;
wheels=[(z(4)-P.track_m*z(5)/2)/P.radius_m; (z(4)+P.track_m*z(5)/2)/P.radius_m];
limit=min(P.peak_torque_Nm,max(0,P.envelope_intercept_Nm-P.envelope_slope_Nm_s_rad*abs(wheels)));
request=P.motor_gain*[common-diff;common+diff];
cmd=max(-limit,min(limit,request));
torque=max(-limit,min(limit,z(6:7)));
MeP=P.mass_kg+2*P.wheel_equivalent_inertia_kg_m2/P.radius_m^2;
IeP=P.yaw_inertia_kg_m2+P.wheel_equivalent_inertia_kg_m2*P.track_m^2/(2*P.radius_m^2);
dz=[z(4)*cos(z(3));z(4)*sin(z(3));z(5); ...
    sum(torque)/(P.radius_m*MeP); ...
    P.track_m*(torque(2)-torque(1))/(2*P.radius_m*IeP); ...
    (cmd-z(6:7))/P.actuator_lag_s];
if nargout>1, audit=struct('torque',torque','wheels',wheels','clipped',any(abs(request)>limit+1e-10)); end
end

function [A,Ad] = ramp(t,T)
s=max(0,min(1,t/T)); A=3*s^2-2*s^3;
Ad=(6*s-6*s^2)/T;
end

function m = metrics(tr,alpha,start_time)
% Enumerate EVERY full turn from first sample at/after start_time.
ix=find(tr.t>=start_time,1); t=tr.t(ix:end); xy=tr.z(ix:end,1:2);
theta=tr.z(ix:end,3); signw=sign(theta(end)-theta(1));
phase=signw*(theta-theta(1));
assert(all(diff(phase)>=-1e-9),'Yaw reversal invalidates monotonic turn extraction');
[phase,keep]=unique(phase,'stable'); t=t(keep); xy=xy(keep,:);
nt=floor(phase(end)/(2*pi)+1e-10);
bound=(0:nt)'*2*pi;
bt=interp1(phase,t,bound,'linear'); bx=interp1(phase,xy,bound,'linear');
along=bx*[cos(alpha);sin(alpha)]; cross=bx*[-sin(alpha);cos(alpha)];
dt=diff(bt); va=diff(along)./dt; vc=diff(cross)./dt;
cycles=struct('start_time_s',num2cell(bt(1:end-1)), 'end_time_s',num2cell(bt(2:end)), ...
    'along_net_m',num2cell(diff(along)), 'cross_net_m',num2cell(diff(cross)), ...
    'along_m_s',num2cell(va),'cross_m_s',num2cell(vc));
m=struct('first_sample_time_s',t(1),'full_turn_count',nt,'cycles',cycles, ...
    'cycle_along_m_s',sum(diff(along))/sum(dt),'cycle_cross_m_s',sum(diff(cross))/sum(dt), ...
    'full_window_along_m_s',(xy(end,:)-xy(1,:))*[cos(alpha);sin(alpha)]/(t(end)-t(1)), ...
    'full_window_cross_m_s',(xy(end,:)-xy(1,:))*[-sin(alpha);cos(alpha)]/(t(end)-t(1)));
end

function make_figures(D,P,R,tr,stress,corrected)
f=figure('Name','MOD4: 边走边转可行性 / WORLD net progress','Color','w','Position',[80 90 1240 790]);
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
nexttile; hold on; cols=lines(3); speeds=[.15 .3 .5];
for j=1:3
    a=kinematic(speeds(j),2,0,0,'world',inf);
    plot(a.along,a.cross,'LineWidth',1.8,'Color',cols(j,:));
end
b=kinematic(.5,2,0,0,'body',inf); plot(b.along,b.cross,'--','Color',[.55 .55 .55],'LineWidth',1.8);
xlabel('目标方向净位移 / along (m)'); ylabel('横向位移 / cross (m)'); grid on;
title('转圈同时推进；恒 BODY 速度只绕圈');
legend('V=0.15 m/s','V=0.30 m/s','V=0.50 m/s','恒 BODY 0.50: 整圈净位移=0','Location','northwest');
nexttile; use=tr.t>=3 & tr.t<=3+2*pi/2;
plot(tr.t(use)-3,tr.u(use),'LineWidth',1.6); hold on;
plot(tr.t(use)-3,tr.u(use).*cos(tr.z(use,3)-P.world_direction_rad),'LineWidth',1.6);
plot(tr.t(use)-3,tr.u(use).*sin(tr.z(use,3)-P.world_direction_rad),'LineWidth',1.6);
yline(.5,'k:'); grid on; xlabel('一个自转周期内时间 (s)'); ylabel('速度 (m/s)');
title('V=0.50, yaw=2: 车身交替前进与倒车'); legend('BODY前向','世界along','世界cross','目标周期均值');
nexttile; plot(tr.t,tr.along,'LineWidth',1.6); hold on; plot(tr.t,.5*tr.t,'k--');
plot(tr.t,tr.cross,'LineWidth',1.4); plot(stress.t,stress.cross,'LineWidth',1.3);
plot(corrected.t,corrected.cross,'LineWidth',1.3); grid on; xlabel('时间 (s)'); ylabel('位移 (m)');
title('延迟造成横向偏移；世界位置反馈可纠偏');
legend('名义along','理想Vt（启动有偏移）','名义cross','延迟150ms cross','同延迟+世界纠偏cross','Location','northwest');
nexttile; nom=R.dynamic(1:12); vals=reshape([nom.steady_cycle_along_m_s],4,3)';
bar([.15 .3 .5],vals); hold on; plot([.15 .3 .5],[.15 .3 .5],'k--o');
xlabel('要求世界净速度 (m/s)'); ylabel('实际完整圈净速度 (m/s)'); grid on;
title('名义模型，左右 yaw=1/2 rad/s'); legend('+1','-1','+2','-2','目标','Location','northwest');
sgtitle('MATLAB 简化模型：周期平均可推进；不能全朝向瞬时直线匀速（非完整平衡 / PPO 验收）');
savefig(f,fullfile(D,'DIRECTIONAL_SPIN.fig')); exportgraphics(f,fullfile(D,'DIRECTIONAL_SPIN.png'),'Resolution',145);
g=figure('Name','MOD4 motor and traction assumptions','Color','w','Position',[140 130 1180 700]);
tiledlayout(2,2,'Padding','compact','TileSpacing','compact');
nexttile; plot(tr.t,tr.wheel_speed,'LineWidth',1.1); yline(P.no_load_speed_rad_s,'k--'); yline(-P.no_load_speed_rad_s,'k--');
title('Wheel speed / nominal 0.5 m/s + 2 rad/s'); xlabel('t (s)'); ylabel('rad/s'); grid on; legend('Left','Right','No-load envelope');
nexttile; plot(tr.t,tr.torque,'LineWidth',1.1); yline(P.continuous_torque_Nm,'k--'); yline(-P.continuous_torque_Nm,'k--');
title('Motor torque / estimated continuous rating'); xlabel('t (s)'); ylabel('Nm'); grid on;
nexttile; plot(tr.t,tr.traction_utilization,'LineWidth',1.1); yline(1,'r--');
title('No-slip consistency check, mu=0.75'); xlabel('t (s)'); ylabel('Force / mu*N'); grid on;
nexttile; plot(tr.t,tr.wheel_normal,'LineWidth',1.1); yline(0,'r--');
title('Quasi-static load transfer (balance assumed)'); xlabel('t (s)'); ylabel('N'); grid on;
sgtitle('CONDITIONAL planar model: rigid contact, balance assumed; no springs/legs/thermal limits');
savefig(g,fullfile(D,'MOTOR_TRACTION.fig')); exportgraphics(g,fullfile(D,'MOTOR_TRACTION.png'),'Resolution',145);
figure(f); drawnow;
end

function write_json(path,x)
fid=fopen(path,'w','n','UTF-8'); assert(fid>=0); clean=onCleanup(@()fclose(fid));
fprintf(fid,'%s\n',jsonencode(x,'PrettyPrint',true));
end
