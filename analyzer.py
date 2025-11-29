import os
import re
import zipfile
import shutil
from pathlib import Path
import tempfile

def extract_apk_completely(apk_path, extract_dir=None):
    """Extract APK to extract_dir (created if None) and return list of files."""
    if extract_dir is None:
        extract_dir = tempfile.mkdtemp(prefix="apk_analysis_")

    with zipfile.ZipFile(apk_path, 'r') as apk_zip:
        apk_zip.extractall(extract_dir)

    file_list = []
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, extract_dir)
            file_size = os.path.getsize(file_path)
            file_list.append((rel_path, file_size))

    return extract_dir, file_list


def analyze_file_structure(extract_dir):
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
            analysis['file_types'][file_ext] = analysis['file_types'].get(file_ext, 0) + 1
            if file_ext in suspicious_extensions:
                analysis['suspicious_files'].append(os.path.relpath(file_path, extract_dir))

    return analysis


def extract_all_images(extract_dir, output_dir):
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg'}
    image_count = 0
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                rel_path = Path(root).relative_to(extract_dir)
                output_path = Path(output_dir) / rel_path / file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(os.path.join(root, file), output_path)
                image_count += 1

    return image_count


def analyze_android_manifest(extract_dir):
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
            with open(manifest_path, 'rb') as f:
                content = f.read()
                text_content = content.decode('utf-8', errors='ignore')

            permission_pattern = r'android\.permission\.[A-Z_]+'
            analysis['permissions'] = re.findall(permission_pattern, text_content)

            activity_pattern = r'<activity[^>]*android:name="([^"]*)"'
            analysis['activities'] = re.findall(activity_pattern, text_content)

            service_pattern = r'<service[^>]*android:name="([^"]*)"'
            analysis['services'] = re.findall(service_pattern, text_content)

        except Exception as e:
            analysis['error'] = f"解析Manifest失败: {e}"

    return analysis


def analyze_code_files(extract_dir):
    analysis = {
        'suspicious_strings': [],
        'dangerous_api_calls': [],
        'urls': [],
        'file_operations': []
    }

    suspicious_patterns = [
        (r'lock|锁机|解锁|屏幕锁', '锁机相关'),
        (r'accessibility|无障碍', '无障碍服务'),
        (r'qq|tencent|wechat|微信', '社交应用操作'),
        (r'killProcess|forceStop|uninstall', '进程操作'),
        (r'System\.exit|Runtime\.getRuntime', '系统操作'),
        (r'exec|su|root', 'Root相关'),
        (r'monkey|adb', '自动化操作')
    ]

    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, description in suspicious_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            analysis['suspicious_strings'].append(f"{description}: {os.path.relpath(file_path, extract_dir)}")

                    urls = re.findall(r'https?://[^\s<>\"]+|www\.[^\s<>\"]+', content)
                    analysis['urls'].extend(urls)
            except Exception:
                continue

    return analysis


def analyze_resource_files(extract_dir):
    analysis = {
        'strings': [],
        'layouts': [],
        'drawables': []
    }

    # Placeholder for future expansion
    return analysis


def detect_malicious_behavior(manifest_analysis, code_analysis, resource_analysis):
    findings = []
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

    findings.extend(code_analysis.get('suspicious_strings', []))

    suspicious_domains = ['lock', 'virus', 'hack', 'malware']
    for url in code_analysis.get('urls', []):
        if any(domain in url.lower() for domain in suspicious_domains):
            findings.append(f"可疑URL: {url}")

    return findings


def create_comprehensive_zip(apk_path, extract_dir, overview_text, details_text, files_list, image_dir=None):
    apk_name = Path(apk_path).stem
    zip_filename = f"疑似病毒_{apk_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(apk_path, f"原始APK/{apk_name}.apk")
        zipf.writestr("分析报告.txt", overview_text.encode('utf-8'))
        zipf.writestr("详细分析.txt", details_text.encode('utf-8'))
        zipf.writestr("文件列表.txt", '\n'.join([f"{p} ({s} bytes)" for p, s in files_list]).encode('utf-8'))
        if image_dir and os.path.exists(image_dir):
            for root, dirs, files in os.walk(image_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('提取图片', os.path.relpath(file_path, image_dir))
                    zipf.write(file_path, arcname)

    return zip_filename
