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
import math
import os
import sys

# 创建主窗口
root = tk.Tk()
root.title("夜刀计算器")
root.geometry("1280x1200")

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
    # 新增：攻速、再部署时间（可为正负，支持小数）
    ("攻速", "attack_speed"),
    ("落地攻速", "landing_attack_speed"),
    ("再部署时间", "redeploy_time"),
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

# 中部左右分栏容器：左侧（结果与累计表），右侧（时间轴）
content_frame = tk.Frame(root, bg="#f5f5f5")
content_frame.pack(pady=5, fill=tk.BOTH, expand=True)

left_col = tk.Frame(content_frame, bg="#f5f5f5")
left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10))

right_col = tk.Frame(content_frame, bg="#f5f5f5", width=560)
right_col.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 20))
right_col.pack_propagate(False)

# 输出区美化
attack_labelframe = tk.LabelFrame(left_col, text="单次伤害结果", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
attack_labelframe.pack(pady=10, fill=tk.X)

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
cumulative_labelframe = tk.LabelFrame(left_col, text="累计伤害表", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
cumulative_labelframe.pack(pady=10, fill=tk.BOTH, expand=True)

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

# 时间轴参考视图
timeline_labelframe = tk.LabelFrame(right_col, text="时间轴参考", font=("黑体", 10, "bold"), bg="#f5f5f5", padx=10, pady=10, labelanchor='nw')
timeline_labelframe.pack(pady=10, fill=tk.BOTH, expand=True)

timeline_scroll = tk.Scrollbar(timeline_labelframe)
timeline_scroll.pack(side=tk.RIGHT, fill=tk.Y)
timeline_hscroll = tk.Scrollbar(timeline_labelframe, orient=tk.HORIZONTAL)
timeline_text = tk.Text(
    timeline_labelframe,
    font=("Consolas", 9),
    bg="#f5f5f5",
    height=10,
    wrap=tk.NONE,
    yscrollcommand=timeline_scroll.set,
    xscrollcommand=timeline_hscroll.set,
    state=tk.DISABLED
)
timeline_text.pack(fill=tk.BOTH, expand=True)
timeline_scroll.config(command=timeline_text.yview)
timeline_hscroll.config(command=timeline_text.xview)
timeline_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
timeline_text.tag_configure("page_current", background="#e8f4ff")

# 翻页导航状态（用于一技能多次技能分页）
skill_block_indices = []  # 存储每次技能块头部在 Text 中的索引
current_skill_block = -1

def _timeline_goto_block(idx: int):
    global current_skill_block
    if not skill_block_indices:
        return
    if idx < 0 or idx >= len(skill_block_indices):
        return
    current_skill_block = idx
    start = skill_block_indices[idx]
    # 高亮该块的标题行
    line = start.split('.')[0]
    header_start = f"{line}.0"
    header_end = f"{line}.end"
    try:
        timeline_text.config(state=tk.NORMAL)
        timeline_text.tag_remove("page_current", "1.0", tk.END)
        timeline_text.tag_add("page_current", header_start, header_end)
        timeline_text.see(header_start)
    finally:
        timeline_text.config(state=tk.DISABLED)

def _timeline_next_page(event=None):
    if not skill_block_indices:
        return "break"
    next_idx = current_skill_block + 1 if current_skill_block >= 0 else 0
    if next_idx >= len(skill_block_indices):
        next_idx = len(skill_block_indices) - 1
    _timeline_goto_block(next_idx)
    return "break"

def _timeline_prev_page(event=None):
    if not skill_block_indices:
        return "break"
    prev_idx = current_skill_block - 1 if current_skill_block > 0 else 0
    _timeline_goto_block(prev_idx)
    return "break"

# 绑定 PageUp/PageDown 或 [] 键在时间轴文本上翻页
timeline_text.bind("<Next>", _timeline_next_page)   # PageDown
timeline_text.bind("<Prior>", _timeline_prev_page)  # PageUp
timeline_text.bind("<bracketright>", _timeline_next_page) # ] 键
timeline_text.bind("<bracketleft>", _timeline_prev_page)  # [ 键

# 计算一技能出伤时间轴（基于攻速）
def compute_skill1_timeline(raw_attack_speed: float, is_j1: bool, landing_as: float = 0.0, max_frames: int = 600):
    """
    计算一技能命中时间轴，基于新的三段式动画理论（14+14+28）：
    - 基础结构：5段二连击分为 14帧(1st) + 14帧(2nd) + 28帧(3rd,4th,5th) 三个动画片段
    - 时长判定：
        - 14帧段: 设计算值f, 若 Round(f) < Ceil(f) 则时长=Ceil(f)+1，否则 Round(f)
        - 28帧段: 直接取两段 Round(f) 相加
    - 出伤帧判定：
        - 14帧段: 取中间帧 (d+1)//2 (奇数取中，偶数下取整)
        - 28帧段: 按基准 [6, 10, 5] 比例缩放
    - 攻速机制：
        - 前9秒（<=270帧）使用 n1 = base + raw + landing_as
        - 9秒后（后11秒）使用 n2 = base + raw
    """
    base = 170 if is_j1 else 200
    
    # 辅助简单的四舍五入函数 (x.5 向上取整)
    def round_half_up(n):
        return int(n + 0.5)

    # 确定攻速数值
    n2 = raw_attack_speed + base
    n2 = max(1, min(600, n2))
    
    n1 = raw_attack_speed + landing_as + base
    n1 = max(1, min(600, n1))
    
    use_two_phase = abs(landing_as) > 0.0

    # 14帧段的时长计算
    def calc_dur_14(curr_n):
        f = 14 * 200 / curr_n
        r = round_half_up(f)
        c = math.ceil(f)
        if r < c:
            return c + 1
        return r

    # 28帧段的时长计算（实际上是两个14帧段的合成，不需要特殊比较）
    def calc_dur_14_simple(curr_n):
        f = 14 * 200 / curr_n
        return round_half_up(f)

    # 初始时间：第32帧为动画第一帧，故此时设为31
    t = 31
    times = []
    
    # 循环生成
    # 每次大循环包含 3 个片段 (Seg1, Seg2, Seg3)
    # Seg1 -> 1次双连击
    # Seg2 -> 1次双连击
    # Seg3 -> 3次双连击 (4+2)
    
    while t <= max_frames:
        for segment_idx in range(3):
            # 判断当前攻速
            curr_n = n1 if (use_two_phase and t < 270) else n2
            
            if segment_idx == 0 or segment_idx == 1:
                # 14帧基准段 (Seg1, Seg2)
                # 使用复杂的四舍五入 vs Ceil 比较逻辑
                dur = calc_dur_14(curr_n)
                # 出伤点：奇数取中，偶数下取整 -> (dur + 1) // 2
                hit_offset = (dur + 1) // 2
                
                hit_time = t + hit_offset
                if hit_time > max_frames:
                    break
                times.append(hit_time) # 第1击
                times.append(hit_time) # 第2击
                
                # 推进时间
                t += dur
                
            else:
                # Seg3: 4+2 组合。
                # 理论上由两个 14帧基准段组成，但不进行复杂比较，直接四舍五入。
                # 结构：[段1(4连击)] + [段2(2连击)]
                # 总时长 = 2 * d_base
                d_base = calc_dur_14_simple(curr_n)
                
                # 3次出伤判定 (每次双连击)
                # 1. 段1内，6/14 处
                # 2. 段1内，10/14 处
                # 3. 段2内，5/14 处 (总偏移 = d_base + 5/14 * d_base)
                
                off1 = round_half_up(d_base * 6 / 14)
                off2 = round_half_up(d_base * 10 / 14)
                off3 = d_base + round_half_up(d_base * 5 / 14)
                
                current_offsets = [off1, off2, off3]
                
                for off in current_offsets:
                    hit_time = t + off
                    if hit_time > max_frames:
                        break
                    times.append(hit_time) # 第1击
                    times.append(hit_time) # 第2击
                
                # 推进时间 (2倍时长)
                t += (2 * d_base)
            
            if t > max_frames:
                break
        
        if t > max_frames:
            break

    # 构造返回结果，兼容原有UI显示格式
    # 原UI是用 'n' 或 'n1'/'n2' 来显示攻速信息
    result = {
        'pre': 31, # 前摇/空闲帧
        'times': times,
    }
    
    # 为了UI显示“攻击间隔”，我们计算当前攻速下的各段时长供参考
    # 这里仅计算第一轮的间隔作为展示，不再返回完整的周期列表
    sample_n = n1 if use_two_phase else n2
    d1 = calc_dur_14(sample_n)
    d2 = calc_dur_14(sample_n) # 目前逻辑d1==d2
    # d3 显示为单一数值可能不再准确，因为它是 2*d_simple
    # 但为了UI兼容，我们显示总长
    d3 = 2 * calc_dur_14_simple(sample_n)
    
    # UI期望一个列表格式，我们造一个示例列表 [Seg1, Seg2, Seg3]
    intervals_display = [d1, d2, d3]

    if use_two_phase:
        # 如果双阶段，分别计算后阶段的
        d1_post = calc_dur_14(n2)
        # d3_post
        d3_post = 2 * calc_dur_14_simple(n2)
        intervals_post = [d1_post, d1_post, d3_post]
        
        result.update({
            'n1': n1,
            'n2': n2,
            'cycle_intervals_pre': intervals_display, # 前9秒参考
            'cycle_intervals_post': intervals_post,   # 后11秒参考
        })
    else:
        result.update({
            'n': n2,
            'cycle_intervals': intervals_display,
        })
        
    return result

# 三技能：逐帧覆盖范围与每格命中帧清单（基于几何判定）
def compute_skill3_frame_ranges_and_cell_hits():
    FPS = 30.0
    v = 8.0  # 格/秒
    A = FPS / v  # 30/8 = 3.75
    R = 0.51 + 0.1  # 合并半径 0.61
    max_f = 18  # 仅判定第1~18帧

    frame_ranges = []  # [(f, low, high)]
    for f in range(1, max_f + 1):
        x = (v / FPS) * f
        low = x - R
        high = x + R
        frame_ranges.append((f, low, high))

    cell_hits = {}  # k -> [frames]
    for k in range(0, 6):  # 0~5 格
        fmin = math.ceil(A * (k - R))
        fmax = math.floor(A * (k + R))
        # 与 [1,18] 取交集
        fmin = max(fmin, 1)
        fmax = min(fmax, max_f)
        hits = []
        if fmin <= fmax:
            hits = list(range(fmin, fmax + 1))
        cell_hits[k] = hits

    return frame_ranges, cell_hits

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
        attack_speed = float(entries['attack_speed'].get())
        redeploy_time = float(entries['redeploy_time'].get())
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
            
            # 更新累计伤害显示(1-1000次) - 简洁表格形式
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

        # 更新右侧“时间轴参考”视图
        timeline_text.config(state=tk.NORMAL)
        timeline_text.delete(1.0, tk.END)
        
        # 重置分页索引
        global skill_block_indices, current_skill_block
        skill_block_indices = []
        current_skill_block = -1

        if skill_selected == "一技能":
            # 插入顶部操作提示
            timeline_text.insert(tk.END, "使用 PgUp/PgDn 或 [ / ] 键翻页\n", "highlight")
            timeline_text.insert(tk.END, "=" * 30 + "\n")
            
            # 记录顶部作为第一页（概览页）
            skill_block_indices.append("1.0")

            # 技能周期：再部署时间 + 21 秒
            try:
                cycle_sec = float(entries['redeploy_time'].get()) + 21.0
            except Exception:
                cycle_sec = 21.0
            timeline_text.insert(tk.END, f"技能周期：{cycle_sec:.2f} 秒\n")
            try:
                raw_as = float(entries['attack_speed'].get())
            except Exception:
                raw_as = 0.0
            try:
                landing_as = float(entries.get('landing_attack_speed', tk.Entry()).get())
            except Exception:
                landing_as = 0.0
            # 覆盖完整技能时长，使用 21s = 630 帧
            tl = compute_skill1_timeline(raw_as, is_j1, landing_as, max_frames=630)
            if 'n' in tl:
                header = (
                    f"实际攻速 n = {tl['n']}\n"
                    f"前摇 = {tl['pre']} 帧\n"
                    f"攻击间隔(帧) = \n"
                    f"{tl['cycle_intervals']}\n"
                    + "-" * 20 + "\n"
                )
            else:
                header = (
                    f"实际攻速 n(前10秒) = {tl['n1']}\n"
                    f"实际攻速 n(后11秒) = {tl['n2']}\n"
                    f"前摇 = {tl['pre']} 帧\n"
                    f"攻击间隔(帧, 前10秒) = \n{tl['cycle_intervals_pre']}\n"
                    f"攻击间隔(帧, 后11秒) = \n{tl['cycle_intervals_post']}\n"
                    + "-" * 20 + "\n"
                )
            timeline_text.insert(tk.END, header)
            # 仅显示偶数次（每对的第二次），一行一个值，格式为 x秒y帧
            times = tl['times']
            inserted_split_marker = False
            for i in range(1, len(times), 2):
                tframe = times[i]
                # 若启用落地攻速，两段攻速分隔处加入 10 秒提示线
                if not inserted_split_marker:
                    try:
                        if abs(landing_as) > 0.0 and tframe >= 300:
                            timeline_text.insert(tk.END, "———— 10秒 ————\n")
                            inserted_split_marker = True
                    except Exception:
                        pass
                sec = tframe // 30
                rem = tframe % 30
                hit_no = i + 1  # 1-based 编号
                line = f"第{hit_no:02d}次: {sec}秒{rem}帧"
                timeline_text.insert(tk.END, line + "\n")

            # 多次技能累计（至1000次）：每次技能的内部时间轴与第一次一致；
            try:
                # 技能周期基准：再部署时间 + 21 秒
                cycle_sec = float(entries['redeploy_time'].get()) + 21.0
            except Exception:
                cycle_sec = 21.0
            
            per_skill_hits = len(times)
            # 仅偶数次（每对第二次）
            timeline_text.insert(tk.END, "\n—— 多次技能（累计至1000次）——\n")
            timeline_text.insert(tk.END, f"周期：{cycle_sec:.2f} 秒；\n每次技能起始偏移已含在单次轴(32帧)中\n")
            
            if per_skill_hits == 0:
                timeline_text.insert(tk.END, "（无可用命中点）\n")
            else:
                skill_index = 1  # 技能次数，从1开始
                while (skill_index - 1) * per_skill_hits < 1000:
                    # 每次技能的基准时刻（秒）
                    skill_start_sec = (skill_index - 1) * cycle_sec
                    
                    # 记录当前技能块头部索引（插入前的位置）
                    header_index = timeline_text.index(tk.END)
                    skill_block_indices.append(header_index)
                    timeline_text.insert(tk.END, f"—— 第{skill_index}次技能（基准起点：{skill_start_sec:.2f}秒） ——\n")
                    
                    # 遍历偶数次（2,4,6,...)
                    for j in range(2, per_skill_hits + 1, 2):
                        label_count = (skill_index - 1) * per_skill_hits + j
                        if label_count > 1000:
                            break
                        
                        # 单次技能内的相对帧数 (已经包含32帧起步)
                        # tframe 是相对于该次技能“部署动作开始”的帧数
                        tframe = times[j - 1]  
                        
                        # 将基准秒转换成帧，再加上 tframe
                        # 30帧/秒
                        # 注意：这里可能存在对齐偏差，但通常模拟器按 fps * sec 计算总帧数
                        base_frames = skill_start_sec * 30
                        total_frames = int(round(base_frames + tframe))
                        
                        sec = total_frames // 30
                        rem = total_frames % 30
                        
                        line = f"第{label_count:04d}次: {sec}秒{rem}帧"
                        timeline_text.insert(tk.END, line + "\n")
                        
                    if skill_index * per_skill_hits < 1000:
                        timeline_text.insert(tk.END, "—— 分页 ——\n\n")
                    skill_index += 1
            # 初始定位第一页并提示按键
            if skill_block_indices:
                _timeline_goto_block(0)
        elif skill_selected == "二技能":
            # 技能周期：再部署时间 + 4 秒
            try:
                cycle_val = float(entries['redeploy_time'].get()) + 4.0
            except Exception:
                cycle_val = 4.0
            timeline_text.insert(tk.END, f"技能周期：{cycle_val:.2f} 秒\n")
            timeline_text.insert(tk.END, "=" * 30 + "\n")
            timeline_text.insert(tk.END, "二技能出伤帧 (自部署起点)\n")
            timeline_text.insert(tk.END, "注:每段可能独立随机+1帧\n")
            timeline_text.insert(tk.END, "-" * 30 + "\n")
            
            base_frames = [43, 63, 65, 73, 81, 89, 91, 97, 99, 110, 112, 114, 115, 117, 118, 120]
            for i, f in enumerate(base_frames):
                sec = f // 30
                rem = f % 30
                line = f"第{i+1:02d}段: {sec}秒{rem:02d}帧"
                timeline_text.insert(tk.END, line + "\n")
        else:
            # 三技能：显示逐帧覆盖范围与每格命中帧清单
            frame_ranges, cell_hits = compute_skill3_frame_ranges_and_cell_hits()
            # 表1：逐帧覆盖范围 [x, y]
            timeline_text.insert(tk.END, "三技能逐帧覆盖范围\n")
            for f, low, high in frame_ranges:
                timeline_text.insert(tk.END, f"第{f:02d}帧: [{low:.3f}, {high:.3f}]\n")
            timeline_text.insert(tk.END, "-" * 24 + "\n")
            # 表2：每格命中帧（改为一帧一行，便于竖向浏览），并显示每格次数
            timeline_text.insert(tk.END, "三技能每格命中\n")
            counts = []
            for k in range(0, 6):
                hits = cell_hits.get(k, [])
                counts.append(len(hits))
                timeline_text.insert(tk.END, f"第{k}格（共{len(hits)}次）:\n")
                if not hits:
                    timeline_text.insert(tk.END, "  无\n\n")
                    continue
                for f in hits:
                    timeline_text.insert(tk.END, f"  第{f:02d}帧\n")
                timeline_text.insert(tk.END, "\n")
            if counts:
                summary = "/".join(str(c) for c in counts)
                timeline_text.insert(tk.END, f"各格命中次数：{summary}\n")
        timeline_text.config(state=tk.DISABLED)
        
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
        timeline_text.config(state=tk.NORMAL)
        timeline_text.delete(1.0, tk.END)
        timeline_text.insert(tk.END, "时间轴计算错误")
        timeline_text.config(state=tk.DISABLED)

# 添加所有输入框值变化的跟踪
for var_name in entries:
    entries[var_name].bind('<KeyRelease>', calculate_attack)

# 添加精一勾选框和技能选择值变化的跟踪
j1_var.trace_add('write', calculate_attack)
skill_var.trace_add('write', calculate_attack)
gd_var.trace_add('write', calculate_attack)

# 添加底部署名
footer_label = tk.Label(root, text="KirinRYatoCalc by potatonya", font=("黑体", 9), fg="#161616", bg="#f5f5f5")
footer_label.pack(side=tk.BOTTOM, pady=3)

# 运行主循环
root.mainloop()
