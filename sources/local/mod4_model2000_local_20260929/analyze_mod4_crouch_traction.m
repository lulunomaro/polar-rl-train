% Reduced-order MATLAB analysis of MOD4 traction vs body-pitch control.
% Source plant measurements: fixed_pose_wheel_probe.csv (MuJoCo); policy trace:
% probe_flat_profile_15s.csv. This does not replace full Isaac replay.
here = fileparts(mfilename('fullpath'));
out = fullfile(here, 'matlab_traction_results');
if ~isfolder(out), mkdir(out); end
F = readtable(fullfile(here, 'fixed_pose_wheel_probe.csv'));
P = readtable(fullfile(here, 'probe_flat_profile_15s.csv'));
G = jsondecode(fileread(fullfile(here, '..', 'matlab_mod4_wbr_20260917', 'mod4_extracted_parameters.json')));
C = jsondecode(fileread(fullfile(here, 'contract_rm2025_later.json')));
drive = F(strcmp(string(F.phase), 'drive'), :);
mass = mean(drive.mass_kg);
radius = C.wheel_radius;
mu = 0.9; % exact MuJoCo tire/floor tangential friction in this local model
wheelN = drive.left_wheel_normal_n + drive.right_wheel_normal_n;
forceLimit = mu .* wheelN;
tractionTorqueLimit = radius .* forceLimit;
motorTorqueLimit = 2 * C.wheel_effort;
accelerationLimit = min(forceLimit, motorTorqueLimit / radius) / mass;
wheelPeripheral = drive.wheel_peripheral_m_s;
velocityError = drive.vx_m_s - wheelPeripheral;

% Flat high pose inertia and COM from earlier CAD-based MATLAB extraction.
% For the virtual axle-centred 2D inverted-pendulum model, x0 is signed
% horizontal COM offset behind the axle and l is COM height above the axle.
highPose = G.poses(end);
x0 = highPose.total_com_xz_m(1);
l = highPose.total_com_xz_m(2);
Icom = highPose.body_pitch_inertia_kg_m2;
Iaxle = Icom + mass * l^2;
g = 9.81;
leanEq = atan2(-x0, l);
A = [0 0 0; 0 0 1; 0 mass*g*l/Iaxle 0];
B = [1/(mass*radius); 0; -(1+l/radius)/Iaxle];
Q = diag([30, 400, 3]);
R = 0.3;
K = lqr(A, B, Q, R);

% Nonlinear planar simulation. One input is total torque of both wheels.
% Vertical equilibrium and no-slip rolling are assumed; u is clipped by
% both motor torque and contact friction. This is a feasibility calculation,
% not an executable robot controller or a certificate of full-body stability.
dt = 0.001;
t = (0:dt:8)';
state = zeros(numel(t), 3); % [vx, body pitch, pitch rate]
torque = zeros(numel(t), 1);
command = zeros(numel(t), 1);
pitchBiasTorque = zeros(numel(t), 1);
uMax = min(motorTorqueLimit, mu*mean(wheelN)*radius);
for k = 1:numel(t)-1
    if t(k) >= .5
        command(k) = .5*(1-exp(-(t(k)-.5)/.4));
        commandAccel = .5/.4*exp(-(t(k)-.5)/.4);
    else
        commandAccel = 0;
    end
    v = state(k,1); theta = state(k,2); thetaDot = state(k,3);
    u = -K * [v-command(k); theta-leanEq; thetaDot] + mass*radius*commandAccel;
    u = max(-uMax, min(uMax, u));
    torque(k) = u;
    pitchBiasTorque(k) = mass*g*(x0*cos(theta) + l*sin(theta));
    vDot = u/(mass*radius);
    thetaDDot = (pitchBiasTorque(k) - u*(1+l/radius))/Iaxle;
    state(k+1,:) = [v+dt*vDot, theta+dt*thetaDot, thetaDot+dt*thetaDDot];
end
command(end) = command(end-1);
torque(end) = torque(end-1);
pitchBiasTorque(end) = pitchBiasTorque(end-1);
T = table(t, command, state(:,1), rad2deg(state(:,2)), torque, pitchBiasTorque, ...
    'VariableNames', {'time_s','command_m_s','predicted_speed_m_s','predicted_pitch_deg','total_wheel_torque_nm','gravity_pitch_moment_nm'});
writetable(T, fullfile(out, 'lqr_reduced_trace.csv'));

% Extract actual policy's command-to-action relation; if the policy emits
% negative wheel speed, poor progress is not proof of tire slip.
commands = [0 .3 .6 1.0]';
meanActual = zeros(4,1); meanWheelPeripheral = zeros(4,1);
meanAction = zeros(4,1); meanHeight = zeros(4,1);
for k = 1:4
    take = abs(P.command_vx_m_s - commands(k)) < 1e-8 & P.time_s > 2;
    meanActual(k) = mean(P.actual_vx_m_s(take));
    meanWheelPeripheral(k) = mean(P.wheel_peripheral_m_s(take));
    meanAction(k) = mean(P.wheel_action_mean(take));
    meanHeight(k) = mean(P.base_z_m(take));
end
S = table(commands, meanActual, meanWheelPeripheral, meanAction, meanHeight, ...
    'VariableNames', {'command_m_s','actual_m_s','wheel_peripheral_m_s','wheel_action','root_height_m'});
writetable(S, fullfile(out, 'policy_stage_means.csv'));

fig = figure('Visible','off','Position',[60 60 1300 850]);
tiledlayout(2,2,'Padding','compact');
nexttile;
plot(drive.root_z_m, wheelN/(mass*g), 'ko-', 'LineWidth',1.7); hold on;
yline(1,'--','all weight'); ylim([0 1.12]);
xlabel('Measured root height (m)'); ylabel('Two-wheel share of weight');
title('Fixed legs, fixed wheel speed, external pitch moment'); grid on;
nexttile;
plot(drive.root_z_m, drive.vx_m_s, 'bo-', drive.root_z_m, wheelPeripheral, 'r--', 'LineWidth',1.7);
ylim([0 .55]);
xlabel('Measured root height (m)'); ylabel('Speed (m/s)'); legend('Body','Wheel periphery');
title('High pose rolls without observable slip'); grid on;
nexttile;
plot(commands, meanActual, 'ko-', commands, meanWheelPeripheral, 'r--o', commands, commands, 'b:', 'LineWidth',1.7);
xlabel('Policy speed command (m/s)'); ylabel('Mean speed (m/s)');
legend('Body','Wheel periphery','Perfect tracking','Location','northwest');
title('model 2000: body follows wheel output, not command'); grid on;
nexttile;
yyaxis left; plot(t, command, 'k--', t, state(:,1), 'b', 'LineWidth',1.4); ylabel('Speed (m/s)');
yyaxis right; plot(t, rad2deg(state(:,2)), 'r', 'LineWidth',1.4); ylabel('Pitch (deg)');
xlabel('Time (s)'); title('Reduced LQR feasibility with measured limits'); grid on;
exportgraphics(fig, fullfile(out, 'traction_and_balance.png'), 'Resolution',160);
close(fig);

result = struct();
result.model_scope = 'Planar inverted pendulum with fixed leg length, rolling contact, externally measured N; no full closed chain or pitch/height RL policy';
result.local_plant_scope = 'MuJoCo fixed-leg/fixed-wheel probe with an external pure pitch stabilizer, not real actuator and not native Isaac replay';
result.mass_kg = mass; result.wheel_radius_m = radius; result.mu = mu;
result.measured_root_height_min_max_m = [min(drive.root_z_m), max(drive.root_z_m)];
result.measured_two_wheel_normal_min_max_n = [min(wheelN), max(wheelN)];
result.measured_drive_speed_min_max_m_s = [min(drive.vx_m_s), max(drive.vx_m_s)];
result.measured_slip_max = max(drive.slip_ratio);
result.measured_spring_force_per_side_min_max_n = [min(drive.gas_force_mean_n), max(drive.gas_force_mean_n)];
result.measured_leg_target_error_max_rad = max(drive.leg_target_error_rms_rad);
result.external_pitch_stabilizer_abs_max_nm = max(abs(drive.external_pitch_stabilizer_nm));
result.traction_force_limit_min_n = min(forceLimit);
result.traction_torque_limit_min_nm = min(tractionTorqueLimit);
result.motor_torque_limit_total_nm = motorTorqueLimit;
result.conservative_acceleration_limit_min_m_s2 = min(accelerationLimit);
result.com_x_m = x0; result.com_height_above_axle_m = l;
result.unforced_equilibrium_pitch_deg = rad2deg(leanEq);
result.gravity_pitch_moment_at_zero_deg_nm = mass*g*x0;
result.pitch_inertia_about_axle_kg_m2 = Iaxle;
result.lqr_K = K;
result.sim_peak_total_wheel_torque_nm = max(abs(torque));
result.sim_max_abs_pitch_deg = max(abs(rad2deg(state(:,2))));
result.sim_final_speed_m_s = state(end,1);
result.policy_stage_means = table2struct(S);
fid = fopen(fullfile(out, 'summary.json'),'w');
fwrite(fid, jsonencode(result, 'PrettyPrint', true)); fclose(fid);
save(fullfile(out, 'analysis.mat'), 'result', 'T', 'S', 'F', 'P', 'A', 'B', 'K', 'Q', 'R');
disp(result);
