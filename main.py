from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import mainthread
import threading
import os
from analyzer import (
    extract_apk_completely, analyze_file_structure, extract_all_images,
    analyze_android_manifest, analyze_code_files, analyze_resource_files,
    detect_malicious_behavior, create_comprehensive_zip
)


class AnalyzerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.filechooser = FileChooserListView(size_hint=(1, 0.6))
        self.add_widget(self.filechooser)

        controls = BoxLayout(size_hint=(1, 0.1))
        self.extract_images_cb = CheckBox(active=True)
        controls.add_widget(Label(text='提取图片'))
        controls.add_widget(self.extract_images_cb)
        self.add_widget(controls)

        run_btn = Button(text='开始深度分析', size_hint=(1, 0.1))
        run_btn.bind(on_release=self.on_run)
        self.add_widget(run_btn)

        self.output = TextInput(readonly=True, size_hint=(1, 0.2))
        self.add_widget(self.output)

    def on_run(self, *args):
        selection = self.filechooser.selection
        if not selection:
            self.append_output('请先选择 APK 文件')
            return
        apk_path = selection[0]
        threading.Thread(target=self.run_analysis, args=(apk_path,)).start()

    def append_output(self, text):
        self.output.text += text + '\n'

    @mainthread
    def update_ui_text(self, text):
        self.append_output(text)

    def run_analysis(self, apk_path):
        try:
            self.update_ui_text('正在解压 APK...')
            extract_dir, files = extract_apk_completely(apk_path)

            self.update_ui_text('分析文件结构...')
            file_struct = analyze_file_structure(extract_dir)

            image_count = 0
            image_dir = None
            if self.extract_images_cb.active:
                self.update_ui_text('提取图片...')
                image_dir = f"{PathName(apk_path).stem}_photos"
                image_count = extract_all_images(extract_dir, image_dir)
                self.update_ui_text(f'提取图片: {image_count} 张')

            self.update_ui_text('分析 AndroidManifest...')
            manifest = analyze_android_manifest(extract_dir)

            self.update_ui_text('分析代码文件...')
            code = analyze_code_files(extract_dir)

            self.update_ui_text('检测恶意行为...')
            findings = detect_malicious_behavior(manifest, code, {})

            overview = [f"APK: {os.path.basename(apk_path)}", f"文件数: {file_struct['total_files']}"]
            if findings:
                overview.append('发现可疑项:')
                overview.extend(findings)
            else:
                overview.append('未发现明显恶意行为')

            self.update_ui_text('\n'.join(overview))

            zipfile = create_comprehensive_zip(apk_path, extract_dir, '\n'.join(overview), '', files, image_dir)
            self.update_ui_text(f'已生成报告压缩: {zipfile}')

        except Exception as e:
            self.update_ui_text(f'分析出错: {e}')


class AnalyzerApp(App):
    def build(self):
        return AnalyzerLayout()


def PathName(p):
    # helper to get Path-like stem without importing pathlib repeatedly
    return __import__('pathlib').Path(p)


if __name__ == '__main__':
    AnalyzerApp().run()
#!/usr/bin/env python3
"""
XingChen APK Builder - Kivy 版本
用于 Android 平台的应用程序
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import zipfile
import os
import threading
from pathlib import Path
import re
import json
import hashlib


# 设置窗口大小
Window.size = (720, 1280)


class APKAnalyzer:
    """APK 文件分析器"""
    
    def __init__(self):
        self.apk_info = {}
        
    def analyze_apk(self, apk_path):
        """分析 APK 文件"""
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk:
                # 获取 AndroidManifest.xml
                manifest = self._parse_manifest(apk)
                
                # 获取资源信息
                resources = self._list_resources(apk)
                
                # 获取文件大小
                size = os.path.getsize(apk_path)
                
                return {
                    'status': 'success',
                    'size': size,
                    'manifest': manifest,
                    'resources_count': len(resources),
                    'resources': resources[:20]  # 前20个资源
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _parse_manifest(self, apk):
        """解析 AndroidManifest.xml"""
        try:
            manifest_data = apk.read('AndroidManifest.xml')
            # 简单的二进制解析
            manifest_str = str(manifest_data)
            
            # 提取包名
            package_match = re.search(r'package=[\'\"]([^\'\"]*)[\'\"]', manifest_str)
            package = package_match.group(1) if package_match else 'Unknown'
            
            return {
                'package': package,
                'activities': [],
                'permissions': []
            }
        except:
            return {'package': 'Unknown'}
    
    def _list_resources(self, apk):
        """列出 APK 中的资源"""
        resources = []
        for name in apk.namelist():
            if name.startswith('res/'):
                resources.append(name)
        return resources
    
    def calculate_hash(self, apk_path):
        """计算 APK 文件的 MD5 哈希"""
        try:
            md5 = hashlib.md5()
            with open(apk_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"


class XingChenApp(App):
    """XingChen APK Builder 主应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analyzer = APKAnalyzer()
        self.analysis_result = None
        
    def build(self):
        """构建 UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(
            text='XingChen APK Builder',
            size_hint_y=None,
            height=50,
            font_size='24sp'
        )
        main_layout.add_widget(title)
        
        # 选项卡布局
        self.tab_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=50)
        
        # 标签按钮
        analyze_btn = Button(text='分析 APK', size_hint_x=0.5)
        analyze_btn.bind(on_press=self.show_analyze_tab)
        self.tab_layout.add_widget(analyze_btn)
        
        build_btn = Button(text='构建应用', size_hint_x=0.5)
        build_btn.bind(on_press=self.show_build_tab)
        self.tab_layout.add_widget(build_btn)
        
        main_layout.add_widget(self.tab_layout)
        
        # 内容区域
        self.content_area = BoxLayout(orientation='vertical', padding=10, spacing=10)
        main_layout.add_widget(self.content_area)
        
        # 默认显示分析界面
        self.show_analyze_tab(None)
        
        return main_layout
    
    def show_analyze_tab(self, instance):
        """显示 APK 分析界面"""
        self.content_area.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        # 文件路径输入
        path_input = TextInput(
            text='/path/to/app.apk',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(Label(text='APK 文件路径:', size_hint_y=None, height=30))
        layout.add_widget(path_input)
        
        # 分析按钮
        analyze_btn = Button(
            text='分析 APK',
            size_hint_y=None,
            height=50
        )
        analyze_btn.bind(on_press=lambda x: self.analyze_apk(path_input.text))
        layout.add_widget(analyze_btn)
        
        # 结果显示区域
        self.result_display = TextInput(
            readonly=True,
            multiline=True,
            size_hint_y=1
        )
        layout.add_widget(self.result_display)
        
        self.content_area.add_widget(layout)
    
    def show_build_tab(self, instance):
        """显示构建应用界面"""
        self.content_area.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        # 应用名称
        layout.add_widget(Label(text='应用名称:', size_hint_y=None, height=30))
        app_name_input = TextInput(
            text='My App',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(app_name_input)
        
        # 包名
        layout.add_widget(Label(text='包名 (Package Name):', size_hint_y=None, height=30))
        package_input = TextInput(
            text='org.example.myapp',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(package_input)
        
        # 版本号
        layout.add_widget(Label(text='版本号:', size_hint_y=None, height=30))
        version_input = TextInput(
            text='1.0',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(version_input)
        
        # 构建类型
        layout.add_widget(Label(text='构建类型:', size_hint_y=None, height=30))
        build_type_spinner = Spinner(
            text='调试版 (Debug)',
            values=('调试版 (Debug)', '发布版 (Release)'),
            size_hint_y=None,
            height=40
        )
        layout.add_widget(build_type_spinner)
        
        # 构建按钮
        build_btn = Button(
            text='开始构建',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 0.2, 1)
        )
        layout.add_widget(build_btn)
        
        # 状态显示
        status_display = TextInput(
            text='准备就绪',
            readonly=True,
            multiline=True,
            size_hint_y=1
        )
        layout.add_widget(status_display)
        
        self.content_area.add_widget(layout)
    
    def analyze_apk(self, path):
        """分析 APK 文件"""
        def run_analysis():
            if os.path.exists(path):
                result = self.analyzer.analyze_apk(path)
                self.display_analysis_result(result)
            else:
                self.result_display.text = f'错误: 文件不存在 - {path}'
        
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
    
    def display_analysis_result(self, result):
        """显示分析结果"""
        if result['status'] == 'error':
            self.result_display.text = f"分析失败: {result['message']}"
        else:
            output = f"""
APK 分析结果:
{'='*50}

包名: {result['manifest'].get('package', 'Unknown')}
文件大小: {result['size'] / 1024 / 1024:.2f} MB
资源数量: {result['resources_count']}

顶部资源:
{chr(10).join(result['resources'][:10])}
"""
            self.result_display.text = output


if __name__ == '__main__':
    app = XingChenApp()
    app.run()
