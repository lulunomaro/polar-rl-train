function refine_results()
% Independent deployment audit and clearer plots; no policy/remote changes.
here=fileparts(mfilename('fullpath'));out=fullfile(here,'results');
loaded=load(fullfile(out,'mod4_wbr_simulation.mat'),'summary','traces','P');
summary=loaded.summary;traces=loaded.traces;P=loaded.P;
sch=summary.schedule;
for i=1:numel(sch)
    [~,li]=min(abs([P.poses.leg_length_m]-sch(i).left_length_m));
    [~,ri]=min(abs([P.poses.leg_length_m]-sch(i).right_length_m));
    trim=deg2rad(sch(i).trim_leg_lean_deg);
    q=[P.poses(li).hip_rad+trim,P.poses(li).crank_rad+trim,P.poses(ri).hip_rad+trim,P.poses(ri).crank_rad+trim];
    sch(i).trim_motor_positions_rad=q;
    sch(i).trim_within_motor_limits=all(q>=[-.5,-1.2,-.5,-1.2] & q<=[.5,.9,.5,.9]);
end
valid=sch([sch.trim_within_motor_limits]);
summary.schedule=sch;
summary.schedule_feasibility=struct('total',numel(sch),'valid',numel(valid),'invalid',numel(sch)-numel(valid), ...
    'reason','Horizontal-body balance trim must satisfy individual motor hip +/-0.5 and crank [-1.2,0.9] rad. Mathematical stability alone is insufficient.');
write_json(fullfile(out,'feasible_gain_schedule.json'),valid);
write_json(fullfile(out,'summary.json'),summary);
save(fullfile(out,'mod4_wbr_simulation.mat'),'summary','traces','P','-v7.3');
figDir=fullfile(out,'figures');
set(groot,'defaultFigureVisible','off','defaultAxesFontName','Microsoft YaHei','defaultAxesFontSize',10);
f=figure('Position',[100 100 1200 530],'Color','w');tiledlayout(1,2,'TileSpacing','compact');
pr=summary.nominal_system.pole_real;poleImag=summary.nominal_system.pole_imag;
a=linspace(0,2*pi,2000);
nexttile;plot(cos(a),sin(a),'--','Color',[.75 .5 .3]);hold on;plot(pr,poleImag,'x','MarkerSize',9,'LineWidth',1.8);axis equal;grid on;xlabel('实部');ylabel('虚部');title('单位圆概览');
nexttile;plot(cos(a),sin(a),'--','Color',[.75 .5 .3]);hold on;plot(pr,poleImag,'x','MarkerSize',9,'LineWidth',1.8);grid on;xlim([min(pr)-.006,1.003]);ylim([min(poleImag)-.004,max(poleImag)+.004]);xlabel('实部');ylabel('虚部');title('极点附近放大');
exportgraphics(f,fullfile(figDir,'closed_loop_poles.png'),'Resolution',180);close(f);
f=figure('Position',[100 100 1200 580],'Color','w');tiledlayout(1,2);
tr=summary.robustness_trials;
nexttile;scatter([tr.delay_ms],[tr.speed_rms_error_m_s],36,[tr.spring_left_n],'filled');colorbar;grid on;xlabel('延迟 (ms)');ylabel('速度 RMS 误差 (m/s)');title('颜色为左弹簧参考力 (N)');
nexttile;scatter([tr.mass_scale],[tr.leg_peak_nm],36,[tr.spring_right_n],'filled');colorbar;grid on;xlabel('车体/腿质量倍率');ylabel('腿电机峰值 (N m)');title('颜色为右弹簧参考力 (N)');
exportgraphics(f,fullfile(figDir,'model_robustness.png'),'Resolution',180);close(f);
names=fieldnames(traces.gas_height);
for i=1:numel(names)
    h=traces.gas_height.(names{i});
    table0=array2table([h.t,h.leg_length,h.reference,h.torque,h.gas_force], ...
        'VariableNames',{'time_s','leg_length_m','reference_m','left_hip_nm','left_crank_nm','right_hip_nm','right_crank_nm','left_spring_force_n','right_spring_force_n'});
    writetable(table0,fullfile(out,[names{i} '.csv']));
end
fprintf('FEASIBLE_GAIN_TABLE: %d/%d; excluded %d\n',numel(valid),numel(sch),numel(sch)-numel(valid));
end
function write_json(path,value)
fid=fopen(path,'w','n','UTF-8');c=onCleanup(@()fclose(fid));fprintf(fid,'%s\n',jsonencode(value,'PrettyPrint',true));
end
