param([string]$IncomingOnnx = "")

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimePython = Join-Path $Root ".runtime\Scripts\python.exe"
$WorkspacePython = [IO.Path]::GetFullPath((Join-Path $Root "..\.venv\Scripts\python.exe"))
if (Test-Path -LiteralPath $RuntimePython) { $Python = $RuntimePython }
elseif (Test-Path -LiteralPath $WorkspacePython) { $Python = $WorkspacePython }
else { $Python = "python.exe" }
$Backend = Join-Path $Root "launcher.py"
$Driver = Join-Path $Root "drive_wasd.py"
$Model = Join-Path $Root "model\rm_training_arena.xml"
$Imported = Join-Path $Root "policies\imported"

$SpawnCodes = [ordered]@{
  "平地 / 狗洞通道（位置 1）" = "f1"
  "二级台阶（位置 2）" = "f2"
  "25 度斜坡（位置 3）" = "f3"
  "247.2 mm 狗洞入口（位置 4）" = "f4"
  "起伏路（位置 5）" = "f5"
  "飞坡（位置 6）" = "f6"
  "中心岛与 50 mm 挡圈（位置 7）" = "f7"
  "416 mm 挡墙（位置 8）" = "f8"
}
$script:PolicyMap = @{}
$script:Simulation = $null

function Invoke-Backend([string[]]$Arguments) {
  $raw = & $Python $Backend @Arguments 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) {
    try { $parsed = $raw | ConvertFrom-Json; throw $parsed.error }
    catch [System.Management.Automation.RuntimeException] { throw $_ }
    catch { throw $raw.Trim() }
  }
  return ($raw | ConvertFrom-Json)
}

$Form = New-Object Windows.Forms.Form
$Form.Text = "MOD4 ONNX -> MuJoCo 一键启动器"
$Form.StartPosition = "CenterScreen"
$Form.Size = New-Object Drawing.Size(900, 650)
$Form.MinimumSize = New-Object Drawing.Size(760, 560)
$Form.Font = New-Object Drawing.Font("Microsoft YaHei UI", 10)

$Title = New-Object Windows.Forms.Label
$Title.Text = "MOD4 ONNX -> MuJoCo"
$Title.Font = New-Object Drawing.Font("Microsoft YaHei UI", 18, [Drawing.FontStyle]::Bold)
$Title.Location = New-Object Drawing.Point(18, 15)
$Title.AutoSize = $true
$Form.Controls.Add($Title)

$Intro = New-Object Windows.Forms.Label
$Intro.Text = "导入训练导出的 ONNX，检查单帧/五帧历史接口与闭链模型，然后一键驾驶查看。"
$Intro.Location = New-Object Drawing.Point(20, 53)
$Intro.AutoSize = $true
$Form.Controls.Add($Intro)

$PolicyLabel = New-Object Windows.Forms.Label
$PolicyLabel.Text = "策略："
$PolicyLabel.Location = New-Object Drawing.Point(20, 88)
$PolicyLabel.AutoSize = $true
$Form.Controls.Add($PolicyLabel)

$PolicyBox = New-Object Windows.Forms.ComboBox
$PolicyBox.DropDownStyle = "DropDownList"
$PolicyBox.Location = New-Object Drawing.Point(75, 84)
$PolicyBox.Size = New-Object Drawing.Size(575, 30)
$PolicyBox.Anchor = "Top,Left,Right"
$Form.Controls.Add($PolicyBox)

$ImportButton = New-Object Windows.Forms.Button
$ImportButton.Text = "导入 ONNX..."
$ImportButton.Location = New-Object Drawing.Point(665, 82)
$ImportButton.Size = New-Object Drawing.Size(105, 32)
$ImportButton.Anchor = "Top,Right"
$Form.Controls.Add($ImportButton)

$RefreshButton = New-Object Windows.Forms.Button
$RefreshButton.Text = "刷新"
$RefreshButton.Location = New-Object Drawing.Point(780, 82)
$RefreshButton.Size = New-Object Drawing.Size(85, 32)
$RefreshButton.Anchor = "Top,Right"
$Form.Controls.Add($RefreshButton)

$SpawnLabel = New-Object Windows.Forms.Label
$SpawnLabel.Text = "初始场地："
$SpawnLabel.Location = New-Object Drawing.Point(20, 135)
$SpawnLabel.AutoSize = $true
$Form.Controls.Add($SpawnLabel)

$SpawnBox = New-Object Windows.Forms.ComboBox
$SpawnBox.DropDownStyle = "DropDownList"
$SpawnBox.Location = New-Object Drawing.Point(105, 131)
$SpawnBox.Size = New-Object Drawing.Size(310, 30)
[void]$SpawnBox.Items.AddRange([string[]]$SpawnCodes.Keys)
$SpawnBox.SelectedIndex = 0
$Form.Controls.Add($SpawnBox)

$AssistBox = New-Object Windows.Forms.CheckBox
$AssistBox.Text = "开启航向辅助（便于 MuJoCo 手动驾驶）"
$AssistBox.Location = New-Object Drawing.Point(445, 133)
$AssistBox.Size = New-Object Drawing.Size(355, 28)
$AssistBox.Checked = $true
$Form.Controls.Add($AssistBox)

$CheckButton = New-Object Windows.Forms.Button
$CheckButton.Text = "检查 ONNX 与模型"
$CheckButton.Location = New-Object Drawing.Point(20, 178)
$CheckButton.Size = New-Object Drawing.Size(160, 38)
$Form.Controls.Add($CheckButton)

$StartButton = New-Object Windows.Forms.Button
$StartButton.Text = "> 一键启动 MuJoCo"
$StartButton.Location = New-Object Drawing.Point(192, 178)
$StartButton.Size = New-Object Drawing.Size(185, 38)
$StartButton.BackColor = [Drawing.Color]::FromArgb(210, 242, 214)
$Form.Controls.Add($StartButton)

$StopButton = New-Object Windows.Forms.Button
$StopButton.Text = "停止仿真"
$StopButton.Location = New-Object Drawing.Point(389, 178)
$StopButton.Size = New-Object Drawing.Size(110, 38)
$StopButton.Enabled = $false
$Form.Controls.Add($StopButton)

$FolderButton = New-Object Windows.Forms.Button
$FolderButton.Text = "打开导入目录"
$FolderButton.Location = New-Object Drawing.Point(735, 178)
$FolderButton.Size = New-Object Drawing.Size(130, 38)
$FolderButton.Anchor = "Top,Right"
$Form.Controls.Add($FolderButton)

$Status = New-Object Windows.Forms.Label
$Status.Text = "尚未检查"
$Status.Font = New-Object Drawing.Font("Microsoft YaHei UI", 10, [Drawing.FontStyle]::Bold)
$Status.Location = New-Object Drawing.Point(20, 232)
$Status.Size = New-Object Drawing.Size(845, 28)
$Status.Anchor = "Top,Left,Right"
$Form.Controls.Add($Status)

$Details = New-Object Windows.Forms.TextBox
$Details.Location = New-Object Drawing.Point(20, 263)
$Details.Size = New-Object Drawing.Size(845, 245)
$Details.Multiline = $true
$Details.ReadOnly = $true
$Details.ScrollBars = "Vertical"
$Details.Font = New-Object Drawing.Font("Consolas", 10)
$Details.Anchor = "Top,Bottom,Left,Right"
$Form.Controls.Add($Details)

$Help = New-Object Windows.Forms.Label
$Help.Text = "操控：W/S 前后，A/D 转向，X 停车，Q/E 高度，F 循环场地，V 循环模式，Y 辅助，C 对比策略。"
$Help.Location = New-Object Drawing.Point(20, 520)
$Help.Size = New-Object Drawing.Size(845, 45)
$Help.Anchor = "Bottom,Left,Right"
$Form.Controls.Add($Help)

function Refresh-Policies([string]$SelectPath = "") {
  $PolicyBox.Items.Clear()
  $script:PolicyMap = @{}
  $files = Get-ChildItem -LiteralPath (Join-Path $Root "policies") -Filter "*.onnx" -File -Recurse | Sort-Object LastWriteTime -Descending
  foreach ($file in $files) {
    $relative = $file.FullName.Substring($Root.Length + 1)
    $script:PolicyMap[$relative] = $file.FullName
    [void]$PolicyBox.Items.Add($relative)
  }
  if ($PolicyBox.Items.Count -eq 0) { return }
  $chosen = -1
  if ($SelectPath) {
    for ($i = 0; $i -lt $PolicyBox.Items.Count; $i++) {
      if ([IO.Path]::GetFullPath($script:PolicyMap[$PolicyBox.Items[$i]]) -eq [IO.Path]::GetFullPath($SelectPath)) { $chosen = $i; break }
    }
  }
  if ($chosen -lt 0) {
    # A policy imported from the trainer is the user's current candidate.  Select the newest
    # imported ONNX by default so opening the launcher cannot silently run an older bundled
    # checkpoint such as mod4_extended_800.onnx.
    $latestImported = Get-ChildItem -LiteralPath $Imported -Filter "*.onnx" -File -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $preferred = if ($latestImported) {
      $latestImported.FullName.Substring($Root.Length + 1)
    } else {
      "policies\mod4_extended_800.onnx"
    }
    $chosen = $PolicyBox.Items.IndexOf($preferred)
  }
  if ($chosen -lt 0) { $chosen = 0 }
  $PolicyBox.SelectedIndex = $chosen
}

function Get-SelectedPolicy {
  if ($PolicyBox.SelectedIndex -lt 0) { throw "请先导入或选择一个 ONNX。" }
  return $script:PolicyMap[[string]$PolicyBox.SelectedItem]
}

function Inspect-Selected {
  try {
    $policy = Get-SelectedPolicy
    $report = Invoke-Backend @("inspect", "--policy", $policy, "--model", $Model)
    $meta = $report.policy.metadata
    $source = if ($meta.source_checkpoint) { $meta.source_checkpoint } elseif ($meta.checkpoint) { $meta.checkpoint } else { "旁置 JSON 未提供" }
    $iteration = if ($null -ne $meta.source_iteration) { $meta.source_iteration } elseif ($meta.checkpoint -match 'model_(\d+)\.pt$') { $Matches[1] } else { "旁置 JSON 未提供" }
    $Details.Text = "PASS：策略接口和 MuJoCo 机构契约均通过`r`n" +
      "ONNX: $($report.policy.path)`r`n" +
      "SHA256: $($report.policy.sha256)`r`n" +
      "接口: $($report.policy.input.name) [batch,$($report.policy.input.shape[-1])] -> $($report.policy.output.name) [batch,6]`r`n" +
      "零观测动作: $($report.policy.zero_action -join ', ')`r`n" +
      "源检查点: $source`r`n训练迭代: $iteration`r`n" +
      "MJCF: nq=$($report.model.nq) nv=$($report.model.nv) nu=$($report.model.nu) bodies=$($report.model.bodies) geoms=$($report.model.geoms) equalities=$($report.model.equalities)`r`n`r`n" +
      "说明：PASS 只证明 ONNX 接口和机构能够运行。训练是否成熟，请在各场地查看直立、闭链误差、峰值力矩和是否通过。"
    $Status.Text = "可以启动；策略能力仍需在场地中实测"
    $Status.ForeColor = [Drawing.Color]::DarkGreen
    return $true
  } catch {
    $Details.Text = "FAIL：$($_.Exception.Message)"
    $Status.Text = "校验失败，未启动"
    $Status.ForeColor = [Drawing.Color]::DarkRed
    [Windows.Forms.MessageBox]::Show($_.Exception.Message, "检查失败", "OK", "Error") | Out-Null
    return $false
  }
}

function Import-Onnx([string]$Source) {
  try {
    $report = Invoke-Backend @("import", "--source", $Source)
    Refresh-Policies $report.destination
    [void](Inspect-Selected)
    $Status.Text = "已导入：$($report.destination)"
  } catch {
    [Windows.Forms.MessageBox]::Show($_.Exception.Message, "导入失败", "OK", "Error") | Out-Null
  }
}

$RefreshButton.Add_Click({ Refresh-Policies; [void](Inspect-Selected) })
$PolicyBox.Add_SelectedIndexChanged({ if ($PolicyBox.SelectedIndex -ge 0) { [void](Inspect-Selected) } })
$CheckButton.Add_Click({ [void](Inspect-Selected) })
$ImportButton.Add_Click({
  $dialog = New-Object Windows.Forms.OpenFileDialog
  $dialog.Title = "选择训练导出的 ONNX"
  $dialog.Filter = "ONNX policy (*.onnx)|*.onnx"
  if ($dialog.ShowDialog() -eq "OK") { Import-Onnx $dialog.FileName }
})
$FolderButton.Add_Click({ New-Item -ItemType Directory -Force -Path $Imported | Out-Null; Start-Process explorer.exe -ArgumentList $Imported })

$StartButton.Add_Click({
  if (-not (Inspect-Selected)) { return }
  if ($script:Simulation -and -not $script:Simulation.HasExited) {
    [Windows.Forms.MessageBox]::Show("MuJoCo 已经在运行。", "提示", "OK", "Information") | Out-Null
    return
  }
  $policy = Get-SelectedPolicy
  $spawn = $SpawnCodes[[string]$SpawnBox.SelectedItem]
  $yaw = if ($AssistBox.Checked) { "80" } else { "0" }
  $psi = New-Object Diagnostics.ProcessStartInfo
  $psi.FileName = $Python
  $psi.WorkingDirectory = $Root
  $psi.UseShellExecute = $true
  $psi.Arguments = '"' + $Driver + '" --policy "' + $policy + '" --model "' + $Model + '" --spawn ' + $spawn + ' --yaw-assist ' + $yaw
  try {
    $script:Simulation = [Diagnostics.Process]::Start($psi)
    $StartButton.Enabled = $false
    $StopButton.Enabled = $true
    $Status.Text = "MuJoCo 运行中：$([IO.Path]::GetFileName($policy))"
    $Status.ForeColor = [Drawing.Color]::DarkBlue
  } catch {
    [Windows.Forms.MessageBox]::Show($_.Exception.Message, "启动失败", "OK", "Error") | Out-Null
  }
})

$StopButton.Add_Click({
  if ($script:Simulation -and -not $script:Simulation.HasExited) { $script:Simulation.Kill() }
  $StartButton.Enabled = $true
  $StopButton.Enabled = $false
  $Status.Text = "仿真已停止"
})

$Timer = New-Object Windows.Forms.Timer
$Timer.Interval = 500
$Timer.Add_Tick({
  if ($script:Simulation -and $script:Simulation.HasExited) {
    $code = $script:Simulation.ExitCode
    $script:Simulation = $null
    $StartButton.Enabled = $true
    $StopButton.Enabled = $false
    $Status.Text = if ($code -eq 0) { "仿真已关闭" } else { "仿真异常退出，代码 $code" }
  }
})
$Timer.Start()

Refresh-Policies
if ($PolicyBox.Items.Count -gt 0) {
  [void](Inspect-Selected)
} else {
  $Status.Text = "请先导入授权的 MOD4 ONNX，并放入对应的 MJCF/mesh 资产"
  $Details.Text = "源码仓库不包含机器人模型和训练策略。将完整交付资产放入 model/ 与 policies/ 后即可检查和启动。"
}
if ($IncomingOnnx -and (Test-Path -LiteralPath $IncomingOnnx)) { Import-Onnx $IncomingOnnx }
[void]$Form.ShowDialog()
