# 夜刀戈渎计算器（桌面版）

基于 Tkinter 的本地桌面计算器应用，可在 Windows 上一键打包为独立可执行程序。

## 运行源码

```powershell
# 在项目根目录下
python .\yato_calc_app.py
```

## 打包为 EXE（Windows）

本仓库提供 `build.ps1` 脚本，使用 PyInstaller 进行打包。

```powershell
# 方式一：默认单文件、无控制台窗口（推荐）
./build.ps1

# 方式二：显示控制台窗口（便于调试）
./build.ps1 -Windowed:$false

# 方式三：打包为目录（加载更快）
./build.ps1 -OneFile:$false

# 自定义应用名
./build.ps1 -Name "Yato_calc"
```

打包完成后，生成的可执行文件位于 `dist/` 目录，例如：

- `dist/Yato_calc.exe`

### 自定义图标

- 将图标文件放在 `assets/icon.ico`（推荐 256x256，含多尺寸）。
- 本地打包：脚本会自动使用该图标，并把它一并打进程序资源，Tkinter 窗口也会显示该图标。
- 也可显式指定：

```powershell
./build.ps1 -Icon .\assets\icon.ico
```

若你只有 PNG，可先转换为 ICO（示例使用 Python Pillow）：

```powershell
python - << 'PY'
from PIL import Image
img = Image.open('icon.png').convert('RGBA')
img.save('assets/icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
PY
```

## CI 自动打包（可选）

本仓库已配置 GitHub Actions（`.github/workflows/build.yml`）。当你推送到 `main` 或手动触发工作流时，会在云端 Windows 机器上构建 EXE，并作为构建产物（artifact）上传。

如何获取 EXE：

- 打开仓库的 GitHub 页面 → Actions → 选择最新一次运行 → 页面底部 Artifacts → 下载 `Yato_calc-windows-x64`（ZIP 包内包含 `dist/Yato_calc.exe`）。

说明：工作流使用 Python 3.11 + 最新 PyInstaller 构建，与本地构建互不影响。

### 打 tag 自动发布 Release（已启用）

当你推送满足 `v*` 规则的标签时（例如 `v1.0.0`），工作流会：

- 在云端构建 EXE
- 自动创建 GitHub Release，并把 `dist/Yato_calc.exe` 作为发布资产上传

本地操作示例：

```powershell
git tag v1.0.0
git push origin v1.0.0
```

## 常见问题

- 首次打包会自动安装/升级 `pip`、`setuptools`、`wheel`、`pyinstaller`。
- 若提示未找到 Python，请安装并将 Python 加入 PATH（建议 3.11/3.12）。
- Tkinter 属于标准库，PyInstaller 会自动收集所需的 Tcl/Tk 运行时。

## 目录结构

- `yato_calc_app.py` — Tkinter 应用入口
- `index.html` — 网页版静态页面（与桌面版互不依赖）
- `build.ps1` — Windows 打包脚本
- `.gitignore` — 忽略构建产物
