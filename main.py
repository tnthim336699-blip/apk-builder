import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import zipfile
import os
import shutil
import threading
from pathlib import Path
import re
import json
import hashlib
import tempfile
import subprocess

class AdvancedAPKAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("星辰锁机病毒识别程序 v2.0")
        self.root.geometry("900x700")
        self.temp_dir = None
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="星辰锁机病毒识别程序 v2.0", 
                               font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # APK选择区域
        apk_frame = ttk.LabelFrame(main_frame, text="APK文件选择", padding="10")
        apk_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.apk_path = tk.StringVar()
        ttk.Entry(apk_frame, textvariable=self.apk_path, width=70).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(apk_frame, text="选择APK", command=self.select_apk).grid(row=0, column=1)
        
        # 分析选项
        options_frame = ttk.LabelFrame(main_frame, text="分析选项", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.extract_images = tk.BooleanVar(value=True)
        self.analyze_manifest = tk.BooleanVar(value=True)
        self.analyze_code = tk.BooleanVar(value=True)
        self.analyze_resources = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="提取图片", variable=self.extract_images).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="分析Manifest", variable=self.analyze_manifest).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="分析代码", variable=self.analyze_code).grid(row=0, column=2, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="分析资源", variable=self.analyze_resources).grid(row=0, column=3, sticky=tk.W)
        
        # 分析按钮
        ttk.Button(main_frame, text="开始深度分析", command=self.start_analysis, 
                  style="Accent.TButton").grid(row=3, column=0, columnspan=3, pady=10)
        
        # 进度条和状态
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(row=0, column=1, padx=(10, 0))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        notebook = ttk.Notebook(result_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 总览标签页
        overview_tab = ttk.Frame(notebook)
        self.overview_text = scrolledtext.ScrolledText(overview_tab, height=15, width=80)
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(overview_tab, text="分析总览")
        
        # 详细结果标签页
        details_tab = ttk.Frame(notebook)
        self.details_text = scrolledtext.ScrolledText(details_tab, height=15, width=80)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(details_tab, text="详细结果")
        
        # 文件列表标签页
        files_tab = ttk.Frame(notebook)
        self.files_text = scrolledtext.ScrolledText(files_tab, height=15, width=80)
        self.files_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(files_tab, text="文件列表")
        
        # 菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def select_apk(self):
        file_path = filedialog.askopenfilename(
            title="选择APK文件",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if file_path:
            self.apk_path.set(file_path)
    
    def start_analysis(self):
        if not self.apk_path.get():
            messagebox.showerror("错误", "请先选择APK文件")
            return
        
        # 在新线程中执行分析，避免界面冻结
        thread = threading.Thread(target=self.deep_analyze_apk)
        thread.daemon = True
        thread.start()
    
    def deep_analyze_apk(self):
        try:
            apk_path = self.apk_path.get()
            apk_name = Path(apk_path).stem
            
            # 清空结果显示
            self.overview_text.delete(1.0, tk.END)
            self.details_text.delete(1.0, tk.END)
            self.files_text.delete(1.0, tk.END)
            
            self.update_status("正在解压APK...")
            self.progress['value'] = 10
            
            # 创建临时目录解压APK
            self.temp_dir = tempfile.mkdtemp(prefix=f"apk_analysis_{apk_name}_")
            
            # 完整解压APK
            self.extract_apk_completely(apk_path, self.temp_dir)
            self.progress['value'] = 30
            
            # 分析文件结构
            self.update_status("分析文件结构...")
            file_analysis = self.analyze_file_structure(self.temp_dir)
            self.progress['value'] = 40
            
            # 提取图片
            if self.extract_images.get():
                self.update_status("提取图片...")
                output_dir = f"{apk_name}のPhoto"
                image_count = self.extract_all_images(self.temp_dir, output_dir)
            else:
                image_count = 0
            
            self.progress['value'] = 50
            
            # 分析Manifest
            if self.analyze_manifest.get():
                self.update_status("分析AndroidManifest...")
                manifest_analysis = self.analyze_android_manifest(self.temp_dir)
            else:
                manifest_analysis = {}
            
            self.progress['value'] = 60
            
            # 分析代码
            if self.analyze_code.get():
                self.update_status("分析代码文件...")
                code_analysis = self.analyze_code_files(self.temp_dir)
            else:
                code_analysis = {}
            
            self.progress['value'] = 70
            
            # 分析资源
            if self.analyze_resources.get():
                self.update_status("分析资源文件...")
                resource_analysis = self.analyze_resource_files(self.temp_dir)
            else:
                resource_analysis = {}
            
            self.progress['value'] = 80
            
            # 检测恶意行为
            self.update_status("检测恶意行为...")
            malicious_findings = self.detect_malicious_behavior(
                manifest_analysis, code_analysis, resource_analysis
            )
            
            self.progress['value'] = 90
            
            # 生成报告
            self.update_status("生成报告...")
            self.generate_comprehensive_report(
                apk_name, apk_path, image_count, file_analysis, 
                manifest_analysis, code_analysis, resource_analysis, 
                malicious_findings, output_dir if self.extract_images.get() else None
            )
            
            # 创建ZIP文件
            self.create_comprehensive_zip(apk_name, apk_path, malicious_findings)
            
            self.progress['value'] = 100
            self.update_status("分析完成")
            
            # 显示完成提示
            self.overview_text.insert(tk.END, "\n\n✅ 分析完成！")
            self.overview_text.insert(tk.END, "\n请添加作者QQ: 2187250895 进行进一步查验")
            
        except Exception as e:
            self.update_status("分析出错")
            messagebox.showerror("错误", f"分析过程中出现错误: {str(e)}")
        finally:
            # 清理临时文件
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()
    
    def extract_apk_completely(self, apk_path, extract_dir):
        """完整解压APK文件"""
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk_zip:
                apk_zip.extractall(extract_dir)
            
            # 记录文件列表
            file_list = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, extract_dir)
                    file_size = os.path.getsize(file_path)
                    file_list.append(f"{rel_path} ({file_size} bytes)")
            
            self.files_text.insert(tk.END, "APK文件列表:\n")
            self.files_text.insert(tk.END, "\n".join(file_list))
            
        except Exception as e:
            raise Exception(f"解压APK失败: {str(e)}")
    
    def analyze_file_structure(self, extract_dir):
        """分析文件结构"""
        analysis = {
            'total_files': 0,
            'file_types': {},
            'largest_files': [],
            'suspicious_files': []
        }
        
        suspicious_extensions = {'.dex', '.so', '.xml', '.json', '.properties'}
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                analysis['total_files'] += 1
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                # 统计文件类型
                analysis['file_types'][file_ext] = analysis['file_types'].get(file_ext, 0) + 1
                
                # 检查可疑文件
                if file_ext in suspicious_extensions:
                    analysis['suspicious_files'].append(file_path)
        
        return analysis
    
    def extract_all_images(self, extract_dir, output_dir):
        """提取所有图片文件"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg'}
        image_count = 0
        
        os.makedirs(output_dir, exist_ok=True)
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = Path(file)
                if file_path.suffix.lower() in image_extensions:
                    # 创建相对路径
                    rel_path = Path(root).relative_to(extract_dir)
                    output_path = Path(output_dir) / rel_path / file
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(os.path.join(root, file), output_path)
                    image_count += 1
        
        return image_count
    
    def analyze_android_manifest(self, extract_dir):
        """分析AndroidManifest.xml"""
        analysis = {
            'permissions': [],
            'activities': [],
            'services': [],
            'receivers': [],
            'providers': [],
            'features': []
        }
        
        manifest_path = os.path.join(extract_dir, 'AndroidManifest.xml')
        if os.path.exists(manifest_path):
            try:
                # 尝试使用AXMLParser2或其他工具解析，这里简化处理
                with open(manifest_path, 'rb') as f:
                    content = f.read()
                    text_content = content.decode('utf-8', errors='ignore')
                
                # 简单的权限提取
                permission_pattern = r'android\.permission\.[A-Z_]+'
                analysis['permissions'] = re.findall(permission_pattern, text_content)
                
                # 提取组件
                activity_pattern = r'<activity[^>]*android:name="([^"]*)"'
                analysis['activities'] = re.findall(activity_pattern, text_content)
                
                service_pattern = r'<service[^>]*android:name="([^"]*)"'
                analysis['services'] = re.findall(service_pattern, text_content)
                
            except Exception as e:
                analysis['error'] = f"解析Manifest失败: {str(e)}"
        
        return analysis
    
    def analyze_code_files(self, extract_dir):
        """分析代码文件"""
        analysis = {
            'suspicious_strings': [],
            'dangerous_api_calls': [],
            'urls': [],
            'file_operations': []
        }
        
        # 可疑字符串模式
        suspicious_patterns = [
            (r'lock|锁机|解锁|屏幕锁', '锁机相关'),
            (r'accessibility|无障碍', '无障碍服务'),
            (r'qq|tencent|wechat|微信', '社交应用操作'),
            (r'killProcess|forceStop|uninstall', '进程操作'),
            (r'System\.exit|Runtime\.getRuntime', '系统操作'),
            (r'exec|su|root', 'Root相关'),
            (r'monkey|adb', '自动化操作')
        ]
        
        # 遍历所有文件进行分析
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # 检查可疑字符串
                        for pattern, description in suspicious_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                analysis['suspicious_strings'].append(
                                    f"{description}: {os.path.relpath(file_path, extract_dir)}"
                                )
                        
                        # 提取URL
                        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
                        analysis['urls'].extend(urls)
                        
                except:
                    continue
        
        return analysis
    
    def analyze_resource_files(self, extract_dir):
        """分析资源文件"""
        analysis = {
            'strings': [],
            'layouts': [],
            'drawables': []
        }
        
        # 分析res目录
        res_dir = os.path.join(extract_dir, 'res')
        if os.path.exists(res_dir):
            # 这里可以添加更详细的资源分析
            pass
        
        return analysis
    
    def detect_malicious_behavior(self, manifest_analysis, code_analysis, resource_analysis):
        """检测恶意行为"""
        findings = []
        
        # 检查危险权限
        dangerous_permissions = [
            "android.permission.BIND_ACCESSIBILITY_SERVICE",
            "android.permission.SYSTEM_ALERT_WINDOW", 
            "android.permission.WRITE_SECURE_SETTINGS",
            "android.permission.DEVICE_ADMIN",
            "android.permission.PACKAGE_USAGE_STATS"
        ]
        
        for perm in manifest_analysis.get('permissions', []):
            if perm in dangerous_permissions:
                findings.append(f"危险权限: {perm}")
        
        # 检查可疑代码
        if code_analysis.get('suspicious_strings'):
            findings.extend(code_analysis['suspicious_strings'])
        
        # 检查可疑URL
        suspicious_domains = ['lock', 'virus', 'hack', 'malware']
        for url in code_analysis.get('urls', []):
            if any(domain in url.lower() for domain in suspicious_domains):
                findings.append(f"可疑URL: {url}")
        
        return findings
    
    def generate_comprehensive_report(self, apk_name, apk_path, image_count, file_analysis, 
                                    manifest_analysis, code_analysis, resource_analysis,
                                    malicious_findings, output_dir):
        """生成综合分析报告"""
        
        # 总览标签页
        self.overview_text.insert(tk.END, f"APK深度分析报告 - {apk_name}\n")
        self.overview_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.overview_text.insert(tk.END, f"文件基本信息:\n")
        self.overview_text.insert(tk.END, f"• APK名称: {apk_name}\n")
        self.overview_text.insert(tk.END, f"• 文件路径: {apk_path}\n")
        self.overview_text.insert(tk.END, f"• 总文件数: {file_analysis['total_files']}\n")
        
        if output_dir:
            self.overview_text.insert(tk.END, f"• 提取图片: {image_count} 张\n")
            self.overview_text.insert(tk.END, f"• 图片目录: {output_dir}\n")
        
        self.overview_text.insert(tk.END, f"• 权限数量: {len(manifest_analysis.get('permissions', []))}\n")
        self.overview_text.insert(tk.END, f"• 活动数量: {len(manifest_analysis.get('activities', []))}\n")
        self.overview_text.insert(tk.END, f"• 服务数量: {len(manifest_analysis.get('services', []))}\n\n")
        
        # 恶意行为检测结果
        self.overview_text.insert(tk.END, "安全检测结果:\n")
        if malicious_findings:
            self.overview_text.insert(tk.END, "🚨 发现可疑行为:\n")
            for finding in malicious_findings:
                self.overview_text.insert(tk.END, f"• {finding}\n")
            
            risk_level = "高危" if len(malicious_findings) > 3 else "中危" if len(malicious_findings) > 1 else "低危"
            self.overview_text.insert(tk.END, f"\n⚠️ 风险等级: {risk_level}\n")
        else:
            self.overview_text.insert(tk.END, "✅ 未发现明显的恶意行为\n")
        
        # 详细结果标签页
        self.details_text.insert(tk.END, "详细分析结果:\n")
        self.details_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.details_text.insert(tk.END, "权限列表:\n")
        for perm in manifest_analysis.get('permissions', []):
            self.details_text.insert(tk.END, f"• {perm}\n")
        
        self.details_text.insert(tk.END, "\n活动列表:\n")
        for activity in manifest_analysis.get('activities', []):
            self.details_text.insert(tk.END, f"• {activity}\n")
        
        self.details_text.insert(tk.END, "\n服务列表:\n")
        for service in manifest_analysis.get('services', []):
            self.details_text.insert(tk.END, f"• {service}\n")
        
        self.details_text.insert(tk.END, "\n发现的URL:\n")
        for url in set(code_analysis.get('urls', [])):  # 去重
            self.details_text.insert(tk.END, f"• {url}\n")
    
    def create_comprehensive_zip(self, apk_name, apk_path, malicious_findings):
        """创建综合报告ZIP文件"""
        zip_filename = f"疑似病毒{apk_name}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加APK文件
            zipf.write(apk_path, f"原始APK/{apk_name}.apk")
            
            # 添加分析报告
            report_content = self.overview_text.get(1.0, tk.END)
            zipf.writestr("分析报告.txt", report_content.encode('utf-8'))
            
            # 添加详细报告
            details_content = self.details_text.get(1.0, tk.END)
            zipf.writestr("详细分析.txt", details_content.encode('utf-8'))
            
            # 添加文件列表
            files_content = self.files_text.get(1.0, tk.END)
            zipf.writestr("文件列表.txt", files_content.encode('utf-8'))
            
            # 添加图片目录（如果存在）
            image_dir = f"{apk_name}のPhoto"
            if os.path.exists(image_dir):
                for root, dirs, files in os.walk(image_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("提取图片", os.path.relpath(file_path, image_dir))
                        zipf.write(file_path, arcname)
        
        self.overview_text.insert(tk.END, f"\n已创建完整报告: {zip_filename}\n")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """星辰锁机病毒识别程序 v2.0

作者QQ: 2187250895

功能特性:
• 完整解压APK文件
• 深度分析所有文件内容
• 检测锁机、无障碍服务等恶意行为
• 分析权限、组件和代码
• 提取所有图片资源
• 生成详细分析报告

注意: 本工具提供深度分析，检测结果请结合人工验证。"""
        
        messagebox.showinfo("关于", about_text)

def main():
    root = tk.Tk()
    app = AdvancedAPKAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()