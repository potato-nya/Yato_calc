# 夜刀计算器（桌面版）

基于 Tkinter 的本地桌面计算器应用，可在 Windows 上一键打包为独立可执行程序。

## 运行源码

```powershell
# 在项目根目录下
python .\yato_calc_app.py
```

## 打包为 EXE（Windows）

本仓库提供 `build.ps1` 脚本，使用 PyInstaller 进行打包。

```powershell
# 方式一：默认单文件、无控制台窗口
./build.ps1

# 方式二：显示控制台窗口
./build.ps1 -Windowed:$false

# 方式三：打包为目录
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

## 常见问题

- 首次打包会自动安装/升级 `pip`、`setuptools`、`wheel`、`pyinstaller`。
- 若提示未找到 Python，请安装并将 Python 加入 PATH（建议 3.11/3.12）。
- Tkinter 属于标准库，PyInstaller 会自动收集所需的 Tcl/Tk 运行时。

## 目录结构

- `yato_calc_app.py` — Tkinter 应用入口
- `index.html` — 网页版静态页面（与桌面版互不依赖）
- `build.ps1` — Windows 打包脚本
- `.gitignore` — 忽略构建产物
