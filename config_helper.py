#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券商配置助手工具
帮助用户创建和验证券商配置文件
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import base64
from datetime import datetime

class ConfigHelper:
    """配置助手主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("券商配置助手")
        self.root.geometry("600x700")
        
        # 配置目录
        self.config_dir = "my_configs"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_label = ttk.Label(self.root, text="券商配置助手", 
                               font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(pady=20)
        
        # 创建笔记本控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建各个券商的配置页面
        self.create_huatai_tab()
        self.create_yjb_tab()
        self.create_yinhe_tab()
        self.create_xueqiu_tab()
        
        # 创建工具页面
        self.create_tools_tab()
    
    def create_huatai_tab(self):
        """创建华泰证券配置页面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="华泰证券")
        
        # 说明文本
        info_text = """
华泰证券配置说明：
1. 需要获取加密后的交易密码(trdpwd)
2. 通过浏览器开发者工具获取
3. 登录华泰网站时查看Network请求
"""
        ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=10)
        
        # 输入字段
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.ht_vars = {}
        fields = [
            ("账号", "user"),
            ("登录密码", "password"),
            ("通讯密码", "comm_password"),
            ("加密交易密码", "trdpwd"),
            ("资金账号", "account")
        ]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(fields_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(fields_frame, textvariable=var, width=40)
            if key in ['password', 'comm_password', 'trdpwd']:
                entry.config(show='*')
            entry.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            self.ht_vars[key] = var
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="生成配置文件", 
                  command=lambda: self.generate_config('ht', self.ht_vars)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="获取密码帮助", 
                  command=self.show_huatai_help).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="测试连接", 
                  command=lambda: self.test_connection('ht')).pack(side=tk.RIGHT)
    
    def create_yjb_tab(self):
        """创建佣金宝配置页面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="佣金宝")
        
        # 说明文本
        info_text = """
佣金宝配置说明：
1. 需要获取加密后的登录密码
2. 通过浏览器开发者工具获取
3. 登录佣金宝网站时查看Network请求
"""
        ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=10)
        
        # 输入字段
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.yjb_vars = {}
        fields = [
            ("账号", "user"),
            ("加密密码", "password"),
            ("资金账号", "account")
        ]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(fields_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(fields_frame, textvariable=var, width=40)
            if key == 'password':
                entry.config(show='*')
            entry.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            self.yjb_vars[key] = var
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="生成配置文件", 
                  command=lambda: self.generate_config('yjb', self.yjb_vars)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="获取密码帮助", 
                  command=self.show_yjb_help).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="测试连接", 
                  command=lambda: self.test_connection('yjb')).pack(side=tk.RIGHT)
    
    def create_yinhe_tab(self):
        """创建银河证券配置页面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="银河证券")
        
        # 说明文本
        info_text = """
银河证券配置说明：
1. 使用明文密码即可
2. 需要安装验证码识别工具
3. 推荐安装: pip install ddddocr
"""
        ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=10)
        
        # 输入字段
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.yh_vars = {}
        fields = [
            ("账号", "user"),
            ("登录密码", "password"),
            ("资金账号", "account")
        ]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(fields_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(fields_frame, textvariable=var, width=40)
            if key == 'password':
                entry.config(show='*')
            entry.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            self.yh_vars[key] = var
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="生成配置文件", 
                  command=lambda: self.generate_config('yh', self.yh_vars)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="安装验证码工具", 
                  command=self.install_ocr_tools).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="测试连接", 
                  command=lambda: self.test_connection('yh')).pack(side=tk.RIGHT)
    
    def create_xueqiu_tab(self):
        """创建雪球模拟盘配置页面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="雪球模拟")
        
        # 说明文本
        info_text = """
雪球模拟盘配置说明：
1. 适合新手练习使用
2. 需要先在雪球网站创建模拟组合
3. 从组合URL中获取组合代码
"""
        ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=10)
        
        # 输入字段
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.xq_vars = {}
        fields = [
            ("雪球用户名", "username"),
            ("雪球密码", "password"),
            ("组合代码", "portfolio_code"),
            ("市场代码", "portfolio_market")
        ]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(fields_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar()
            if key == 'portfolio_market':
                var.set('cn')  # 默认值
            entry = ttk.Entry(fields_frame, textvariable=var, width=40)
            if key == 'password':
                entry.config(show='*')
            entry.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            self.xq_vars[key] = var
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="生成配置文件", 
                  command=lambda: self.generate_config('xq', self.xq_vars)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="获取组合代码帮助", 
                  command=self.show_xueqiu_help).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="测试连接", 
                  command=lambda: self.test_connection('xq')).pack(side=tk.RIGHT)
    
    def create_tools_tab(self):
        """创建工具页面"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="工具")
        
        # 配置文件管理
        mgmt_frame = ttk.LabelFrame(frame, text="配置文件管理", padding=10)
        mgmt_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(mgmt_frame, text="查看配置文件", 
                  command=self.view_configs).pack(side=tk.LEFT, padx=5)
        ttk.Button(mgmt_frame, text="备份配置文件", 
                  command=self.backup_configs).pack(side=tk.LEFT, padx=5)
        ttk.Button(mgmt_frame, text="导入配置文件", 
                  command=self.import_config).pack(side=tk.LEFT, padx=5)
        
        # 密码工具
        pwd_frame = ttk.LabelFrame(frame, text="密码工具", padding=10)
        pwd_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(pwd_frame, text="明文密码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.plain_pwd_var = tk.StringVar()
        ttk.Entry(pwd_frame, textvariable=self.plain_pwd_var, width=30, show='*').grid(row=0, column=1, padx=5)
        
        ttk.Label(pwd_frame, text="加密结果:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.encrypted_pwd_var = tk.StringVar()
        ttk.Entry(pwd_frame, textvariable=self.encrypted_pwd_var, width=30, state='readonly').grid(row=1, column=1, padx=5)
        
        ttk.Button(pwd_frame, text="MD5加密", 
                  command=self.encrypt_md5).grid(row=0, column=2, padx=5)
        ttk.Button(pwd_frame, text="Base64编码", 
                  command=self.encrypt_base64).grid(row=1, column=2, padx=5)
        
        # 系统检查
        check_frame = ttk.LabelFrame(frame, text="系统检查", padding=10)
        check_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(check_frame, text="检查Python模块", 
                  command=self.check_modules).pack(side=tk.LEFT, padx=5)
        ttk.Button(check_frame, text="检查网络连接", 
                  command=self.check_network).pack(side=tk.LEFT, padx=5)
        ttk.Button(check_frame, text="检查验证码工具", 
                  command=self.check_ocr_tools).pack(side=tk.LEFT, padx=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(frame, text="操作日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_config(self, broker_type, vars_dict):
        """生成配置文件"""
        try:
            # 收集配置数据
            config_data = {}
            for key, var in vars_dict.items():
                value = var.get().strip()
                if not value:
                    messagebox.showerror("错误", f"请填写{key}字段")
                    return
                config_data[key] = value
            
            # 生成文件名
            filename = f"{broker_type}.json"
            filepath = os.path.join(self.config_dir, filename)
            
            # 写入配置文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            self.log(f"配置文件已生成: {filepath}")
            messagebox.showinfo("成功", f"配置文件已保存到: {filepath}")
            
        except Exception as e:
            self.log(f"生成配置文件失败: {e}")
            messagebox.showerror("错误", f"生成配置文件失败: {e}")
    
    def test_connection(self, broker_type):
        """测试连接"""
        try:
            import easytrader
            
            config_file = os.path.join(self.config_dir, f"{broker_type}.json")
            if not os.path.exists(config_file):
                messagebox.showerror("错误", "请先生成配置文件")
                return
            
            # 尝试连接
            trader = easytrader.use(broker_type)
            trader.prepare(config_file)
            
            self.log(f"{broker_type}连接测试成功")
            messagebox.showinfo("成功", "连接测试成功！")
            
        except ImportError:
            messagebox.showerror("错误", "easytrader模块未安装")
        except Exception as e:
            self.log(f"{broker_type}连接测试失败: {e}")
            messagebox.showerror("失败", f"连接测试失败: {e}")
    
    def show_huatai_help(self):
        """显示华泰证券帮助"""
        help_text = """
获取华泰证券加密密码步骤：

1. 打开华泰证券官网
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 登录账号
5. 找到登录的POST请求
6. 查看请求参数中的trdpwd值
7. 复制该值到配置中

注意：加密密码有时效性，可能需要定期更新
"""
        messagebox.showinfo("华泰证券配置帮助", help_text)
    
    def show_yjb_help(self):
        """显示佣金宝帮助"""
        help_text = """
获取佣金宝加密密码步骤：

1. 打开佣金宝官网
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 登录账号
5. 找到登录的POST请求
6. 查看请求参数中的password值
7. 复制该值到配置中

建议使用无痕模式避免缓存干扰
"""
        messagebox.showinfo("佣金宝配置帮助", help_text)
    
    def show_xueqiu_help(self):
        """显示雪球帮助"""
        help_text = """
获取雪球组合代码步骤：

1. 登录雪球网站
2. 进入模拟交易页面
3. 创建新的投资组合
4. 进入组合页面
5. 从URL中获取组合ID
   例如：https://xueqiu.com/P/ZH123456
   组合代码就是：ZH123456

市场代码固定填写：cn
"""
        messagebox.showinfo("雪球模拟盘配置帮助", help_text)
    
    def install_ocr_tools(self):
        """安装验证码识别工具"""
        import subprocess
        import sys
        
        try:
            # 安装ddddocr
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ddddocr'])
            self.log("ddddocr安装成功")
            messagebox.showinfo("成功", "验证码识别工具安装成功")
        except Exception as e:
            self.log(f"安装失败: {e}")
            messagebox.showerror("失败", f"安装失败: {e}")
    
    def encrypt_md5(self):
        """MD5加密"""
        plain_text = self.plain_pwd_var.get()
        if plain_text:
            md5_hash = hashlib.md5(plain_text.encode()).hexdigest()
            self.encrypted_pwd_var.set(md5_hash)
            self.log(f"MD5加密完成")
    
    def encrypt_base64(self):
        """Base64编码"""
        plain_text = self.plain_pwd_var.get()
        if plain_text:
            base64_encoded = base64.b64encode(plain_text.encode()).decode()
            self.encrypted_pwd_var.set(base64_encoded)
            self.log(f"Base64编码完成")
    
    def check_modules(self):
        """检查Python模块"""
        modules = ['easytrader', 'easyquant', 'akshare', 'pandas', 'numpy']
        results = []
        
        for module in modules:
            try:
                __import__(module)
                results.append(f"✓ {module}")
            except ImportError:
                results.append(f"✗ {module}")
        
        result_text = "\n".join(results)
        self.log(f"模块检查结果:\n{result_text}")
        messagebox.showinfo("模块检查", result_text)
    
    def check_network(self):
        """检查网络连接"""
        import urllib.request
        
        urls = [
            ('百度', 'https://www.baidu.com'),
            ('华泰证券', 'https://www.htsc.com.cn'),
            ('雪球', 'https://xueqiu.com')
        ]
        
        results = []
        for name, url in urls:
            try:
                urllib.request.urlopen(url, timeout=5)
                results.append(f"✓ {name}")
            except:
                results.append(f"✗ {name}")
        
        result_text = "\n".join(results)
        self.log(f"网络检查结果:\n{result_text}")
        messagebox.showinfo("网络检查", result_text)
    
    def check_ocr_tools(self):
        """检查验证码工具"""
        tools = []
        
        # 检查ddddocr
        try:
            import ddddocr
            tools.append("✓ ddddocr")
        except ImportError:
            tools.append("✗ ddddocr")
        
        # 检查tesseract
        import subprocess
        try:
            subprocess.run(['tesseract', '--version'], 
                         capture_output=True, check=True)
            tools.append("✓ tesseract")
        except:
            tools.append("✗ tesseract")
        
        result_text = "\n".join(tools)
        self.log(f"验证码工具检查结果:\n{result_text}")
        messagebox.showinfo("验证码工具检查", result_text)
    
    def view_configs(self):
        """查看配置文件"""
        if not os.path.exists(self.config_dir):
            messagebox.showinfo("提示", "配置目录不存在")
            return
        
        files = [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
        if not files:
            messagebox.showinfo("提示", "没有找到配置文件")
            return
        
        file_list = "\n".join(files)
        messagebox.showinfo("配置文件列表", f"找到以下配置文件:\n\n{file_list}")
    
    def backup_configs(self):
        """备份配置文件"""
        import shutil
        
        backup_dir = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            shutil.copytree(self.config_dir, backup_dir)
            self.log(f"配置文件已备份到: {backup_dir}")
            messagebox.showinfo("成功", f"配置文件已备份到: {backup_dir}")
        except Exception as e:
            self.log(f"备份失败: {e}")
            messagebox.showerror("失败", f"备份失败: {e}")
    
    def import_config(self):
        """导入配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            try:
                import shutil
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.config_dir, filename)
                shutil.copy2(file_path, dest_path)
                
                self.log(f"配置文件已导入: {filename}")
                messagebox.showinfo("成功", f"配置文件已导入: {filename}")
            except Exception as e:
                self.log(f"导入失败: {e}")
                messagebox.showerror("失败", f"导入失败: {e}")
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        print(log_message.strip())
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动券商配置助手...")
    app = ConfigHelper()
    app.run()

if __name__ == "__main__":
    main()