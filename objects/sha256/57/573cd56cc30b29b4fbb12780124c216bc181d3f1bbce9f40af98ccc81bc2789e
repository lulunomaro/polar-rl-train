function status=build_mod4_balance_model(outputDirectory,S,reference)
% A runnable Simulink check of the same discrete, unsaturated stand model.
modelName='MOD4_WBR_Balance_20260917';
status=struct('pass',false,'model_path',fullfile(outputDirectory,[modelName '.slx']), ...
    'max_state_difference',NaN,'error','');
if isempty(ver('simulink')),status.error='Simulink not installed';return;end
try
    if bdIsLoaded(modelName),close_system(modelName,0);end
    new_system(modelName);
    c=onCleanup(@()close_if_loaded(modelName));
    add_block('simulink/Sources/Constant',[modelName '/ZeroInput'],'Value','0','Position',[45 70 80 100]);
    add_block('simulink/Discrete/Discrete State-Space',[modelName '/LQR_ClosedLoop'], ...
        'A',mat2str(S.Ad-S.Bd*S.K,17),'B',mat2str(zeros(10,1)), ...
        'C',mat2str(eye(10)),'D',mat2str(zeros(10,1)), ...
        'InitialCondition',mat2str(reference.X(1,:)',17), ...
        'SampleTime',num2str(S.Ts,17),'Position',[145 50 345 125]);
    add_block('simulink/Sinks/To Workspace',[modelName '/StateOutput'], ...
        'VariableName','state_simulink','SaveFormat','Array','MaxDataPoints','inf','Position',[420 60 550 110]);
    add_line(modelName,'ZeroInput/1','LQR_ClosedLoop/1');
    add_line(modelName,'LQR_ClosedLoop/1','StateOutput/1');
    set_param(modelName,'SolverType','Fixed-step','Solver','FixedStepDiscrete', ...
        'FixedStep',num2str(S.Ts,17),'StopTime',num2str(reference.t(end),17),'ReturnWorkspaceOutputs','on');
    Simulink.Annotation(modelName,'MOD4 CAD parameters; 10-state fixed-length rolling approximation. Stand only; no contact/flight certification.');
    save_system(modelName,status.model_path);
    result=sim(modelName);
    state=result.get('state_simulink');
    assert(isequal(size(state),size(reference.X)),'Simulink sample dimensions differ.');
    status.max_state_difference=max(abs(state-reference.X),[],'all');
    assert(status.max_state_difference<1e-8,'MATLAB / Simulink stand response differs.');
    status.pass=true;
catch ex
    status.error=getReport(ex,'extended','hyperlinks','off');
end
end
function close_if_loaded(name)
if bdIsLoaded(name),close_system(name,0);end
end
