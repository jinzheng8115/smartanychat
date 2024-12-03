# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import webbrowser

class UIManager:
    def __init__(self, root, config_manager, on_config_save):
        self.root = root
        self.config_manager = config_manager
        self.on_config_save = on_config_save
        self.setup_ui()
        self.setup_styles()
        
        # 设置关闭按钮行为
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """处理窗口关闭事件"""
        self.root.iconify()  # 最小化窗口而不是关闭

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))

    def setup_ui(self):
        """设置UI界面"""
        self.root.title("智能写作助手 - 设置")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # 标题栏
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(title_frame, text="智能写作助手", style='Title.TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Label(title_frame, text="v1.0", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=5)

        # 创建notebook（选项卡）
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)

        # 基本设置选项卡
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本设置")
        self.setup_basic_tab(basic_frame)

        # 角色管理选项卡
        role_frame = ttk.Frame(notebook, padding="10")
        notebook.add(role_frame, text="角色管理")
        self.setup_role_tab(role_frame)

        # 使用说明选项卡
        help_frame = ttk.Frame(notebook, padding="10")
        notebook.add(help_frame, text="使用说明")
        self.setup_help_tab(help_frame)

        # 状态栏
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, padding=(2, 2))
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.status_label = ttk.Label(status_frame, text="就绪", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)

        # 底部按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, pady=(10, 0))
        
        # 使用Grid布局来对齐按钮
        btn_frame.grid_columnconfigure(0, weight=1)  # 左边空白
        btn_frame.grid_columnconfigure(3, weight=1)  # 右边空白
        
        ttk.Button(btn_frame, text="保存配置", command=self.save_config, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="退出程序", command=self.exit_program, width=15).grid(row=0, column=2, padx=5)

    def setup_basic_tab(self, parent):
        """设置基本设置选项卡"""
        # 创建左右分栏
        left_frame = ttk.Frame(parent)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # API设置（左栏）
        ttk.Label(left_frame, text="API设置", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(left_frame, text="API类型:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.api_type = ttk.Combobox(left_frame, values=['OpenAI', 'OpenAI兼容', 'Ollama'], state='readonly', width=30)
        self.api_type.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.api_type.set(self.config_manager.api_type_value)
        self.api_type.bind('<<ComboboxSelected>>', self.on_api_type_changed)

        ttk.Label(left_frame, text="API密钥:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.apikey = ttk.Entry(left_frame, width=32)
        self.apikey.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.apikey.insert(0, self.config_manager.apikey)

        ttk.Label(left_frame, text="API地址:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.base_url = ttk.Entry(left_frame, width=32)
        self.base_url.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.base_url.insert(0, self.config_manager.base_url)

        # 模型设置（右栏）
        ttk.Label(right_frame, text="模型设置", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(right_frame, text="模型名称:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.model = ttk.Entry(right_frame, width=32)
        self.model.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.model.insert(0, self.config_manager.model)

        ttk.Label(right_frame, text="补全数量:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.text_complete_number = ttk.Entry(right_frame, width=32)
        self.text_complete_number.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.text_complete_number.insert(0, str(self.config_manager.text_complete_number))

        ttk.Label(right_frame, text="温度参数:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.temperature = ttk.Entry(right_frame, width=32)
        self.temperature.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.temperature.insert(0, str(self.config_manager.temperature))

        # 其他设置（底部）
        other_frame = ttk.Frame(parent)
        other_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        ttk.Label(other_frame, text="其他设置", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 添加语言设置
        ttk.Label(other_frame, text="输出语言:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.language = ttk.Combobox(other_frame, values=['chinese', 'english'], state='readonly', width=30)
        self.language.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.language.set(self.config_manager.get_config().get('language', 'chinese'))
        
        self.keep_history = tk.BooleanVar(value=self.config_manager.keep_history)
        ttk.Checkbutton(other_frame, text="保持历史记录", variable=self.keep_history).grid(row=3, column=0, sticky=tk.W)

    def on_api_type_changed(self, event=None):
        """处理API类型改变事件"""
        # 先保存当前配置
        current_api_type = self.config_manager.api_type_value
        self.config_manager.save_api_config(
            current_api_type,
            self.apikey.get(),
            self.base_url.get(),
            self.model.get()
        )
        
        # 加载新选择的API类型配置
        api_type = self.api_type.get()
        api_config = self.config_manager.get_api_config(api_type)
        
        # 只更新API相关的配置，保持其他配置不变
        config = self.config_manager.get_config()
        config['api_type'] = api_type
        config['apikey'] = api_config.get('apikey', '')
        config['base_url'] = api_config.get('base_url', '')
        config['model'] = api_config.get('model', '')
        
        # 保存更新后的配置
        self.config_manager.save_config(config)
        
        # 更新界面
        self.apikey.delete(0, tk.END)
        self.apikey.insert(0, api_config.get('apikey', ''))
        
        self.base_url.delete(0, tk.END)
        self.base_url.insert(0, api_config.get('base_url', ''))
        
        self.model.delete(0, tk.END)
        self.model.insert(0, api_config.get('model', ''))

    def setup_role_tab(self, parent):
        """设置角色管理选项卡"""
        # 创建左右分栏
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(expand=True, fill=tk.BOTH)

        # 左侧角色列表
        left_frame = ttk.Frame(paned)
        paned.add(left_frame)

        # 角色列表标题
        list_label = ttk.Label(left_frame, text="角色列表")
        list_label.pack(pady=5)

        # 角色列表
        self.role_listbox = tk.Listbox(left_frame, width=20)
        self.role_listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.role_listbox.bind('<<ListboxSelect>>', self.on_role_selected)

        # 按钮框架
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # 添加和删除按钮
        add_button = ttk.Button(button_frame, text="添加", command=self.add_role)
        add_button.pack(side=tk.LEFT, padx=2)
        delete_button = ttk.Button(button_frame, text="删除", command=self.delete_role)
        delete_button.pack(side=tk.LEFT, padx=2)

        # 右侧角色详情
        right_frame = ttk.Frame(paned)
        paned.add(right_frame)

        # 角色详情标题
        detail_label = ttk.Label(right_frame, text="角色详情")
        detail_label.pack(pady=5)

        # 创建滚动条和Canvas
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 角色名称
        name_label = ttk.Label(scrollable_frame, text="角色名称:")
        name_label.pack(anchor=tk.W, padx=5, pady=2)
        self.name_entry = ttk.Entry(scrollable_frame)
        self.name_entry.pack(fill=tk.X, padx=5, pady=2)

        # 角色描述
        desc_label = ttk.Label(scrollable_frame, text="角色描述:")
        desc_label.pack(anchor=tk.W, padx=5, pady=2)
        self.desc_entry = ttk.Entry(scrollable_frame)
        self.desc_entry.pack(fill=tk.X, padx=5, pady=2)

        # Temperature参数
        temp_frame = ttk.Frame(scrollable_frame)
        temp_frame.pack(fill=tk.X, padx=5, pady=2)
        
        temp_label = ttk.Label(temp_frame, text="Temperature:")
        temp_label.pack(side=tk.LEFT)
        
        temp_help = ttk.Label(temp_frame, text="(?)", cursor="hand2")
        temp_help.pack(side=tk.LEFT, padx=2)
        temp_help.bind("<Button-1>", lambda e: self.show_parameter_help("temperature"))
        
        self.temp_entry = ttk.Entry(scrollable_frame)
        self.temp_entry.pack(fill=tk.X, padx=5, pady=2)

        # Text Complete Number参数
        tcn_frame = ttk.Frame(scrollable_frame)
        tcn_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tcn_label = ttk.Label(tcn_frame, text="生成长度:")
        tcn_label.pack(side=tk.LEFT)
        
        tcn_help = ttk.Label(tcn_frame, text="(?)", cursor="hand2")
        tcn_help.pack(side=tk.LEFT, padx=2)
        tcn_help.bind("<Button-1>", lambda e: self.show_parameter_help("text_complete_number"))
        
        self.tcn_entry = ttk.Entry(scrollable_frame)
        self.tcn_entry.pack(fill=tk.X, padx=5, pady=2)

        # 输入提示词
        input_label = ttk.Label(scrollable_frame, text="输入提示词:")
        input_label.pack(anchor=tk.W, padx=5, pady=2)
        self.input_text = tk.Text(scrollable_frame, height=6)
        self.input_text.pack(fill=tk.X, padx=5, pady=2)

        # 输出提示词
        output_label = ttk.Label(scrollable_frame, text="输出提示词:")
        output_label.pack(anchor=tk.W, padx=5, pady=2)
        self.output_text = tk.Text(scrollable_frame, height=6)
        self.output_text.pack(fill=tk.X, padx=5, pady=2)

        # 保存按钮
        save_button = ttk.Button(scrollable_frame, text="保存", command=self.save_role)
        save_button.pack(pady=10)

        # 打包滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 更新角色列表
        self.update_role_list()

    def setup_help_tab(self, parent):
        """设置使用说明选项卡"""
        help_text = tk.Text(parent, wrap=tk.WORD, font=('微软雅黑', 10))
        help_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 使用说明内容
        instructions = """使用说明：

1. 快捷键
   Ctrl + Alt + \\ - 补全选中文本
   Ctrl + Alt + / - 继续生成内容
   Ctrl + Esc - 清除历史记录

2. 基本操作
   - 选择文本后使用快捷键进行AI补全
   - 在角色管理中可以添加、修改、删除角色
   - 补全结果会自动复制到剪贴板
   - 使用继续生成快捷键可以让AI继续未完成的内容
   - 使用Ctrl+Esc可以清除对话历史

3. 注意事项
   - 首次使用请先配置API信息
   - 建议根据需求调整文本补全数量
   - 可以通过温度参数调整输出的随机性
"""
        help_text.insert(tk.END, instructions)
        help_text.configure(state='disabled')

    def show_parameter_help(self, param_type):
        """显示参数说明对话框"""
        if param_type == "temperature":
            title = "Temperature参数说明"
            message = """Temperature（温度）参数控制AI回答的创造性和随机性：

- 范围：0.0 到 1.0
- 建议值：
  * 0.3-0.5：适合代码生成、事实性回答
  * 0.6-0.8：适合一般对话、解释说明
  * 0.8-1.0：适合创意写作、头脑风暴

较低的值会使回答更加确定和保守
较高的值会使回答更加多样和创新"""
        else:  # text_complete_number
            title = "生成长度参数说明"
            message = """生成长度控制AI单次回答的最大字数：

- 单位：字符数（tokens）
- 建议值：
  * 2000：适合一般对话和简短回答
  * 4000：适合代码生成和技术解释
  * 3000：适合文案创作和内容生成

较小的值可以获得更快的响应
较大的值适合需要详细说明的场景"""
        
        messagebox.showinfo(title, message)

    def update_role_list(self):
        """更新角色列表"""
        self.role_listbox.delete(0, tk.END)
        roles = self.config_manager.get_config().get('roles', [])
        for role in roles:
            self.role_listbox.insert(tk.END, role['name'])

    def on_role_selected(self, event):
        """当选择角色时更新显示"""
        selection = self.role_listbox.curselection()
        if not selection:
            return
            
        role_name = self.role_listbox.get(selection[0])
        roles = self.config_manager.get_config().get('roles', [])
        role = next((r for r in roles if r['name'] == role_name), {})
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, role.get('name', ''))
        
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, role.get('description', ''))
        
        self.temp_entry.delete(0, tk.END)
        self.temp_entry.insert(0, str(role.get('temperature', 0.7)))
        
        self.tcn_entry.delete(0, tk.END)
        self.tcn_entry.insert(0, str(role.get('text_complete_number', 2000)))
        
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', role.get('input_prompt', ''))
        
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', role.get('output_prompt', ''))

    def add_role(self):
        """添加新角色"""
        name = simpledialog.askstring("添加角色", "请输入角色名称:")
        if not name:
            return
            
        # 检查名称是否已存在
        config = self.config_manager.get_config()
        roles = config.get('roles', [])
        if any(r['name'] == name for r in roles):
            messagebox.showerror("错误", "角色名称已存在")
            return

        # 创建新角色
        new_role = {
            'name': name,
            'description': '',
            'input_prompt': '',
            'output_prompt': '',
            'temperature': 0.7,
            'text_complete_number': 2000
        }
        
        # 添加到角色列表
        roles.append(new_role)
        
        # 更新配置
        config['roles'] = roles
        self.config_manager.save_config(config)
        
        # 更新列表并选中新角色
        self.update_role_list()
        items = self.role_listbox.get(0, tk.END)
        for i, item in enumerate(items):
            if item == name:
                self.role_listbox.selection_clear(0, tk.END)
                self.role_listbox.selection_set(i)
                self.role_listbox.see(i)
                self.on_role_selected(None)  # 触发选择事件
                break
                
        messagebox.showinfo("成功", "角色已添加，请在右侧编辑角色详情")

    def save_role(self):
        """保存角色设置"""
        try:
            name = self.name_entry.get().strip()
            if not name:
                raise ValueError("角色名称不能为空")

            # 验证temperature值
            try:
                temp = float(self.temp_entry.get())
                if not 0 <= temp <= 1:
                    raise ValueError
            except ValueError:
                raise ValueError("Temperature必须是0到1之间的数字")

            # 验证text_complete_number值
            try:
                tcn = int(self.tcn_entry.get())
                if tcn <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("生成长度必须是正整数")

            # 获取当前角色列表
            config = self.config_manager.get_config()
            roles = config.get('roles', [])
            
            # 检查是否存在同名角色
            existing_role_index = next((i for i, r in enumerate(roles) if r['name'] == name), -1)
            
            new_role = {
                'name': name,
                'description': self.desc_entry.get().strip(),
                'input_prompt': self.input_text.get('1.0', tk.END).strip(),
                'output_prompt': self.output_text.get('1.0', tk.END).strip(),
                'temperature': temp,
                'text_complete_number': tcn
            }
            
            if existing_role_index >= 0:
                # 更新现有角色
                roles[existing_role_index] = new_role
            else:
                # 添加新角色
                roles.append(new_role)

            # 更新配置
            config['roles'] = roles
            self.config_manager.save_config(config)

            # 更新列表
            self.update_role_list()
            messagebox.showinfo("成功", "角色设置已保存")
            
        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def delete_role(self):
        """删除角色"""
        selection = self.role_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择要删除的角色")
            return
            
        role_name = self.role_listbox.get(selection[0])
        
        # 不允许删除默认角色
        if role_name == "通用助手":
            messagebox.showerror("错误", "不能删除默认角色")
            return
            
        if messagebox.askyesno("确认", f"确定要删除角色 {role_name} 吗？"):
            # 如果删除的是当前选中的角色，先切换到默认角色
            if role_name == self.name_entry.get():
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, "通用助手")
            
            config = self.config_manager.get_config()
            roles = config.get('roles', [])
            
            # 删除角色
            roles = [r for r in roles if r['name'] != role_name]
            
            # 更新配置
            config['roles'] = roles
            self.config_manager.save_config(config)

            # 更新列表
            self.update_role_list()
            messagebox.showinfo("成功", "角色删除成功")

    def save_config(self):
        """保存配置"""
        try:
            # 保存当前API类型的配置
            current_api_type = self.api_type.get()
            self.config_manager.save_api_config(
                current_api_type,
                self.apikey.get(),
                self.base_url.get(),
                self.model.get()
            )
            
            # 保存其他配置
            config = {
                'apikey': self.apikey.get(),
                'base_url': self.base_url.get(),
                'model': self.model.get(),
                'text_complete_number': int(self.text_complete_number.get()),
                'temperature': float(self.temperature.get()),
                'keep_history': self.keep_history.get(),
                'api_type': self.api_type.get(),
                'language': self.language.get(),
                'roles': self.config_manager.get_config().get('roles', []),
                'current_role': self.get_current_role()
            }
            
            self.config_manager.save_config(config)
            self.status_label.config(text="配置已保存")
            
            # 调用回调函数，传入配置参数
            if self.on_config_save:
                self.on_config_save(config)
                
        except Exception as e:
            self.status_label.config(text=f"保存配置失败: {str(e)}")
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def exit_program(self):
        """退出程序"""
        if messagebox.askokcancel("确认退出", "确定要退出程序吗？"):
            self.root.quit()

    def get_current_role(self):
        """获取当前选中的角色"""
        selection = self.role_listbox.curselection()
        if not selection:
            return "通用助手"
        return self.role_listbox.get(selection[0])
