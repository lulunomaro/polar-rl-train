function animate_directional_spin
% Render the saved MATLAB planar trajectory through the MATLAB graphics API.
% This is an illustrative footprint, NOT a full MOD4 CAD or balance animation.
D=fileparts(mfilename('fullpath')); S=load(fullfile(D,'TRAJECTORIES.mat'),'demo');
tr=S.demo; frames=linspace(0,tr.t(end),80); z=interp1(tr.t,tr.z,frames);
f=figure('Visible','off','Color','w','Position',[60 60 1120 710], ...
    'Name','WORLD directed spin vs constant BODY velocity');
clean=onCleanup(@()close(f));
tiledlayout(2,1,'Padding','compact','TileSpacing','compact');
ax1=nexttile; hold(ax1,'on'); plot(ax1,tr.along,tr.cross,'Color',[.8 .87 .9],'LineWidth',1.6);
plot(ax1,[0 max(tr.along)+.3],[0 0],'k:');
line1=plot(ax1,0,0,'Color',[.02 .47 .62],'LineWidth',2.4);
body1=patch(ax1,nan,nan,[.1 .62 .75],'EdgeColor',[.02 .2 .25],'LineWidth',1.4);
heading1=plot(ax1,nan,nan,'r-','LineWidth',3);
axis(ax1,[-.8 1.8 -.65 .65]); daspect(ax1,[1 1 1]); grid(ax1,'on');
xlabel(ax1,'指定世界方向净位移 (m)'); ylabel(ax1,'横向位移 (m)');
title1=title(ax1,'交替前进 / 倒车：每整圈沿目标方向推进');
ax2=nexttile; hold(ax2,'on'); tt=linspace(0,4*pi,400); plot(ax2,.25*sin(tt),.25*(1-cos(tt)),'--','Color',[.65 .65 .65]);
line2=plot(ax2,0,0,'Color',[.7 .25 .2],'LineWidth',2.2);
body2=patch(ax2,nan,nan,[.8 .45 .25],'EdgeColor',[.3 .1 .05],'LineWidth',1.4);
heading2=plot(ax2,nan,nan,'r-','LineWidth',3);
axis(ax2,[-.65 .65 -.25 .85]); daspect(ax2,[1 1 1]); grid(ax2,'on');
xlabel(ax2,'世界X (m)'); ylabel(ax2,'世界Y (m)');
title(ax2,'负对照：恒 BODY 前进0.5m/s + yaw 2rad/s，只绕圈，整圈净进度为0');
sgtitle('MATLAB简化仿真 / V=0.5m/s，yaw=2rad/s；姿态平衡和无滑接触为假设');
base=[-.13 -.13 .13 .13;-.2188 .2188 .2188 -.2188];
gifpath=fullfile(D,'DIRECTIONAL_SPIN_ANIMATION.gif');
for k=1:numel(frames)
    it=find(tr.t<=frames(k),1,'last');
    set(line1,'XData',tr.along(1:it),'YData',tr.cross(1:it));
    th=z(k,3); c=[cos(th) -sin(th);sin(th) cos(th)]*base+z(k,1:2)';
    set(body1,'XData',c(1,:),'YData',c(2,:));
    xlim(ax1,[z(k,1)-.8 z(k,1)+1.8]);
    if z(k,4)<0, body1.FaceColor=[.55 .25 .75]; else, body1.FaceColor=[.1 .62 .75]; end
    set(heading1,'XData',[z(k,1) z(k,1)+.32*cos(th)],'YData',[z(k,2) z(k,2)+.32*sin(th)]);
    title1.String=sprintf('等比例跟随视图：t=%.1fs，前进净位移=%.2fm，BODY速度=%+.2fm/s',frames(k),tr.along(it),z(k,4));
    th2=2*frames(k); p2=[.25*sin(th2);.25*(1-cos(th2))];
    t2=linspace(0,th2,400);
    set(line2,'XData',.25*sin(t2),'YData',.25*(1-cos(t2)));
    c2=[cos(th2) -sin(th2);sin(th2) cos(th2)]*base+p2;
    set(body2,'XData',c2(1,:),'YData',c2(2,:));
    set(heading2,'XData',[p2(1) p2(1)+.32*cos(th2)],'YData',[p2(2) p2(2)+.32*sin(th2)]);
    rgb=print(f,'-RGBImage','-r95'); [indexed,map]=rgb2ind(rgb,256);
    if k==1, imwrite(indexed,map,gifpath,'gif','LoopCount',inf,'DelayTime',.09);
    else, imwrite(indexed,map,gifpath,'gif','WriteMode','append','DelayTime',.09); end
end
fprintf('MATLAB animation saved: %s\n',gifpath);
end
