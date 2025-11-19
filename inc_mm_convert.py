import tkinter as tk
from tkinter import ttk
import sys
import ctypes

# --- 常量定义 ---
CONVERSION_FACTOR = 25.4
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 450


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("in_mm_convert")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        # 设置窗口始终置顶
        self.root.attributes('-topmost', True)

        # 尝试设置 Windows 高分屏适配 (让文字不模糊)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # 状态变量
        self.mode = "in_to_mm"  # 初始模式: 英寸 -> 毫米
        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", self.calculate)  # 监听输入变化实现自动转换
        self.result_var = tk.StringVar(value="0.00")
        self.unit_label_var = tk.StringVar(value="毫米 (mm)")
        self.error_msg = tk.StringVar(value="")

        self.setup_ui()

    def setup_ui(self):
        # 1. 顶部：巨大的切换按钮
        self.toggle_btn = tk.Button(
            self.root,
            text="英寸 (in)  ➜  毫米 (mm)",
            font=("Segoe UI", 18, "bold"),
            bg="#f1f5f9",
            fg="#334155",
            activebackground="#e2e8f0",
            relief="flat",
            command=self.toggle_mode,
            pady=10,
            cursor="hand2"
        )
        self.toggle_btn.pack(fill="x", padx=20, pady=(20, 10))

        # 2. 输入区域
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", padx=30, pady=10)

        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Segoe UI", 36),
            justify="center",
            bd=2,
            relief="solid",
            fg="#1e293b"
        )
        # 设置边框颜色稍微麻烦，这里用默认样式，聚焦通过逻辑处理
        self.input_entry.pack(fill="x", ipady=8)
        self.input_entry.focus()

        # 错误提示/帮助信息
        self.msg_label = tk.Label(
            self.root,
            textvariable=self.error_msg,
            font=("Segoe UI", 14),
            fg="#ef4444",  # 红色
            height=1
        )
        self.msg_label.pack()

        # 3. 结果展示区域 (最显著)
        result_frame = tk.Frame(self.root, bg="#0f172a", padx=20, pady=20)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # 圆角效果在Tkinter很难做，这里做直角矩形

        # 创建一个容器来包含结果数值和单位，用于居中显示
        center_container = tk.Frame(result_frame, bg="#0f172a")
        # 使用place方法将容器居中放置在result_frame中
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # 创建一个水平容器来放置结果数值和复制按钮
        result_row = tk.Frame(center_container, bg="#0f172a")
        result_row.pack(pady=(0, 5))

        # 结果数值
        self.result_label = tk.Label(
            result_row,
            textvariable=self.result_var,
            font=("Consolas", 54, "bold"),
            bg="#0f172a",
            fg="#4ade80"  # 亮绿色
        )
        self.result_label.pack(side="left")

        # 复制图标按钮（放在结果数值右边）
        self.copy_btn = tk.Button(
            result_row,
            text="📋",
            font=("Segoe UI", 20),
            bg="#0f172a",
            fg="#94a3b8",
            activebackground="#1e293b",
            activeforeground="#4ade80",
            relief="flat",
            borderwidth=0,
            command=self.copy_result,
            cursor="hand2",
            padx=10
        )
        self.copy_btn.pack(side="left", padx=(10, 0))

        # 结果单位
        self.unit_label = tk.Label(
            center_container,
            textvariable=self.unit_label_var,
            font=("Segoe UI", 15, "bold"),
            bg="#0f172a",
            fg="#94a3b8"  # 灰色
        )
        self.unit_label.pack()

    def toggle_mode(self):
        if self.mode == "in_to_mm":
            self.mode = "mm_to_in"
            self.toggle_btn.config(text="毫米 (mm)  ➜  英寸 (in)")
            self.unit_label_var.set("英寸 (in)")
        else:
            self.mode = "in_to_mm"
            self.toggle_btn.config(text="英寸 (in)  ➜  毫米 (mm)")
            self.unit_label_var.set("毫米 (mm)")

        # 切换后立即重新计算
        self.calculate()

    def calculate(self, *args):
        val_str = self.input_var.get().strip()

        if not val_str:
            self.result_var.set("0.00")
            self.error_msg.set("")
            return

        try:
            val = float(val_str)
            self.error_msg.set("")

            # 核心计算逻辑
            if self.mode == "in_to_mm":
                res = val * CONVERSION_FACTOR
            else:
                res = val / CONVERSION_FACTOR

            # 强制保留2位小数
            self.result_var.set(f"{res:.2f}")

        except ValueError:
            self.result_var.set("Error")
            self.error_msg.set("请输入有效数字")

    def copy_result(self):
        res = self.result_var.get()
        if res != "Error":
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
            original_text = self.copy_btn.cget("text")
            original_fg = self.copy_btn.cget("fg")
            self.copy_btn.config(text="✓", fg="#4ade80")
            self.root.after(1500, lambda: self.copy_btn.config(
                text=original_text, fg=original_fg))

# --- CLI 逻辑 ---


def run_cli():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: convert.exe <number> <in|mm>")
        sys.exit(1)

    try:
        val = float(args[0])
        unit = args[1].lower()

        if unit in ['in', 'inch', '"']:
            res = val * CONVERSION_FACTOR
            print(f"{res:.2f}")
        elif unit in ['mm', 'millimeter']:
            res = val / CONVERSION_FACTOR
            print(f"{res:.2f}")
        else:
            print("Error: Unknown unit. Use 'in' or 'mm'.")
            sys.exit(1)

        sys.exit(0)
    except ValueError:
        print("Error: Invalid number format.")
        sys.exit(1)


if __name__ == "__main__":
    # 如果有命令行参数，运行CLI模式
    if len(sys.argv) > 1:
        run_cli()
    else:
        # 否则启动GUI
        root = tk.Tk()
        app = ConverterApp(root)

        # 居中窗口
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - (WINDOW_WIDTH/2)
        y = (hs/2) - (WINDOW_HEIGHT/2)
        root.geometry('%dx%d+%d+%d' % (WINDOW_WIDTH, WINDOW_HEIGHT, x, y))

        root.mainloop()
