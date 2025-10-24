import ctypes
# Windows DPI感知，避免Tkinter字体模糊
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows older
    except Exception:
        pass

import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import os
import sys

# 创建主窗口
root = tk.Tk()
root.title("夜刀戈渎计算器")
root.geometry("1000x1200")

# 设置窗口图标（如果存在 assets/icon.ico）并兼容 PyInstaller 运行环境
def _resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

try:
    ico_path = _resource_path(os.path.join('assets', 'icon.ico'))
    if os.path.exists(ico_path):
        root.iconbitmap(ico_path)
except Exception:
    pass

# 设置全局字体为黑体（SimHei）优先，其次宋体，并调小字体大小
available_fonts = tkFont.families()
if "黑体" in available_fonts:
    font_family = ("黑体", 8)
elif "SimHei" in available_fonts:
    font_family = ("SimHei", 8)
elif "宋体" in available_fonts:
    font_family = ("宋体", 8)
elif "SimSun" in available_fonts:
    font_family = ("SimSun", 8)
else:
    font_family = ("Arial", 8)  # 备用字体

# 创建标签和输入框
fields = [
    ("局外加攻%", "out_attack"),
    ("局内加攻%（乘算）", "in_attack_mul"),
    ("局内加攻（加算）", "in_attack_add"),
    ("物理易伤%", "phy_vuln"),
    ("法术易伤%", "mag_vuln"),
    ("脆弱%", "fragile"),
    ("敌方护甲", "enemy_armor"),
    ("敌方法抗", "enemy_resist"),
    ("敌方减伤%", "enemy_reduce"),
]

# 设置主窗口背景色
root.configure(bg="#f5f5f5")

# 输入区美化
input_labelframe = tk.LabelFrame(root, text="参数输入：带有%的为百分比", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
input_labelframe.pack(pady=10, fill=tk.X, padx=20)

input_frame = tk.Frame(input_labelframe, bg="#f5f5f5")
input_frame.pack()

entries = {}
for idx, (label_text, var_name) in enumerate(fields):
    row = idx // 3
    col = idx % 3
    label = tk.Label(input_frame, text=label_text, anchor='e', font=font_family, bg="#f5f5f5")
    label.grid(row=row, column=col*2, padx=(10, 2), pady=8, sticky='e')
    entry = tk.Entry(input_frame, width=12, justify='left', font=font_family)
    entry.insert(0, "0")
    entry.grid(row=row, column=col*2+1, padx=(2, 18), pady=8, sticky='w')
    entries[var_name] = entry

# 技能与选项区美化
skill_frame = tk.Frame(root, bg="#f5f5f5")
skill_frame.pack(pady=10)
skill_label = tk.Label(skill_frame, text="选择技能:", font=font_family, bg="#f5f5f5")
skill_label.pack(side=tk.LEFT, padx=(0, 5))
skill_var = tk.StringVar(value="一技能")
skill_dropdown = tk.OptionMenu(skill_frame, skill_var, "一技能", "二技能", "三技能")
skill_dropdown.config(font=font_family)
skill_dropdown.pack(side=tk.LEFT, padx=(0, 15))

j1_var = tk.BooleanVar()
j1_check = tk.Checkbutton(skill_frame, text="精一", variable=j1_var, font=("黑体", 9), width=8, height=1, bg="#f5f5f5", activebackground="#f5f5f5")
j1_check.pack(side=tk.LEFT, padx=8)

gd_var = tk.BooleanVar()
gd_check = tk.Checkbutton(skill_frame, text="戈渎", variable=gd_var, font=("黑体", 9), width=8, height=1, bg="#f5f5f5", activebackground="#f5f5f5")
gd_check.pack(side=tk.LEFT, padx=8)

# 输出区美化
attack_labelframe = tk.LabelFrame(root, text="单次伤害结果", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
attack_labelframe.pack(pady=10, fill=tk.X, padx=20)

attack_frame = tk.Frame(attack_labelframe, bg="#f5f5f5")
attack_frame.pack()
attack_label = tk.Label(attack_frame, text="攻击力: 0", font=("黑体", 11, "bold"), anchor='w', bg="#f5f5f5")
attack_label.pack(anchor='w')

skill_attack_label = tk.Label(attack_frame, text="技能攻击力: 0.00", font=("黑体", 10), anchor='w', bg="#f5f5f5")
skill_attack_label.pack(anchor='w')

physical_damage_label = tk.Label(attack_frame, text="物理伤害: 0.00", font=("黑体", 10), anchor='w', bg="#f5f5f5")
physical_damage_label.pack(anchor='w')

magic_damage_label = tk.Label(attack_frame, text="法术伤害: 0.00", font=("黑体", 10), anchor='w', bg="#f5f5f5")
magic_damage_label.pack(anchor='w')

single_hit_label = tk.Label(attack_frame, text="单次总伤: 0.00", font=("黑体", 11, "bold"), anchor='w', bg="#f5f5f5")
single_hit_label.pack(anchor='w', pady=(0, 2))

# 累计伤害表美化
cumulative_labelframe = tk.LabelFrame(root, text="累计伤害表", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
cumulative_labelframe.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

cumulative_title = tk.Label(cumulative_labelframe, text="累计伤害表格 (法伤+物伤):", font=("黑体", 10, "bold"), bg="#f5f5f5")
cumulative_title.pack(anchor='w')

# 表格加滚动条
cumulative_scroll = tk.Scrollbar(cumulative_labelframe)
cumulative_scroll.pack(side=tk.RIGHT, fill=tk.Y)
cumulative_damage_text = tk.Text(
    cumulative_labelframe,
    font=("Consolas", 9),
    bg="#f5f5f5",
    height=18,
    wrap=tk.NONE,
    yscrollcommand=cumulative_scroll.set,
    state=tk.DISABLED
)
cumulative_damage_text.pack(fill=tk.BOTH, expand=True)
cumulative_scroll.config(command=cumulative_damage_text.yview)

# 修改计算攻击力的函数，增加最终伤害计算
def calculate_attack(*args):
    try:
        out_attack = float(entries['out_attack'].get())
        in_attack_mul = float(entries['in_attack_mul'].get())
        in_attack_add = float(entries['in_attack_add'].get())
        phy_vuln = float(entries['phy_vuln'].get())
        mag_vuln = float(entries['mag_vuln'].get())
        fragile = float(entries['fragile'].get())
        enemy_armor = float(entries['enemy_armor'].get())
        enemy_resist = float(entries['enemy_resist'].get())
        enemy_reduce = float(entries['enemy_reduce'].get())
        is_j1 = j1_var.get()
        skill_selected = skill_var.get()
        
        # 计算攻击力
        base_attack = 552 if is_j1 else 725
        attack = round(base_attack * (1 + out_attack/100))
        attack_label.config(text=f"攻击力: {attack}")
        
        # 计算实际局内加攻
        actual_in_attack = in_attack_mul if is_j1 else (in_attack_mul + 23)
        
        # 计算技能攻击力
        base_skill_attack = attack * (1 + actual_in_attack/100) + in_attack_add
        
        if skill_selected == "一技能":
            skill_attack = base_skill_attack
        elif skill_selected == "二技能":
            if is_j1:
                skill_attack = base_skill_attack * 1.3  # 精一时二技能系数为1.3
            else:
                skill_attack = base_skill_attack * 1.5
        elif skill_selected == "三技能":
            if is_j1:
                # 精一时三技能显示输入错误
                skill_attack_label.config(text="技能攻击力: 输入错误")
                physical_damage_label.config(text="物理伤害: 输入错误")
                magic_damage_label.config(text="法术伤害: 输入错误")
                single_hit_label.config(text="单次总伤: 输入错误")
                cumulative_damage_text.config(state=tk.NORMAL)
                cumulative_damage_text.delete(1.0, tk.END)
                cumulative_damage_text.insert(tk.END, "累计伤害计算错误")
                cumulative_damage_text.config(state=tk.DISABLED)
                return
            else:
                skill_attack = base_skill_attack * 3
        else:
            skill_attack = base_skill_attack
            
        skill_attack_label.config(text=f"技能攻击力: {skill_attack:.2f}")
          # 获取戈渎状态
        is_gd = gd_var.get()
        
        # 计算法术攻击力（用于后续法术伤害计算）
        if is_j1:
            if skill_selected == "二技能":
                magic_attack = skill_attack * 0.13 * 2.1
            else:
                magic_attack = skill_attack * 0.13
        else:
            if skill_selected == "二技能":
                magic_attack = skill_attack * 0.2 * 2.5
            else:
                magic_attack = skill_attack * 0.2
        
        resist_reduction = enemy_resist / 100
        
        # 如果没有选择戈渎，使用原有的单次伤害计算方式
        if not is_gd:
            # 计算物理伤害
            physical_damage = max(skill_attack - enemy_armor, skill_attack * 0.05) * (1 - enemy_reduce/100) * (1 + fragile / 100) * (1 + phy_vuln / 100)
            
            # 计算法术伤害
            magic_damage = max(magic_attack * (1 - resist_reduction), magic_attack * 0.05) * (1 - enemy_reduce/100) * (1 + fragile / 100) * (1 + mag_vuln / 100)
            
            physical_damage_label.config(text=f"物理伤害: {physical_damage:.2f}")
            magic_damage_label.config(text=f"法术伤害: {magic_damage:.2f}")
            single_hit_damage = magic_damage + physical_damage
            if single_hit_damage >= 1000000:
                single_hit_label.config(text=f"单次总伤: {int(round(single_hit_damage))}")
            else:
                single_hit_label.config(text=f"单次总伤: {single_hit_damage:.2f}")
            
            # 更新累计伤害显示(1-999次) - 简洁表格形式
            cumulative_damage = 0
            damage_lines = []
              # 每行显示4个数据，使用固定宽度格式
            for row in range(250):
                line_parts = []
                for col in range(4):
                    hit_count = row * 4 + col + 1
                    if hit_count <= 1000:
                        cumulative_damage += single_hit_damage
                        if cumulative_damage >= 1000000:
                            line_parts.append(f"{hit_count:3d}次:{int(round(cumulative_damage)):>9d}")
                        else:
                            line_parts.append(f"{hit_count:3d}次:{cumulative_damage:9.2f}")
                    else:
                        line_parts.append("            ")
                damage_lines.append("  |  ".join(line_parts))
        else:
            # 戈渎模式：前15次攻击敌方防御递减
            physical_damage_label.config(text="")
            magic_damage_label.config(text="")
            single_hit_label.config(text="")
            
            cumulative_damage = 0
            damage_lines = []
            
            # 每行显示4个数据，使用固定宽度格式
            for row in range(250):  # 64行，每行4个数据
                line_parts = []
                for col in range(4):
                    hit_count = row * 4 + col + 1
                    if hit_count <= 1000:
                        # 计算当前攻击的敌方防御值
                        if hit_count <= 15:
                            # 前15次：防御+2900递减到+100，每次减少200
                            current_armor = enemy_armor + (2900 - (hit_count - 1) * 200)
                        else:
                            # 第16次及以后：正常防御
                            current_armor = enemy_armor
                          # 计算当前攻击的伤害
                        current_physical_damage = max(skill_attack - current_armor, skill_attack * 0.05) * (1 - enemy_reduce/100) * (1 + fragile / 100) * (1 + phy_vuln / 100)
                        current_magic_damage = max(magic_attack * (1 - resist_reduction), magic_attack * 0.05) * (1 - enemy_reduce/100) * (1 + fragile / 100) * (1 + mag_vuln / 100)
                        current_single_hit = current_physical_damage + current_magic_damage
                        
                        cumulative_damage += current_single_hit
                        if cumulative_damage >= 1000000:
                            line_parts.append(f"{hit_count:3d}次:{int(round(cumulative_damage)):>9d}")
                        else:
                            line_parts.append(f"{hit_count:3d}次:{cumulative_damage:9.2f}")
                    else:
                        line_parts.append("            ")
                damage_lines.append("  |  ".join(line_parts))
        
        # 添加表头
        header = "攻击次数与累计伤害对照表" + ("（戈渎）" if is_gd else "")
        result_text = header + "\n" + "=" * 80 + "\n"
        cumulative_damage_text.config(state=tk.NORMAL)
        cumulative_damage_text.delete(1.0, tk.END)
        cumulative_damage_text.insert(tk.END, result_text)

        # 定义高亮标签
        cumulative_damage_text.tag_configure("highlight", foreground="red", font=("Consolas", 9, "bold"))

        # 插入表格内容
        for row, line in enumerate(damage_lines):
            for col, part in enumerate(line.split("  |  ")):
                hit_count = int(part.split("次")[0].strip())
                if hit_count % 16 == 0:
                    # 高亮显示16的倍数
                    cumulative_damage_text.insert(tk.END, part, "highlight")
                else:
                    cumulative_damage_text.insert(tk.END, part)
                if col < 3:
                    cumulative_damage_text.insert(tk.END, "  |  ")
            cumulative_damage_text.insert(tk.END, "\n")

        cumulative_damage_text.config(state=tk.DISABLED)
        
    except ValueError:
        attack_label.config(text="攻击力: 输入错误")
        skill_attack_label.config(text="技能攻击力: 输入错误")
        physical_damage_label.config(text="物理伤害: 输入错误")
        magic_damage_label.config(text="法术伤害: 输入错误")
        single_hit_label.config(text="单次总伤: 输入错误")
        cumulative_damage_text.config(state=tk.NORMAL)
        cumulative_damage_text.delete(1.0, tk.END)
        cumulative_damage_text.insert(tk.END, "累计伤害计算错误")
        cumulative_damage_text.config(state=tk.DISABLED)

# 添加所有输入框值变化的跟踪
for var_name in entries:
    entries[var_name].bind('<KeyRelease>', calculate_attack)

# 添加精一勾选框和技能选择值变化的跟踪
j1_var.trace_add('write', calculate_attack)
skill_var.trace_add('write', calculate_attack)
gd_var.trace_add('write', calculate_attack)

# 添加底部署名
footer_label = tk.Label(root, text="KirinRYatoCalc by potatonya", font=("黑体", 8), fg="#161616", bg="#f5f5f5")
footer_label.pack(side=tk.BOTTOM, pady=3)

# 运行主循环
root.mainloop()
