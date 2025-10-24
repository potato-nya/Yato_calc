# Build script to package yato_calc_app.py into a Windows executable using PyInstaller
# Usage (PowerShell):
#   ./build.ps1

param(
    [switch]$OneFile = $true,      # 打包为单文件
    [switch]$Windowed = $true,      # 隐藏控制台窗口（适合 Tkinter）
    [string]$Name = "Yato_calc",   # 生成的应用名称
    [string]$Icon = ''              # 可选：应用图标（.ico），若留空将尝试使用 assets\icon.ico
)

Write-Host '[1/4] Checking Python...'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $python = "py -3"
    } else {
    Write-Error 'Python not found. Please install Python and add it to PATH.'; exit 1
    }
} else {
    $python = "python"
}

& $python --version
if ($LASTEXITCODE -ne 0) { Write-Error 'Python failed to run'; exit 1 }

function Invoke-PipInstall {
    param(
        [string[]]$Packages
    )
    $commonArgs = @('-m','pip','install','--upgrade','--no-input','--disable-pip-version-check')
    Write-Host ('pip install {0}' -f ($Packages -join ' '))
    & $python @commonArgs @Packages | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'pip install failed; retrying with Tsinghua mirror...'
        & $python @commonArgs @Packages '-i' 'https://pypi.tuna.tsinghua.edu.cn/simple' | Out-Host
    }
    if ($LASTEXITCODE -ne 0) { throw 'pip install failed' }
}

Write-Host '[2/4] Installing/upgrading build deps (setuptools, wheel, pyinstaller)...'
try {
    Invoke-PipInstall -Packages @('setuptools','wheel')
} catch {
    Write-Error $_; exit 1
}

# Detect Python version (major.minor)
$pyVer = & $python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
if (-not $pyVer) { Write-Error 'Failed to detect Python version'; exit 1 }
Write-Host ("Detected Python {0}" -f $pyVer)

# Choose compatible PyInstaller version for older Python (e.g., 3.8 => PyInstaller 5.x)
$pyInstallerSpec = 'pyinstaller'
if ($pyVer -match '^3\.(6|7|8)$') { $pyInstallerSpec = 'pyinstaller==5.13.2' }

try {
    Invoke-PipInstall -Packages @($pyInstallerSpec)
} catch {
    Write-Host 'Primary PyInstaller install failed; trying fallback version 5.13.2...'
    try {
        Invoke-PipInstall -Packages @('pyinstaller==5.13.2')
    } catch {
        Write-Error 'Failed to install PyInstaller'; exit 1
    }
}

Write-Host '[3/4] Running PyInstaller...'
$argsList = @('--noconfirm', '--clean', '--name', $Name)
if ($OneFile) { $argsList += '--onefile' } else { $argsList += '--onedir' }
if ($Windowed) { $argsList += '--windowed' }

# 入口脚本
$argsList += 'yato_calc_app.py'

# Helpers to ensure Pillow and convert PNG->ICO
function Test-PillowInstalled {
    & $python -c "import PIL; print('ok')" > $null 2>&1
    return ($LASTEXITCODE -eq 0)
}
function Ensure-Pillow {
    if (-not (Test-PillowInstalled)) {
        Write-Host 'Installing pillow for PNG->ICO conversion...'
        & $python -m pip install --upgrade --no-input --disable-pip-version-check pillow | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'Failed to install pillow' }
    }
}
function Convert-PngToIco([string]$pngPath, [string]$icoPath) {
    Ensure-Pillow
    Write-Host ("Converting PNG to ICO: {0} -> {1}" -f $pngPath, $icoPath)
    & $python -c "from PIL import Image, ImageOps;import sys;img=Image.open(sys.argv[1]).convert('RGBA');img.save(sys.argv[2], sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])" "$pngPath" "$icoPath"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $icoPath)) { throw 'PNG->ICO conversion failed' }
}

# 处理图标：
# 优先使用 -Icon 参数；支持 .ico 或 .png（.png 会自动转换到 assets\\icon.ico）
# 否则尝试 assets\\icon.ico；若不存在而存在 icon.png 或 assets\\icon.png，则自动转换
$iconToUse = ''
if (-not [string]::IsNullOrWhiteSpace($Icon)) {
    if (Test-Path $Icon) {
        if ($Icon.ToLower().EndsWith('.png')) {
            $targetIco = (Join-Path $PSScriptRoot 'assets\icon.ico')
            if (-not (Test-Path (Split-Path $targetIco))) { New-Item -ItemType Directory -Force -Path (Split-Path $targetIco) | Out-Null }
            Convert-PngToIco -pngPath (Resolve-Path $Icon) -icoPath $targetIco
            $iconToUse = $targetIco
        } else {
            $iconToUse = (Resolve-Path $Icon)
        }
    } else {
        Write-Warning ("Icon path not found: {0}" -f $Icon)
    }
} else {
    $defaultIco = (Join-Path $PSScriptRoot 'assets\icon.ico')
    $defaultPng = (Join-Path $PSScriptRoot 'assets\icon.png')
    $rootPng = (Join-Path $PSScriptRoot 'icon.png')
    if (Test-Path $defaultIco) {
        $iconToUse = $defaultIco
    } elseif (Test-Path $defaultPng) {
        if (-not (Test-Path (Split-Path $defaultIco))) { New-Item -ItemType Directory -Force -Path (Split-Path $defaultIco) | Out-Null }
        Convert-PngToIco -pngPath $defaultPng -icoPath $defaultIco
        $iconToUse = $defaultIco
    } elseif (Test-Path $rootPng) {
        if (-not (Test-Path (Split-Path $defaultIco))) { New-Item -ItemType Directory -Force -Path (Split-Path $defaultIco) | Out-Null }
        Convert-PngToIco -pngPath $rootPng -icoPath $defaultIco
        $iconToUse = $defaultIco
    }
}

if ($iconToUse -and (Test-Path $iconToUse)) {
    $argsList += @('--icon', $iconToUse)
    # 将图标文件打包进资源，供 Tkinter 运行时加载
    $argsList += @('--add-data', ("{0};assets" -f $iconToUse))
}

# 执行打包
& $python -m PyInstaller @argsList | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Error 'PyInstaller build failed'; exit 1 }

Write-Host '[4/4] Done'
Write-Host ("Output dir: {0}" -f (Join-Path $PSScriptRoot 'dist'))
Write-Host ("Executable: {0}" -f (Join-Path (Join-Path $PSScriptRoot 'dist') ("$Name.exe")))
