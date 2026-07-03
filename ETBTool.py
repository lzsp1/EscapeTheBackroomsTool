import os
import sys
import json
import shutil
import datetime
import urllib.request
import webbrowser
import subprocess
import winreg
import re
import zipfile
import time
from typing import List, Tuple
import base64

import requests

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTextEdit,
                             QScrollArea, QFrame, QDialog, QCheckBox,
                             QMessageBox, QComboBox, QGroupBox, QListWidget,
                             QListWidgetItem, QMenu, QAction, QSplitter,
                             QSlider, QSizePolicy, QSpacerItem, QButtonGroup,
                             QRadioButton, QGridLayout, QProgressBar, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                             QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import (Qt, QUrl, QThread, pyqtSignal, QSize, QTimer, QMetaObject,
                          QMimeData, QPoint, QRect, QPropertyAnimation, QEasingCurve)
from PyQt5.QtGui import (QFont, QIcon, QDesktopServices, QFontMetrics, QPixmap, QPainter, QColor, QPen,
                         QBrush)

VERSION = "3.9.44"
UPDATE_CHECK_URL = "https://raw.giteeusercontent.com/yunjie666/etb-mod-names/raw/master/version.json"
WEBSITE_URL = "https://taolihoushiwanyouqun.wordpress.com/"
CONFIG_DIR = None
CONFIG_FILE = None
LOG_FILE = None
OLD_CONFIG_CLEANED_FLAG = None

LOCAL_APP_DATA = os.environ.get('LOCALAPPDATA', '')
SAVE_PATH = os.path.join(LOCAL_APP_DATA, 'EscapeTheBackrooms', 'Saved', 'SaveGames')
CRASH_PATH = os.path.join(LOCAL_APP_DATA, 'EscapeTheBackrooms', 'Saved', 'Crashes')
GAME_BASE_PATH = os.path.join(LOCAL_APP_DATA, 'EscapeTheBackrooms')

DIFFICULTY_MAP = {"Easy": "容易", "Normal": "普通", "Hard": "困难", "Nightmare": "噩梦"}
DIFFICULTY_LIST = ["Easy", "Normal", "Hard", "Nightmare"]
DIFFICULTY_COLORS = {"容易": "#2ecc71", "普通": "#3498db", "困难": "#f39c12", "噩梦": "#e74c3c"}

_AES_KEY = b'ETBTool2024SecretKey'

def _encrypt(data: str) -> str:
    bdata = data.encode('utf-8')
    key = _AES_KEY
    encrypted = bytes([bdata[i] ^ key[i % len(key)] for i in range(len(bdata))])
    return base64.b64encode(encrypted).decode('ascii')

def _decrypt(encrypted: str) -> str:
    encrypted_bytes = base64.b64decode(encrypted.encode('ascii'))
    key = _AES_KEY
    decrypted = bytes([encrypted_bytes[i] ^ key[i % len(key)] for i in range(len(encrypted_bytes))])
    return decrypted.decode('utf-8')

def parse_version(v: str) -> tuple:
    try:
        return tuple(map(int, v.split('.')))
    except:
        return (0,)
def is_newer(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)

LANG = {
    "zh": {
        "window_title": "逃离后室游戏工具",
        "clean_files": "清理文件",
        "clean_save": "清理存档",
        "clean_crash": "清理崩溃日志",
        "file_ops": "文件操作",
        "mod_management": "Mod 管理",
        "download_mod": "下载mod",
        "open_save": "打开存档文件夹",
        "open_crash": "打开崩溃日志文件夹",
        "show_path": "查看游戏路径",
        "log": "日志",
        "clear_log": "清空日志",
        "about_settings": "关于与设置",
        "uninstall": "卸载",
        "font_size": "字体大小",
        "check_update": "检查更新",
        "website": "官网",
        "about": "关于",
        "copyright": "逃离后室玩友群制作，未开源",
        "save_folder_not_exist": "存档文件夹不存在，请先运行游戏！",
        "crash_folder_not_exist": "崩溃日志文件夹不存在，请先运行游戏！",
        "no_archive_found": "未检测到有效的游戏存档文件！",
        "no_crash_found": "无崩溃日志文件夹，无需清理！",
        "clean_crash_success": "崩溃日志清理完成！",
        "clean_crash_fail": "清理崩溃日志失败：",
        "delete_success": "自定义删除完成！",
        "delete_fail": "删除失败：",
        "delete_confirm_msg": "已成功删除 {} 个项目！",
        "select_all": "全选",
        "select_none": "全不选",
        "confirm_delete": "确认删除",
        "open_selected": "打开选中文件夹",
        "about_title": "提示",
        "version_label": f"版本 {VERSION}",
        "about_copyright": "逃离后室玩友群",
        "about_desc": "专为《逃离后室》设计的存档、日志和模组管理工具。\n逃离后室玩友群 - 公益项目",
        "init_complete": "工具已启动",
        "check_update_title": "检查更新",
        "checking_update": "正在检查更新...",
        "stay_on_page_hint": "⚠️ 提示：不要离开此页面，否则检查会被终止",
        "update_available": "发现新版本 V{}",
        "update_notes": "更新内容：",
        "already_latest": "当前已是最新版本。",
        "update_error": "检查更新失败：{}\n请尝试重新检查",
        "download_now": "下载更新",
        "later": "稍后",
        "open_save_log": "✅ 打开存档文件夹\n路径：{}",
        "open_crash_log": "✅ 打开崩溃日志文件夹\n路径：{}",
        "show_path_log": "📌 游戏路径：\n存档路径：{}\n崩溃日志路径：{}",
        "clean_crash_log": "✅ 已删除崩溃日志文件夹：{}",
        "clean_archive_log": "✅ 已删除存档：{} 【{}难度】",
        "path_info": "游戏路径信息",
        "save_path_label": "存档路径：",
        "crash_path_label": "崩溃日志路径：",
        "copy_save_path": "复制存档路径",
        "copy_crash_path": "复制崩溃路径",
        "copy_all_paths": "复制全部路径",
        "warning_title": "提示",
        "copy_path_log": "📋 已复制路径到剪贴板",
        "open_config_dir": "打开软件配置目录",
        "config_dir_warning": "警告：您即将打开软件配置目录。\n请勿自行删除该文件夹内的任何文件，否则可能导致程序异常。",
        "config_dir_known": "我已知晓",
        "old_config_found": "检测到旧版配置文件",
        "old_config_msg": "检测到旧版配置文件文件夹：\n{}\n\n是否删除？（删除不影响当前使用）",
        "old_config_deleted": "已删除旧版配置文件。",
        "old_config_delete_failed": "删除旧版配置文件失败：{}",
        "retry_check": "重新检查",
        "uninstall_game": "卸载游戏",
        "uninstall_game_confirm": "【第三方卸载提醒】\n\n此为第三方卸载方式，非 Steam 官方卸载。\n卸载后如需再次游玩《逃离后室》，请通过 Steam 客户端验证游戏文件完整性，以重新下载缺失文件。\n\n如有 MOD 和存档，建议提前备份。\n\n是否确认卸载游戏？",
        "uninstall_game_confirm_ok": "确定",
        "uninstall_game_success": "游戏已卸载。",
        "uninstall_game_fail": "卸载游戏失败：{}",
        "uninstall_game_not_found": "未找到游戏安装目录。请手动删除。",
        "uninstall_known": "确定",
        "uninstall_start": "开始卸载",
        "log_uninstall_game_start": "🗑️ 开始卸载游戏...",
        "log_uninstall_game_success": "✅ 游戏卸载成功",
        "log_uninstall_game_fail": "❌ 游戏卸载失败：{}",
        "log_old_config_detected": "🔍 检测到旧版配置文件文件夹：{}",
        "log_old_config_cleaned": "🗑️ 用户已同意清理旧版配置文件夹：{}",
        "log_old_config_skip": "⏭️ 用户未同意清理旧版配置文件夹：{}",
        "multi_select_hint": "💡 提示：按住 Ctrl 键 + 鼠标左键可多选模组（支持打包、删除、右键批量禁用/启用）",
        "other": "其它",
        "disable_selected": "禁用选中的模组",
        "enable_selected": "启用选中的模组",
        "bulk_operation_notice": "批量操作已执行：",
        "thanks": "感谢名单",
        "thanks_message": "感谢以下成员|集体：\n• 使用本软件的所有用户\n• 逃离后室玩友群全体成员\n\n特别感谢 angel丶默澜(QQ 3584545620)",
        "submit_nickname": "提交昵称",
        "already_top_level": "已经是最高层级（与 Mod 无关）",
        "search_placeholder": "🔍 搜索模组（文件名/中文名）",
        "no_search_result": "也许您没有安装这个mod，或者还没有收录这个昵称，可以在上方点击【提交昵称】提交",
        "download_mod_confirm": "即将打开逃离后室模组库，是否继续？",
        "download_mod_url": "https://etbtoolmod.xn--online-o20ki81q.top/"
    }
}

def get_config_dir() -> str:
    global CONFIG_DIR
    if CONFIG_DIR:
        return CONFIG_DIR
    drives = [d for d in ['D:', 'E:', 'F:', 'G:'] if os.path.exists(d)]
    base = drives[0] if drives else os.path.expanduser("~")
    config_dir = os.path.join(base, '.EscapeTool')
    os.makedirs(config_dir, exist_ok=True)
    CONFIG_DIR = config_dir
    return config_dir

def load_config() -> dict:
    global CONFIG_DIR, CONFIG_FILE, LOG_FILE, OLD_CONFIG_CLEANED_FLAG
    CONFIG_DIR = get_config_dir()
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
    LOG_FILE = os.path.join(CONFIG_DIR, 'log.txt')
    OLD_CONFIG_CLEANED_FLAG = os.path.join(CONFIG_DIR, 'cleaned_old_config.flag')
    default = {"font_size": 11}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default.update(data)
        except:
            pass
    return default

def save_config(font_size: int = None):
    if CONFIG_FILE:
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            if font_size is not None:
                config["font_size"] = font_size
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except:
            pass

def load_log_from_file() -> List[str]:
    if LOG_FILE and os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n') for line in f.readlines()]
        except:
            return []
    return []
def append_log_to_file(msg: str):
    if LOG_FILE:
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except:
            pass
def clear_log_file():
    if LOG_FILE and os.path.exists(LOG_FILE):
        try:
            open(LOG_FILE, 'w', encoding='utf-8').close()
        except:
            pass

class ETBApi:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api.php"
        self.token = None
        self.username = None
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ETBModClient/1.0"})

    def register(self, username, password, email=""):
        data = {"action": "register", "username": username, "password": password, "email": email}
        result = self._post(data)
        if result.get("success") and result.get("token"):
            self.token = result["token"]
            self.username = username
        return result

    def login(self, username, password):
        data = {"action": "login", "username": username, "password": password}
        result = self._post(data)
        if result.get("success") and result.get("token"):
            self.token = result["token"]
            self.username = username
            self.save_auth(username, self.token)
        else:
            self.token = None
            self.username = None
        return result

    def logout(self):
        result = self._get({"action": "logout"})
        self.token = None
        self.username = None
        self.clear_auth()
        return result

    def is_logged_in(self):
        return self.token is not None

    def get_user(self):
        return self._get({"action": "user"})

    def get_mods(self, search=""):
        params = {"action": "mods"}
        if search:
            params["search"] = search
        return self._get(params)

    def get_mod(self, mod_id):
        return self._get({"action": "mod", "id": mod_id})

    def download(self, mod_id, save_dir="./downloads", filename=None, progress_callback=None):
        if not self.token:
            return {"success": False, "message": "请先登录"}
        url = f"{self.api_url}?action=download&id={mod_id}&token={self.token}"
        try:
            resp = self.session.get(url, timeout=self.timeout, stream=True)
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    error_data = resp.json()
                    return {"success": False, "message": error_data.get("message", "下载失败")}
                except:
                    pass
            if resp.status_code == 200:
                if not filename:
                    cd = resp.headers.get("Content-Disposition", "")
                    if "filename=" in cd:
                        filename = cd.split("filename=")[-1].strip('"').strip("'")
                    else:
                        filename = f"mod_{mod_id}.pak"
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, filename)
                total_size = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(file_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and callable(progress_callback):
                                progress_callback(downloaded, total_size)
                return {"success": True, "file_path": file_path, "file_size": downloaded, "message": "下载完成"}
            elif resp.status_code == 403:
                return {"success": False, "message": "请先登录后再下载"}
            else:
                return {"success": False, "message": f"服务器返回错误：{resp.status_code}"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "下载超时，请检查网络连接"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "无法连接服务器"}
        except Exception as e:
            return {"success": False, "message": f"下载失败：{str(e)}"}

    def get_notice(self):
        return self._get({"action": "notice"})

    def _get(self, params):
        if self.token:
            params["token"] = self.token
        try:
            resp = self.session.get(self.api_url, params=params, timeout=self.timeout)
            return resp.json()
        except:
            return {"success": False, "message": "请求失败"}

    def _post(self, data):
        if self.token:
            data["token"] = self.token
        try:
            resp = self.session.post(self.api_url, data=data, timeout=self.timeout)
            return resp.json()
        except:
            return {"success": False, "message": "请求失败"}

    def save_auth(self, username, token):
        data = {"username": username, "token": token, "login_time": time.time()}
        json_str = json.dumps(data)
        enc = _encrypt(json_str)
        auth_file = os.path.join(get_config_dir(), 'auth.dat')
        with open(auth_file, 'w') as f:
            f.write(enc)

    def load_auth(self):
        auth_file = os.path.join(get_config_dir(), 'auth.dat')
        if not os.path.exists(auth_file):
            return None
        try:
            with open(auth_file, 'r') as f:
                enc = f.read()
            json_str = _decrypt(enc)
            data = json.loads(json_str)
            if self._check_token_valid(data):
                return data
            else:
                self.clear_auth()
                return None
        except Exception:
            self.clear_auth()
            return None

    def _check_token_valid(self, data):
        login_time = data.get('login_time', 0)
        if time.time() - login_time > 20 * 24 * 3600:
            return False
        return True

    def clear_auth(self):
        auth_file = os.path.join(get_config_dir(), 'auth.dat')
        if os.path.exists(auth_file):
            try:
                os.remove(auth_file)
            except:
                pass

    def auto_login(self):
        data = self.load_auth()
        if data:
            self.token = data['token']
            self.username = data['username']
            return True
        return False

class OldConfigScanThread(QThread):
    finished = pyqtSignal(list)
    def run(self):
        found = []
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        for drive in drives:
            target = os.path.join(drive, '.QingLiSystem')
            if os.path.isdir(target):
                found.append(target)
        self.finished.emit(found)

def get_icon():
    base_dir = os.path.dirname(sys.argv[0])
    icon_path = os.path.join(base_dir, 'icon.ico')
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(52, 73, 94))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor(255, 255, 255), 2))
    painter.setBrush(QColor(52, 73, 94))
    painter.drawRoundedRect(0, 0, 64, 64, 10, 10)
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Microsoft YaHei", 32, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "逃")
    painter.end()
    return QIcon(pixmap)

class UpdateCheckThread(QThread):
    finished = pyqtSignal(dict, str)
    def run(self):
        urls = [
            "https://raw.giteeusercontent.com/yunjie666/etb-mod-names/raw/master/version.json",
            "https://gitee.com/yunjie666/etb-mod-names/raw/master/version.json"
        ]
        for url in urls:
            for attempt in range(2):
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        self.finished.emit(data, "")
                        return
                except:
                    if attempt == 1:
                        break
                    time.sleep(1)
        self.finished.emit({}, "the read operation timed out")

class ContentPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

class LogPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr("log"))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QTextEdit { font-family: Consolas; background-color: #fef9e7; border: 1px solid #e0e0e0; border-radius: 8px; }")
        layout.addWidget(self.log_text)
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton(self.parent.tr('clear_log'))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; font-weight: 500; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }")
        self.clear_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.refresh_log()
    def refresh_log(self):
        if hasattr(self.parent, 'log_messages'):
            self.log_text.setPlainText('\n'.join(self.parent.log_messages))
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    def clear_log(self):
        if hasattr(self.parent, 'log_messages'):
            self.parent.log_messages.clear()
            self.log_text.clear()
            clear_log_file()
            self.parent.log_message(self.parent.tr('clear_log') + "\n")
    def append_log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    def showEvent(self, event):
        super().showEvent(event)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

class SaveCleanPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.items = []
        self.checkboxes = []
        self.init_ui()
        self.load_items()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr("clean_save"))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: 1px solid #e0e0e0; border-radius: 8px; background: white; }")
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0,0,0,0)
        self.list_layout.setSpacing(1)
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll)
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton(self.parent.tr('select_all'))
        self.select_none_btn = QPushButton(self.parent.tr('select_none'))
        self.delete_btn = QPushButton(self.parent.tr('confirm_delete'))
        for btn in (self.select_all_btn, self.select_none_btn, self.delete_btn):
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            btn.setCursor(Qt.PointingHandCursor)
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_none_btn.clicked.connect(self.select_none)
        self.delete_btn.clicked.connect(self.confirm_delete)
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.select_none_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        style = "QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }"
        self.select_all_btn.setStyleSheet(style)
        self.select_none_btn.setStyleSheet(style)
        self.delete_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #b71c1c; } QPushButton:pressed { background-color: #8b0000; }")
    def load_items(self):
        for i in reversed(range(self.list_layout.count())):
            w = self.list_layout.itemAt(i).widget()
            if w: w.deleteLater()
        self.checkboxes.clear()
        self.items.clear()
        if not os.path.exists(SAVE_PATH):
            self.show_empty_message(self.parent.tr('save_folder_not_exist'))
            return
        for filename in os.listdir(SAVE_PATH):
            full_path = os.path.join(SAVE_PATH, filename)
            if os.path.isfile(full_path) and filename.startswith("MULTIPLAYER_") and filename.endswith(".sav"):
                for diff_en in DIFFICULTY_LIST:
                    if f"_{diff_en}.sav" in filename:
                        diff_cn = DIFFICULTY_MAP[diff_en]
                        try:
                            base = filename[len("MULTIPLAYER_"):-len(".sav")]
                            if base.endswith(f"_{diff_en}"):
                                save_name = base[:-len(f"_{diff_en}")]
                            else:
                                save_name = base
                        except:
                            save_name = filename
                        self.items.append((save_name, full_path, diff_cn))
                        break
        if not self.items:
            self.show_empty_message(self.parent.tr('no_archive_found'))
            return
        font_size = self.parent.font_size
        v_padding = max(4, font_size // 2)
        h_padding = max(6, font_size - 2)
        item_spacing = max(6, font_size // 2)
        font = QApplication.font()
        font_metrics = QFontMetrics(font)
        max_diff_width = max(font_metrics.width(diff) for _, _, diff in self.items) + h_padding * 2
        for name, path, diff in self.items:
            frame = QFrame()
            frame.setStyleSheet("QFrame{margin:0;padding:0;background:transparent;}")
            frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(4, v_padding, 4, v_padding)
            fl.setSpacing(item_spacing)
            fl.setAlignment(Qt.AlignVCenter)
            cb = QCheckBox()
            cb.setCursor(Qt.PointingHandCursor)
            cb.setIconSize(QSize(font_size + 4, font_size + 4))
            cb.setStyleSheet("""
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 1px solid #b0b0b0;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #4caf50;
                    border-color: #4caf50;
                }
                QCheckBox::indicator:checked:hover {
                    background-color: #45a049;
                }
                QCheckBox::indicator:hover {
                    border-color: #4caf50;
                }
            """)
            fl.addWidget(cb)
            dl = QLabel(diff)
            dl.setFixedWidth(max_diff_width)
            dl.setAlignment(Qt.AlignCenter)
            radius = max(8, (font_size + 4) // 2)
            dl.setStyleSheet(f"background:{DIFFICULTY_COLORS.get(diff,'#3498db')}; color:white; border-radius:{radius}px; padding:{v_padding//2}px {h_padding}px; font-weight:bold;")
            fl.addWidget(dl)
            nl = QLabel(name)
            nl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            nl.setToolTip(f"路径：{path}")
            fl.addWidget(nl)
            fl.addStretch()
            self.checkboxes.append((cb, path, name, diff))
            self.list_layout.addWidget(frame)
        self.list_layout.addStretch()
    def show_empty_message(self, msg):
        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color:#7f8c8d; padding:20px;")
        self.list_layout.addWidget(label)
    def select_all(self):
        for cb, _, _, _ in self.checkboxes:
            cb.setChecked(True)
    def select_none(self):
        for cb, _, _, _ in self.checkboxes:
            cb.setChecked(False)
    def confirm_delete(self):
        selected = [(path, name, diff) for cb, path, name, diff in self.checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.information(self, self.parent.tr('warning_title'), "未选择任何存档。")
            return
        success = []
        errors = []
        for path, name, diff in selected:
            try:
                os.remove(path)
                success.append((name, diff))
                self.parent.log_message(self.parent.tr('clean_archive_log').format(name, diff))
            except Exception as e:
                errors.append((name, str(e)))
        if success:
            QMessageBox.information(self, self.parent.tr('warning_title'), self.parent.tr('delete_confirm_msg').format(len(success)))
        if errors:
            for name, err in errors:
                self.parent.log_message(f"❌ {self.parent.tr('delete_fail')}{name} - {err}")
        if hasattr(self.parent, 'reload_current_panel'):
            self.parent.reload_current_panel()

class CrashCleanPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.items = []
        self.checkboxes = []
        self.init_ui()
        self.load_items()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr("clean_crash"))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: 1px solid #e0e0e0; border-radius: 8px; background: white; }")
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0,0,0,0)
        self.list_layout.setSpacing(1)
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll)
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton(self.parent.tr('select_all'))
        self.select_none_btn = QPushButton(self.parent.tr('select_none'))
        self.open_btn = QPushButton(self.parent.tr('open_selected'))
        self.delete_btn = QPushButton(self.parent.tr('confirm_delete'))
        for btn in (self.select_all_btn, self.select_none_btn, self.open_btn, self.delete_btn):
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            btn.setCursor(Qt.PointingHandCursor)
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_none_btn.clicked.connect(self.select_none)
        self.open_btn.clicked.connect(self.open_selected)
        self.delete_btn.clicked.connect(self.confirm_delete)
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.select_none_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        style = "QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }"
        self.select_all_btn.setStyleSheet(style)
        self.select_none_btn.setStyleSheet(style)
        self.open_btn.setStyleSheet(style)
        self.delete_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #b71c1c; } QPushButton:pressed { background-color: #8b0000; }")
    def load_items(self):
        for i in reversed(range(self.list_layout.count())):
            w = self.list_layout.itemAt(i).widget()
            if w: w.deleteLater()
        self.checkboxes.clear()
        self.items.clear()
        if not os.path.exists(CRASH_PATH):
            self.show_empty_message(self.parent.tr('crash_folder_not_exist'))
            return
        for folder in os.listdir(CRASH_PATH):
            full_path = os.path.join(CRASH_PATH, folder)
            if os.path.isdir(full_path):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                file_count = len([f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))])
                display = f"{folder}  ({file_count} 个文件, {mtime})"
                self.items.append((display, full_path, folder))
        if not self.items:
            self.show_empty_message(self.parent.tr('no_crash_found'))
            return
        font_size = self.parent.font_size
        v_padding = max(4, font_size // 2)
        item_spacing = max(6, font_size // 2)
        for display, path, name in self.items:
            frame = QFrame()
            frame.setStyleSheet("QFrame{margin:0;padding:0;background:transparent;}")
            frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(4, v_padding, 4, v_padding)
            fl.setSpacing(item_spacing)
            fl.setAlignment(Qt.AlignVCenter)
            cb = QCheckBox()
            cb.setCursor(Qt.PointingHandCursor)
            cb.setIconSize(QSize(font_size + 4, font_size + 4))
            cb.setStyleSheet("""
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 1px solid #b0b0b0;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #4caf50;
                    border-color: #4caf50;
                }
                QCheckBox::indicator:hover {
                    border-color: #4caf50;
                }
            """)
            fl.addWidget(cb)
            il = QLabel(display)
            il.setToolTip(f"路径：{path}")
            il.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            fl.addWidget(il)
            fl.addStretch()
            self.checkboxes.append((cb, path, name))
            self.list_layout.addWidget(frame)
        self.list_layout.addStretch()
    def show_empty_message(self, msg):
        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color:#7f8c8d; padding:20px;")
        self.list_layout.addWidget(label)
    def select_all(self):
        for cb, _, _ in self.checkboxes:
            cb.setChecked(True)
    def select_none(self):
        for cb, _, _ in self.checkboxes:
            cb.setChecked(False)
    def open_selected(self):
        selected = [path for cb, path, _ in self.checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.information(self, self.parent.tr('warning_title'), "请先选择要打开的文件夹。")
            return
        for path in selected:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    def confirm_delete(self):
        selected = [(path, name) for cb, path, name in self.checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.information(self, self.parent.tr('warning_title'), "未选择任何崩溃日志。")
            return
        success = []
        errors = []
        for path, name in selected:
            try:
                shutil.rmtree(path)
                success.append(name)
                self.parent.log_message(self.parent.tr('clean_crash_log').format(name))
            except Exception as e:
                errors.append((name, str(e)))
        if success:
            QMessageBox.information(self, self.parent.tr('warning_title'), self.parent.tr('delete_confirm_msg').format(len(success)))
        if errors:
            for name, err in errors:
                self.parent.log_message(f"❌ {self.parent.tr('delete_fail')}{name} - {err}")
        if hasattr(self.parent, 'reload_current_panel'):
            self.parent.reload_current_panel()

class PathInfoPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr('path_info'))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.save_path_label = QLabel(f"{self.parent.tr('save_path_label')} {SAVE_PATH}")
        self.save_path_label.setWordWrap(True)
        layout.addWidget(self.save_path_label)
        self.crash_path_label = QLabel(f"{self.parent.tr('crash_path_label')} {CRASH_PATH}")
        self.crash_path_label.setWordWrap(True)
        layout.addWidget(self.crash_path_label)
        btn_layout = QHBoxLayout()
        self.copy_save_btn = QPushButton(self.parent.tr('copy_save_path'))
        self.copy_save_btn.setCursor(Qt.PointingHandCursor)
        self.copy_save_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.copy_save_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }")
        self.copy_save_btn.clicked.connect(lambda: self.copy_path(SAVE_PATH))
        btn_layout.addWidget(self.copy_save_btn)
        self.copy_crash_btn = QPushButton(self.parent.tr('copy_crash_path'))
        self.copy_crash_btn.setCursor(Qt.PointingHandCursor)
        self.copy_crash_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.copy_crash_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }")
        self.copy_crash_btn.clicked.connect(lambda: self.copy_path(CRASH_PATH))
        btn_layout.addWidget(self.copy_crash_btn)
        self.copy_all_btn = QPushButton(self.parent.tr('copy_all_paths'))
        self.copy_all_btn.setCursor(Qt.PointingHandCursor)
        self.copy_all_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.copy_all_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #0b7dda; } QPushButton:pressed { background-color: #0a5e9e; }")
        self.copy_all_btn.clicked.connect(self.copy_all_paths)
        btn_layout.addWidget(self.copy_all_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()
    def copy_path(self, path):
        QApplication.clipboard().setText(path)
        self.parent.log_message(f"📋 已复制路径：{path}")
        QMessageBox.information(self, self.parent.tr('warning_title'), f"路径已复制：{path}")
    def copy_all_paths(self):
        text = f"{SAVE_PATH}\n{CRASH_PATH}"
        QApplication.clipboard().setText(text)
        self.parent.log_message(self.parent.tr('copy_path_log'))
        QMessageBox.information(self, self.parent.tr('warning_title'), "所有路径已复制到剪贴板。")

class UpdatePanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr('check_update'))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,0)
        layout.addWidget(self.progress_bar)
        self.result_label = QLabel(self.parent.tr('checking_update'))
        layout.addWidget(self.result_label)
        self.hint_label = QLabel(self.parent.tr("stay_on_page_hint"))
        self.hint_label.setStyleSheet("color: #e67e22; font-size: 12px; margin-top: 8px;")
        layout.addWidget(self.hint_label)
        self.retry_btn = None
        self.update_thread = None
        self.start_check()
        layout.addStretch()
    def start_check(self):
        if self.update_thread and self.update_thread.isRunning():
            return
        self.progress_bar.setRange(0,0)
        self.result_label.setText(self.parent.tr('checking_update'))
        if self.retry_btn:
            self.retry_btn.deleteLater()
            self.retry_btn = None
        self.update_thread = UpdateCheckThread()
        self.update_thread.finished.connect(self.on_update_result)
        self.update_thread.start()
    def on_update_result(self, data, error):
        self.progress_bar.setRange(0,1)
        self.progress_bar.setValue(1)
        if error:
            self.result_label.setText(self.parent.tr('update_error').format(error))
            if not self.retry_btn:
                self.retry_btn = QPushButton(self.parent.tr('retry_check'))
                self.retry_btn.setCursor(Qt.PointingHandCursor)
                self.retry_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                self.retry_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }")
                self.retry_btn.clicked.connect(self.start_check)
                layout = self.layout()
                layout.insertWidget(layout.indexOf(self.result_label)+1, self.retry_btn)
            return
        latest = data.get("latest_version","")
        download_url = data.get("download_url","")
        notes = data.get("release_notes","")
        if latest and is_newer(latest, VERSION):
            self.result_label.setText(self.parent.tr('update_available').format(latest))
            download_btn = QPushButton(self.parent.tr('download_now'))
            download_btn.setCursor(Qt.PointingHandCursor)
            download_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            download_btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #45a049; } QPushButton:pressed { background-color: #3d8b40; }")
            download_btn.clicked.connect(lambda: webbrowser.open(download_url))
            self.layout().addWidget(download_btn)
            if notes:
                notes_clean = notes.replace('；',';').replace(';','|')
                items = [item.strip() for item in notes_clean.split('|') if item.strip()]
                if items:
                    html_lines = '<br>• '.join(items)
                    display_html = f'<div style="line-height:1.6;">{self.parent.tr("update_notes")}<br>• {html_lines}</div>'
                else:
                    display_html = f'<div style="line-height:1.6;">{self.parent.tr("update_notes")}<br>{notes}</div>'
            else:
                display_html = f'<div style="line-height:1.6;">{self.parent.tr("update_notes")}<br>无更新说明</div>'
            notes_label = QLabel()
            notes_label.setTextFormat(Qt.RichText)
            notes_label.setText(display_html)
            notes_label.setWordWrap(True)
            notes_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            notes_label.setStyleSheet("QLabel { background-color: #f9f9f9; padding: 10px; border-radius: 5px; font-size: 10pt; }")
            self.layout().addWidget(notes_label)
        else:
            self.result_label.setText(self.parent.tr('already_latest'))

class WebsitePanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr('website'))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.url_label = QLabel(WEBSITE_URL)
        self.url_label.setWordWrap(True)
        layout.addWidget(self.url_label)
        self.open_btn = QPushButton(self.parent.tr('website'))
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #0b7dda; } QPushButton:pressed { background-color: #0a5e9e; }")
        self.open_btn.clicked.connect(lambda: webbrowser.open(WEBSITE_URL))
        layout.addWidget(self.open_btn)
        layout.addStretch()

class AboutPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr('about'))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.version_label = QLabel(self.parent.tr('version_label'))
        self.version_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.version_label)
        self.copyright_label = QLabel(self.parent.tr('about_copyright'))
        layout.addWidget(self.copyright_label)
        self.desc_label = QLabel(self.parent.tr('about_desc'))
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        btn_layout = QHBoxLayout()
        self.open_config_btn = QPushButton(self.parent.tr('open_config_dir'))
        self.open_config_btn.setCursor(Qt.PointingHandCursor)
        self.open_config_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_config_btn.setMaximumWidth(150)
        self.open_config_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border-radius: 6px; padding: 6px 12px; } QPushButton:hover { background-color: #e0e0e0; } QPushButton:pressed { background-color: #d0d0d0; }")
        self.open_config_btn.clicked.connect(self.open_config_dir)
        btn_layout.addWidget(self.open_config_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()
    def open_config_dir(self):
        config_dir = get_config_dir()
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, self.parent.tr('warning_title'), f"无法创建配置目录：{str(e)}")
                return
        reply = QMessageBox.warning(self, self.parent.tr('warning_title'), self.parent.tr('config_dir_warning'), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.startfile(config_dir)
                self.parent.log_message("📂 已打开软件配置目录")
            except Exception as e:
                QMessageBox.critical(self, self.parent.tr('warning_title'), f"无法打开配置目录：{str(e)}")

class ThanksPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr("thanks"))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.thanks_text = QTextEdit()
        self.thanks_text.setReadOnly(True)
        self.thanks_text.setPlainText(self.parent.tr("thanks_message"))
        self.thanks_text.setStyleSheet("QTextEdit { background-color: #fef9e7; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 12px; }")
        layout.addWidget(self.thanks_text)
        layout.addStretch()

class ModsFetchThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, api, search=""):
        super().__init__()
        self.api = api
        self.search = search
    def run(self):
        result = self.api.get_mods(search=self.search)
        self.finished.emit(result)

class DownloadModPanel(ContentPanel):
    _welcome_shown_global = False
    _last_notice_content = None
    def __init__(self, parent):
        super().__init__(parent)
        self.api = ETBApi("https://etbtoolmod.xn--online-o20ki81q.top")
        self.mods_data = []
        self.current_user = None
        self.fetch_thread = None
        self.init_ui()
        self.show_welcome_message()
        if self.api.auto_login():
            self.current_user = self.api.username
            self.auth_btn.setText("登出")
            self.user_label.setText(f"已登录：{self.current_user}")
        self.load_mods()
    def show_welcome_message(self):
        if not DownloadModPanel._welcome_shown_global:
            DownloadModPanel._welcome_shown_global = True
            QMessageBox.information(self, "欢迎使用", "本服务由逃离后室模组库提供，接入第三方（本软件）")
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        top_layout = QHBoxLayout()
        self.title = QLabel("模组下载")
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        top_layout.addWidget(self.title)
        top_layout.addStretch()
        self.official_btn = QPushButton("🌐 打开浏览器使用官方版")
        self.official_btn.setCursor(Qt.PointingHandCursor)
        self.official_btn.setStyleSheet("QPushButton { background-color: #ff9800; color: white; border-radius: 4px; padding: 4px 12px; }")
        self.official_btn.clicked.connect(lambda: webbrowser.open("https://etbtoolmod.xn--online-o20ki81q.top/"))
        top_layout.addWidget(self.official_btn)
        self.auth_btn = QPushButton("登录")
        self.auth_btn.setCursor(Qt.PointingHandCursor)
        self.auth_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; border-radius: 4px; padding: 4px 12px; }")
        self.auth_btn.clicked.connect(self.show_auth_dialog)
        top_layout.addWidget(self.auth_btn)
        self.user_label = QLabel("")
        self.user_label.setStyleSheet("color: #555;")
        top_layout.addWidget(self.user_label)
        layout.addLayout(top_layout)
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索模组...")
        self.search_edit.setStyleSheet("QLineEdit { padding: 4px; border: 1px solid #d1d8e0; border-radius: 4px; }")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; border-radius: 4px; padding: 4px 12px; }")
        self.refresh_btn.clicked.connect(lambda: self.parent.set_active_button(self.parent.download_mod_btn, DownloadModPanel))
        search_layout.addWidget(self.refresh_btn)
        layout.addLayout(search_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "模组名称", "版本", "描述", "操作"])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 80)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        self.status_label = QLabel("加载中...")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
    def stop_current_thread(self):
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.quit()
            self.fetch_thread.wait(5000)
            if self.fetch_thread.isRunning():
                self.fetch_thread.terminate()
            self.fetch_thread.deleteLater()
            self.fetch_thread = None
    def load_mods(self, search=""):
        self.stop_current_thread()
        self.status_label.setText("正在加载模组列表...")
        QApplication.processEvents()
        self.fetch_thread = ModsFetchThread(self.api, search)
        self.fetch_thread.finished.connect(self.on_mods_fetched)
        self.fetch_thread.start()
    def on_mods_fetched(self, result):
        if self.sender() != self.fetch_thread:
            return
        if self.fetch_thread:
            self.fetch_thread.deleteLater()
            self.fetch_thread = None
        if result.get("success"):
            raw_mods = result.get("mods", [])
            if not isinstance(raw_mods, list):
                raw_mods = list(raw_mods) if raw_mods else []
            valid_mods = []
            for mod in raw_mods:
                mod_id = mod.get('id')
                mod_name = mod.get('name', '')
                if mod_id and str(mod_id).strip() != '0' and mod_name and mod_name.strip():
                    valid_mods.append(mod)
                else:
                    self.parent.log_message(f"🚫 过滤无效模组：ID={mod_id}, Name='{mod_name}'")
            self.mods_data = valid_mods
            self.parent.log_message(f"✅ 模组列表：原始 {len(raw_mods)} 个，有效 {len(self.mods_data)} 个")
            self.populate_table()
            self.status_label.setText(f"共 {len(self.mods_data)} 个模组")
            notice = self.api.get_notice()
            if notice.get("has_notice"):
                content = notice.get("fullscreen_content") or notice.get("banner_content", "")
                if content and content != DownloadModPanel._last_notice_content:
                    DownloadModPanel._last_notice_content = content
                    QMessageBox.information(self, "通知", content)
        else:
            self.status_label.setText(f"加载失败：{result.get('message', '未知错误')}")
            self.table.setRowCount(0)
    def on_search(self, text):
        if text.strip() == "":
            self.parent.set_active_button(self.parent.download_mod_btn, DownloadModPanel)
        else:
            self.load_mods(search=text)
    def populate_table(self):
        self.table.setRowCount(0)
        self.table.clearContents()
        valid_data = [mod for mod in self.mods_data if mod.get('id') and mod.get('name', '').strip()]
        if not valid_data:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 5)
            self.table.setItem(0, 0, QTableWidgetItem("暂无模组"))
            return
        sorted_mods = sorted(valid_data, key=lambda x: x.get('id', 0))
        self.table.setRowCount(len(sorted_mods))
        for row, mod in enumerate(sorted_mods):
            id_val = mod.get('id', 0)
            id_item = QTableWidgetItem(str(id_val))
            id_item.setData(Qt.UserRole, id_val)
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(mod.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(mod.get("version", "")))
            desc = mod.get("description", "")[:30] + ("..." if len(mod.get("description", "")) > 30 else "")
            self.table.setItem(row, 3, QTableWidgetItem(desc))
            download_btn = QPushButton("下载")
            download_btn.setCursor(Qt.PointingHandCursor)
            download_btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; border-radius: 4px; padding: 2px 8px; }")
            download_btn.clicked.connect(lambda checked, mod_id=id_val: self.download_mod(mod_id))
            self.table.setCellWidget(row, 4, download_btn)
        self.table.sortItems(0, Qt.AscendingOrder)
    def download_mod(self, mod_id):
        if not self.api.is_logged_in():
            QMessageBox.warning(self, "提示", "请先登录后再下载模组。")
            self.show_auth_dialog()
            return
        save_dir = QFileDialog.getExistingDirectory(self, "选择保存文件夹", os.path.expanduser("~"))
        if not save_dir:
            return
        self.status_label.setText("正在下载...")
        QApplication.processEvents()
        result = self.api.download(mod_id, save_dir=save_dir)
        if result["success"]:
            QMessageBox.information(self, "下载完成", f"模组已保存至：{result['file_path']}")
            self.status_label.setText("下载完成")
        else:
            QMessageBox.critical(self, "下载失败", result.get("message", "未知错误"))
            self.status_label.setText("下载失败")
    def on_cell_double_clicked(self, row, column):
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        mod_id = id_item.data(Qt.UserRole)
        if not mod_id:
            return
        result = self.api.get_mod(mod_id)
        if result.get("success"):
            mod = result["mod"]
            detail = f"名称：{mod.get('name', '')}\n"
            detail += f"版本：{mod.get('version', '')}\n"
            detail += f"描述：{mod.get('description', '')}\n"
            detail += f"使用说明：{mod.get('usage_guide', '无')}\n"
            QMessageBox.information(self, f"模组详情 - {mod.get('name', '')}", detail)
        else:
            QMessageBox.critical(self, "错误", "获取详情失败：" + result.get("message", "未知错误"))
    def show_auth_dialog(self):
        if self.api.is_logged_in():
            reply = QMessageBox.question(self, "确认", f"当前用户：{self.current_user}\n是否登出？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.api.logout()
                self.current_user = None
                self.auth_btn.setText("登录")
                self.user_label.setText("")
                QMessageBox.information(self, "已登出", "您已成功登出")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("登录 / 注册")
        dialog.setModal(True)
        dialog.resize(300, 300)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("注册时必填")
        if self.api.username:
            self.username_edit.setText(self.api.username)
        form.addRow("用户名:", self.username_edit)
        form.addRow("密码:", self.password_edit)
        form.addRow("邮箱:", self.email_edit)
        layout.addLayout(form)
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("登录")
        register_btn = QPushButton("注册")
        help_btn = QPushButton("?")
        cancel_btn = QPushButton("取消")
        for btn in (login_btn, register_btn, help_btn, cancel_btn):
            btn.setCursor(Qt.PointingHandCursor)
        help_btn.setToolTip("点击查看帮助")
        help_btn.clicked.connect(lambda: QMessageBox.information(dialog, "帮助", "本服务由模组库提供，您在本软件注册的帐户可以在模组库直接登录并开始使用。"))
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        def on_login():
            username = self.username_edit.text().strip()
            password = self.password_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(dialog, "提示", "用户名和密码不能为空")
                return
            result = self.api.login(username, password)
            if result.get("success"):
                self.current_user = username
                self.auth_btn.setText("登出")
                self.user_label.setText(f"已登录：{username}")
                dialog.accept()
                QMessageBox.information(self, "登录成功", f"欢迎回来，{username}")
            else:
                QMessageBox.critical(dialog, "登录失败", result.get("message", "未知错误"))
        def on_register():
            username = self.username_edit.text().strip()
            password = self.password_edit.text().strip()
            email = self.email_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(dialog, "提示", "用户名和密码不能为空")
                return
            if not email:
                QMessageBox.warning(dialog, "提示", "邮箱不能为空，请输入邮箱地址")
                return
            result = self.api.register(username, password, email)
            if result.get("success"):
                QMessageBox.information(dialog, "注册成功", f"用户 {username} 注册成功，请登录")
                QMessageBox.information(self, "账户接入", "您的帐户已接入逃离后室模组库官方，可以在官方模组库登录相同的账号")
                login_result = self.api.login(username, password)
                if login_result.get("success"):
                    self.current_user = username
                    self.auth_btn.setText("登出")
                    self.user_label.setText(f"已登录：{username}")
                    dialog.accept()
                    QMessageBox.information(self, "登录成功", f"欢迎回来，{username}")
                else:
                    dialog.reject()
            else:
                QMessageBox.critical(dialog, "注册失败", result.get("message", "未知错误"))
        login_btn.clicked.connect(on_login)
        register_btn.clicked.connect(on_register)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()

class UE4ManagementPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.ue4_root = None
        self.current_path = None
        self.all_items = []
        self.filtered_items = []
        self.installed_flag = False
        self.recorded_files = []
        self.config_key = "ue4_management"
        self.init_ui()
        self.detect_ue4_path()
        if self.ue4_root:
            self.current_path = self.ue4_root
            self.load_current_directory()
            self.check_installation_status()
        else:
            self.path_label.setText("⚠️ 未找到游戏 UE4 目录，请确保游戏已安装")
            self.status_label.setText("检测失败，请确保《逃离后室》已正确安装")
    def detect_ue4_path(self):
        game_path = get_game_install_path()
        if game_path:
            ue4_path = os.path.join(game_path, "EscapeTheBackrooms", "Binaries", "Win64")
            if os.path.exists(ue4_path):
                self.ue4_root = ue4_path
                return
        self.ue4_root = None
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 12px;")
        title_layout = QHBoxLayout(title_frame)
        title_label = QLabel("🎮 UE4 管理")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        self.path_label = QLabel()
        self.path_label.setStyleSheet("background-color: #f5f7fa; padding: 6px 12px; border-radius: 6px; color: #555;")
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.path_label.setCursor(Qt.PointingHandCursor)
        self.path_label.mousePressEvent = self.on_path_label_clicked
        title_layout.addWidget(self.path_label, stretch=1)
        layout.addWidget(title_frame)
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 8px;")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        self.back_btn = QPushButton("← 返回上级")
        self.back_btn.setStyleSheet("QPushButton { background-color: #e3f2fd; color: #1976d2; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #bbdef5; } QPushButton:pressed { background-color: #90caf9; }")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.back_btn.clicked.connect(self.go_up)
        self.back_btn.setEnabled(False)
        toolbar_layout.addWidget(self.back_btn)
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #0b7dda; } QPushButton:pressed { background-color: #0a5e9e; }")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.refresh_btn.clicked.connect(self.load_current_directory)
        toolbar_layout.addWidget(self.refresh_btn)
        self.install_btn = QPushButton("📥 安装 UE4 文件")
        self.install_btn.setStyleSheet("QPushButton { background-color: #9c27b0; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #8e24aa; } QPushButton:pressed { background-color: #6a1b9a; }")
        self.install_btn.setCursor(Qt.PointingHandCursor)
        self.install_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.install_btn.clicked.connect(self.show_install_menu)
        toolbar_layout.addWidget(self.install_btn)
        self.uninstall_btn = QPushButton("🗑️ 卸载 UE4")
        self.uninstall_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #c62828; } QPushButton:pressed { background-color: #b71c1c; }")
        self.uninstall_btn.setCursor(Qt.PointingHandCursor)
        self.uninstall_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.uninstall_btn.clicked.connect(self.uninstall_ue4)
        toolbar_layout.addWidget(self.uninstall_btn)
        self.open_dir_btn = QPushButton("📂 打开文件夹")
        self.open_dir_btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #45a049; } QPushButton:pressed { background-color: #3d8b40; }")
        self.open_dir_btn.setCursor(Qt.PointingHandCursor)
        self.open_dir_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_dir_btn.clicked.connect(self.open_current_folder)
        toolbar_layout.addWidget(self.open_dir_btn)
        toolbar_layout.addStretch()
        layout.addWidget(toolbar_frame)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; margin-top: 5px;")
        layout.addWidget(self.status_label)
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
        table_layout = QVBoxLayout(table_frame)
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["名称", "大小", "操作"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.setAcceptDrops(True)
        self.file_table.dragEnterEvent = self.drag_enter_event
        self.file_table.dropEvent = self.drop_event
        self.file_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        table_layout.addWidget(self.file_table)
        layout.addWidget(table_frame)
        self.install_status_label = QLabel("")
        self.install_status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        layout.addWidget(self.install_status_label)
    def show_install_menu(self):
        menu = QMenu(self)
        action_files = menu.addAction("安装文件（多选）")
        action_folder = menu.addAction("安装文件夹（递归）")
        action = menu.exec_(self.install_btn.mapToGlobal(QPoint(0, self.install_btn.height())))
        if action == action_files:
            self.install_files()
        elif action == action_folder:
            self.import_folder()
    def load_current_directory(self):
        if not self.ue4_root or not os.path.exists(self.ue4_root):
            self.file_table.setRowCount(0)
            self.path_label.setText("UE4 根目录不存在")
            return
        if self.current_path is None:
            self.current_path = self.ue4_root
        if not os.path.exists(self.current_path):
            self.path_label.setText(f"路径不存在: {self.current_path}")
            self.file_table.setRowCount(0)
            return
        if self.current_path.startswith(self.ue4_root):
            rel = os.path.relpath(self.current_path, self.ue4_root)
            if rel == '.':
                display = self.ue4_root + " (根目录)"
            else:
                display = f"{self.ue4_root} → {rel}"
        else:
            display = self.current_path
        self.path_label.setText(f"📂 {display}")
        self.all_items.clear()
        try:
            items = os.listdir(self.current_path)
        except Exception as e:
            self.status_label.setText(f"无法读取目录：{str(e)}")
            return
        dirs = []
        files = []
        for name in items:
            full = os.path.join(self.current_path, name)
            if os.path.isdir(full):
                dirs.append((name, full, True))
            else:
                files.append((name, full, False))
        dirs.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        for name, full, is_dir in dirs:
            self.all_items.append((name, full, is_dir))
        for name, full, is_dir in files:
            self.all_items.append((name, full, is_dir))
        self.filter_items("")
        self.back_btn.setEnabled(self.current_path != self.ue4_root)
        self.check_installation_status()
    def filter_items(self, text):
        self.filtered_items = self.all_items[:]
        self.refresh_table_display()
    def refresh_table_display(self):
        self.file_table.setRowCount(0)
        row = 0
        for name, full_path, is_dir in self.filtered_items:
            self._add_table_row(row, name, full_path, is_dir)
            row += 1
        self.status_label.setText(f"共 {len(self.filtered_items)} 个项目")
    def _add_table_row(self, row, name, full_path, is_dir):
        self.file_table.insertRow(row)
        icon = "📁" if is_dir else "📄"
        name_item = QTableWidgetItem(f"{icon} {name}")
        name_item.setData(Qt.UserRole, (full_path, is_dir))
        if is_dir:
            name_item.setForeground(QBrush(QColor("#1976d2")))
        self.file_table.setItem(row, 0, name_item)
        if is_dir:
            size_item = QTableWidgetItem("文件夹")
        else:
            size = os.path.getsize(full_path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            size_item = QTableWidgetItem(size_str)
        size_item.setTextAlignment(Qt.AlignCenter)
        self.file_table.setItem(row, 1, size_item)
        op_widget = QWidget()
        op_layout = QHBoxLayout(op_widget)
        op_layout.setContentsMargins(0,0,0,0)
        op_layout.setSpacing(4)
        if is_dir:
            open_btn = QPushButton("打开")
            open_btn.setCursor(Qt.PointingHandCursor)
            open_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            open_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; border-radius: 3px; padding: 2px 6px; font-size: 11px; } QPushButton:hover { background-color: #bdbdbd; } QPushButton:pressed { background-color: #9e9e9e; }")
            open_btn.clicked.connect(lambda checked, p=full_path: self.enter_directory(p))
            op_layout.addWidget(open_btn)
        else:
            delete_btn = QPushButton("删除")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            delete_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 3px; padding: 2px 6px; font-size: 11px; } QPushButton:hover { background-color: #b71c1c; } QPushButton:pressed { background-color: #8b0000; }")
            delete_btn.clicked.connect(lambda checked, p=full_path: self.delete_file(p))
            op_layout.addWidget(delete_btn)
        op_layout.addStretch()
        self.file_table.setCellWidget(row, 2, op_widget)
    def enter_directory(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.load_current_directory()
    def go_up(self):
        if self.current_path == self.ue4_root:
            QMessageBox.information(self, "提示", "已经是根目录")
            return
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.load_current_directory()
    def delete_file(self, path):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除 {os.path.basename(path)} 吗？", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(path)
            self.parent.log_message(f"❌ 删除UE4文件：{os.path.basename(path)}")
            self.load_current_directory()
        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))
    def install_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择要安装的文件", "", "所有文件 (*)")
        if not files:
            return
        success = 0
        for f in files:
            try:
                dest = os.path.join(self.current_path, os.path.basename(f))
                if os.path.exists(dest):
                    reply = QMessageBox.question(self, "文件已存在", f"{os.path.basename(f)} 已存在，是否覆盖？", QMessageBox.Yes | QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        continue
                shutil.copy2(f, dest)
                success += 1
                self.parent.log_message(f"📥 安装UE4文件：{os.path.basename(f)}")
            except Exception as e:
                QMessageBox.warning(self, "安装失败", str(e))
        if success:
            self.load_current_directory()
            self.record_installation()
            QMessageBox.information(self, "完成", f"成功安装 {success} 个文件")
    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择要导入的文件夹", os.path.expanduser("~"))
        if not folder:
            return
        success = 0
        for root, dirs, files in os.walk(folder):
            for file in files:
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, folder)
                dest = os.path.join(self.current_path, rel_path)
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if os.path.exists(dest):
                        reply = QMessageBox.question(self, "文件已存在", f"{rel_path} 已存在，是否覆盖？", QMessageBox.Yes | QMessageBox.No)
                        if reply != QMessageBox.Yes:
                            continue
                    shutil.copy2(src, dest)
                    success += 1
                    self.parent.log_message(f"📥 导入UE4文件夹：{rel_path}")
                except Exception as e:
                    QMessageBox.warning(self, "导入失败", f"{rel_path}: {str(e)}")
        if success:
            self.load_current_directory()
            self.record_installation()
            QMessageBox.information(self, "完成", f"成功导入 {success} 个文件")
    def uninstall_ue4(self):
        if not self.ue4_root or not os.path.exists(self.ue4_root):
            QMessageBox.warning(self, "提示", "未找到 UE4 目录")
            return
        reply = QMessageBox.question(self, "确认卸载",
                                     "此操作会删除 UE4 文件夹内的所有文件，删除后请前往 Steam 库-右键游戏-属性-验证游戏文件完整性恢复必要的 UE4 文件。\n\n是否继续？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            for item in os.listdir(self.ue4_root):
                item_path = os.path.join(self.ue4_root, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            self.parent.log_message("🗑️ UE4 目录已清空")
            self.load_current_directory()
            self.installed_flag = False
            self.recorded_files = []
            self.save_ue4_status()
            self.install_status_label.setText("")
            QMessageBox.information(self, "完成", "UE4 目录已清空，请前往 Steam 验证游戏完整性。")
            try:
                webbrowser.open("steam://open/games")
            except:
                pass
        except Exception as e:
            QMessageBox.critical(self, "错误", f"卸载失败：{str(e)}")
    def open_current_folder(self):
        if self.current_path and os.path.exists(self.current_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_path))
        else:
            QMessageBox.warning(self, "提示", "当前路径无效")
    def on_path_label_clicked(self, event):
        if not self.ue4_root:
            return
        new_root = QFileDialog.getExistingDirectory(self, "选择 UE4 根目录", self.ue4_root)
        if new_root and os.path.exists(new_root):
            self.ue4_root = new_root
            self.current_path = self.ue4_root
            self.load_current_directory()
    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def drop_event(self, event):
        urls = event.mimeData().urls()
        count = 0
        for url in urls:
            src = url.toLocalFile()
            if os.path.isfile(src):
                dest = os.path.join(self.current_path, os.path.basename(src))
                if os.path.exists(dest):
                    reply = QMessageBox.question(self, "文件已存在", f"{os.path.basename(src)} 已存在，是否覆盖？", QMessageBox.Yes | QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        continue
                try:
                    shutil.copy2(src, dest)
                    count += 1
                    self.parent.log_message(f"📥 拖拽安装UE4文件：{os.path.basename(src)}")
                except Exception as e:
                    QMessageBox.warning(self, "安装失败", str(e))
        if count:
            self.load_current_directory()
            self.record_installation()
            QMessageBox.information(self, "完成", f"成功安装 {count} 个文件")
    def check_installation_status(self):
        config = load_config()
        ue4_config = config.get(self.config_key, {})
        self.installed_flag = ue4_config.get("installed", False)
        self.recorded_files = ue4_config.get("files", [])
        current_files = []
        if self.current_path and os.path.exists(self.current_path):
            current_files = [f for f in os.listdir(self.current_path) if os.path.isfile(os.path.join(self.current_path, f))]
        if self.installed_flag and current_files:
            missing = [f for f in self.recorded_files if f not in current_files]
            if missing:
                self.installed_flag = False
                self.recorded_files = []
                self.save_ue4_status()
                self.install_status_label.setText("")
            else:
                self.install_status_label.setText("✅ 用户已上传过 UE4 文件")
        else:
            self.install_status_label.setText("")
    def save_ue4_status(self):
        config = load_config()
        ue4_config = config.get(self.config_key, {})
        ue4_config["installed"] = self.installed_flag
        ue4_config["files"] = self.recorded_files
        config[self.config_key] = ue4_config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    def record_installation(self):
        if self.current_path and os.path.exists(self.current_path):
            self.recorded_files = [f for f in os.listdir(self.current_path) if os.path.isfile(os.path.join(self.current_path, f))]
        else:
            self.recorded_files = []
        self.installed_flag = True
        self.save_ue4_status()
        self.install_status_label.setText("✅ 用户已上传过 UE4 文件")
    def on_cell_double_clicked(self, row, column):
        item = self.file_table.item(row, 0)
        if item:
            full_path, is_dir = item.data(Qt.UserRole)
            if is_dir:
                self.enter_directory(full_path)

class UninstallPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        self.title = QLabel(self.parent.tr("uninstall"))
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title)
        self.check_game = QCheckBox(self.parent.tr("uninstall_game"))
        self.check_game.setCursor(Qt.PointingHandCursor)
        self.check_game.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #b0b0b0;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4caf50;
                border-color: #4caf50;
            }
            QCheckBox::indicator:hover {
                border-color: #4caf50;
            }
        """)
        layout.addWidget(self.check_game)
        layout.addSpacing(20)
        self.uninstall_btn = QPushButton(self.parent.tr("uninstall_start"))
        self.uninstall_btn.setCursor(Qt.PointingHandCursor)
        self.uninstall_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.uninstall_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #b71c1c; } QPushButton:pressed { background-color: #8b0000; }")
        self.uninstall_btn.clicked.connect(self.start_uninstall)
        layout.addWidget(self.uninstall_btn)
        layout.addStretch()
    def start_uninstall(self):
        if not self.check_game.isChecked():
            QMessageBox.warning(self, self.parent.tr('warning_title'), "请选择卸载游戏。")
            return
        if not self.is_game_installed():
            reply = QMessageBox.question(self, self.parent.tr('warning_title'), "游戏似乎已经卸载，是否仍尝试清理残留文件？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        msg_box = QMessageBox(QMessageBox.Warning, "确认卸载", self.parent.tr("uninstall_game_confirm"), QMessageBox.NoButton, self)
        ok_btn = msg_box.addButton(self.parent.tr("uninstall_known"), QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton(QMessageBox.Cancel)
        msg_box.setDefaultButton(ok_btn)
        msg_box.exec_()
        if msg_box.clickedButton() != ok_btn:
            return
        try:
            self.parent.log_message(self.parent.tr("log_uninstall_game_start"))
            self.uninstall_game_func()
            self.parent.log_message(self.parent.tr("log_uninstall_game_success"))
            QMessageBox.information(self, self.parent.tr('warning_title'), self.parent.tr("uninstall_game_success"))
        except Exception as e:
            self.parent.log_message(self.parent.tr("log_uninstall_game_fail").format(str(e)))
            QMessageBox.critical(self, self.parent.tr('warning_title'), self.parent.tr("uninstall_game_fail").format(str(e)))
    def is_game_installed(self) -> bool:
        game_path = get_game_install_path()
        if game_path and os.path.exists(game_path):
            return True
        if os.path.exists(GAME_BASE_PATH):
            return True
        return False
    def uninstall_game_func(self):
        game_path = get_game_install_path()
        if game_path and os.path.exists(game_path):
            self.parent.log_message(f"✅ 找到游戏目录：{game_path}")
            try:
                shutil.rmtree(game_path, ignore_errors=True)
                self.parent.log_message(f"✅ 已删除游戏目录：{game_path}")
            except Exception as e:
                self.parent.log_message(f"❌ 删除游戏目录失败：{str(e)}")
                raise Exception(f"删除游戏目录失败：{str(e)}")
        else:
            self.parent.log_message("未找到游戏安装目录")
        if os.path.exists(GAME_BASE_PATH):
            try:
                shutil.rmtree(GAME_BASE_PATH, ignore_errors=True)
                self.parent.log_message(f"✅ 已删除游戏存档/配置目录：{GAME_BASE_PATH}")
            except Exception as e:
                self.parent.log_message(f"❌ 删除存档目录失败：{str(e)}")
                raise Exception(f"删除存档目录失败：{str(e)}")
        else:
            self.parent.log_message("未找到游戏存档/配置目录，跳过。")

def get_game_install_path() -> str:
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        winreg.CloseKey(key)
        possible_paths = [os.path.join(steam_path, "steamapps", "common", "EscapeTheBackrooms"), os.path.join(steam_path, "steamapps", "common", "Escape The Backrooms")]
        for p in possible_paths:
            if os.path.isdir(p):
                return p
    except:
        pass
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        subkey_count = winreg.QueryInfoKey(key)[0]
        for i in range(subkey_count):
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                if "Escape the Backrooms" in display_name or "EscapeTheBackrooms" in display_name:
                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    if install_location and os.path.isdir(install_location):
                        winreg.CloseKey(subkey)
                        winreg.CloseKey(key)
                        return install_location
            except:
                pass
            winreg.CloseKey(subkey)
        winreg.CloseKey(key)
    except:
        pass
    default_paths = [r"C:\Program Files (x86)\Steam\steamapps\common\EscapeTheBackrooms", r"C:\Program Files\Steam\steamapps\common\EscapeTheBackrooms", r"D:\Steam\steamapps\common\EscapeTheBackrooms", r"E:\Steam\steamapps\common\EscapeTheBackrooms"]
    for p in default_paths:
        if os.path.isdir(p):
            return p
    return None

class ModManagementPanel(ContentPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.mods_root = None
        self.current_path = None
        self.all_items = []
        self.filtered_items = []
        self.mod_name_map = {}
        self.logic_mods_btn = None
        self.logic_mods_frame = None
        self.init_ui()
        self.detect_game_path()
        if self.mods_root:
            self.current_path = self.mods_root
            self.load_current_directory()
        else:
            self.path_label.setText("⚠️ 未找到游戏模组目录，请确保游戏已安装")
            self.status_label.setText("检测失败，请确保《逃离后室》已正确安装")
    def detect_game_path(self):
        def from_registry():
            paths = [r"SOFTWARE\WOW6432Node\Valve\Steam\Apps\1943950", r"SOFTWARE\Valve\Steam\Apps\1943950"]
            for reg_path in paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        installed, _ = winreg.QueryValueEx(key, "Installed")
                        if installed != 1:
                            continue
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        if os.path.exists(install_dir):
                            paks = os.path.join(install_dir, "EscapeTheBackrooms", "Content", "Paks")
                            if os.path.exists(paks):
                                return paks
                except:
                    continue
            return None
        def from_steam_config():
            try:
                import vdf
            except ImportError:
                return None
            steam_path = None
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                    steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            except:
                pass
            if not steam_path:
                return None
            lib_path = os.path.join(steam_path, "config", "libraryfolders.vdf")
            if not os.path.exists(lib_path):
                return None
            try:
                with open(lib_path, "r", encoding="utf-8") as f:
                    data = vdf.load(f)
                for k, v in data.get("libraryfolders", {}).items():
                    if not k.isdigit():
                        continue
                    lp = v.get("path")
                    if not lp or not os.path.exists(lp):
                        continue
                    acf = os.path.join(lp, "steamapps", "appmanifest_1943950.acf")
                    if not os.path.exists(acf):
                        continue
                    with open(acf, "r", encoding="utf-8") as f:
                        acf_data = vdf.load(f)
                    installdir = acf_data.get("AppState", {}).get("installdir")
                    if not installdir:
                        continue
                    game_path = os.path.join(lp, "steamapps", "common", installdir)
                    if os.path.exists(game_path):
                        paks = os.path.join(game_path, "EscapeTheBackrooms", "Content", "Paks")
                        if os.path.exists(paks):
                            return paks
            except:
                pass
            return None
        paks = from_registry()
        if not paks:
            paks = from_steam_config()
        if not paks:
            defaults = [r"C:\Program Files (x86)\Steam\steamapps\common\Escape the Backrooms\EscapeTheBackrooms\Content\Paks",
                        r"D:\SteamLibrary\steamapps\common\Escape the Backrooms\EscapeTheBackrooms\Content\Paks",
                        r"E:\SteamLibrary\steamapps\common\Escape the Backrooms\EscapeTheBackrooms\Content\Paks",
                        r"F:\SteamLibrary\steamapps\common\Escape the Backrooms\EscapeTheBackrooms\Content\Paks"]
            for d in defaults:
                if os.path.exists(d):
                    paks = d
                    break
        self.mods_root = paks
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 12px;")
        title_layout = QHBoxLayout(title_frame)
        title_label = QLabel("🎮 模组管理器")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        self.path_label = QLabel()
        self.path_label.setStyleSheet("background-color: #f5f7fa; padding: 6px 12px; border-radius: 6px; color: #555;")
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.path_label.setCursor(Qt.PointingHandCursor)
        self.path_label.mousePressEvent = self.on_path_label_clicked
        title_layout.addWidget(self.path_label, stretch=1)
        layout.addWidget(title_frame)
        self.logic_mods_frame = QFrame()
        self.logic_mods_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 8px;")
        logic_layout = QHBoxLayout(self.logic_mods_frame)
        logic_layout.setContentsMargins(0, 0, 0, 0)
        self.logic_mods_btn = QPushButton("创建 mod 运行文件夹 (LogicMods)")
        self.logic_mods_btn.setStyleSheet("QPushButton { background-color: #ff9800; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #fb8c00; }")
        self.logic_mods_btn.setCursor(Qt.PointingHandCursor)
        self.logic_mods_btn.clicked.connect(self.create_logic_mods)
        logic_layout.addWidget(self.logic_mods_btn)
        logic_layout.addStretch()
        layout.addWidget(self.logic_mods_frame)
        self.logic_mods_frame.setVisible(False)
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
        search_layout = QHBoxLayout(search_frame)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.parent.tr("search_placeholder"))
        self.search_edit.setStyleSheet("QLineEdit { padding: 6px; border: 1px solid #d1d8e0; border-radius: 6px; }")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_edit)
        layout.addWidget(search_frame)
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 8px;")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        self.back_btn = QPushButton("← 返回上级")
        self.back_btn.setStyleSheet("QPushButton { background-color: #e3f2fd; color: #1976d2; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #bbdef5; } QPushButton:pressed { background-color: #90caf9; }")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.back_btn.clicked.connect(self.go_up)
        self.back_btn.setEnabled(False)
        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addStretch()
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #2196f3; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #0b7dda; } QPushButton:pressed { background-color: #0a5e9e; }")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.refresh_btn.clicked.connect(self.load_current_directory)
        toolbar_layout.addWidget(self.refresh_btn)
        self.import_btn = QPushButton("📥 导入模组")
        self.import_btn.setStyleSheet("QPushButton { background-color: #9c27b0; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #8e24aa; } QPushButton:pressed { background-color: #6a1b9a; }")
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.import_btn.clicked.connect(self.import_mod)
        toolbar_layout.addWidget(self.import_btn)
        self.pack_btn = QPushButton("📦 打包选中")
        self.pack_btn.setStyleSheet("QPushButton { background-color: #3f51b5; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #303f9f; } QPushButton:pressed { background-color: #1a237e; }")
        self.pack_btn.setCursor(Qt.PointingHandCursor)
        self.pack_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pack_btn.clicked.connect(self.pack_selected)
        toolbar_layout.addWidget(self.pack_btn)
        self.delete_btn = QPushButton("❌ 删除选中")
        self.delete_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #c62828; } QPushButton:pressed { background-color: #b71c1c; }")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.delete_btn.clicked.connect(self.delete_selected)
        toolbar_layout.addWidget(self.delete_btn)
        self.open_dir_btn = QPushButton("📂 打开当前文件夹")
        self.open_dir_btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #45a049; } QPushButton:pressed { background-color: #3d8b40; }")
        self.open_dir_btn.setCursor(Qt.PointingHandCursor)
        self.open_dir_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.open_dir_btn.clicked.connect(self.open_current_folder)
        toolbar_layout.addWidget(self.open_dir_btn)
        self.submit_name_btn = QPushButton(self.parent.tr("submit_nickname"))
        self.submit_name_btn.setStyleSheet("QPushButton { background-color: #e67e22; color: white; border-radius: 4px; padding: 6px 12px; } QPushButton:hover { background-color: #d35400; } QPushButton:pressed { background-color: #a04000; }")
        self.submit_name_btn.setCursor(Qt.PointingHandCursor)
        self.submit_name_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.submit_name_btn.clicked.connect(lambda: webbrowser.open("https://f.wps.cn/g/02zho2bf/"))
        toolbar_layout.addWidget(self.submit_name_btn)
        toolbar_layout.addStretch()
        layout.addWidget(toolbar_frame)
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 5px;")
        table_layout = QVBoxLayout(table_frame)
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels(["文件名", "中文/俗名", "大小", "状态", "操作"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_table.customContextMenuRequested.connect(self.show_context_menu)
        self.file_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.file_table.setAcceptDrops(True)
        self.file_table.dragEnterEvent = self.drag_enter_event
        self.file_table.dropEvent = self.drop_event
        table_layout.addWidget(self.file_table)
        layout.addWidget(table_frame)
        self.hint_label = QLabel(self.parent.tr("multi_select_hint"))
        self.hint_label.setStyleSheet("color: #888; margin-top: 8px;")
        layout.addWidget(self.hint_label)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; margin-top: 5px;")
        layout.addWidget(self.status_label)
    def create_logic_mods(self):
        content_dir = os.path.dirname(self.mods_root)
        logic_path = os.path.join(content_dir, "LogicMods")
        try:
            os.makedirs(logic_path, exist_ok=True)
            self.parent.log_message(f"✅ 已创建 LogicMods 文件夹：{logic_path}")
            self.logic_mods_frame.setVisible(False)
            QMessageBox.information(self, "完成", f"已创建 LogicMods 文件夹\n路径：{logic_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建失败：{str(e)}")
    def check_logic_mods(self):
        if not self.mods_root:
            return
        content_dir = os.path.dirname(self.mods_root)
        logic_path = os.path.join(content_dir, "LogicMods")
        if not os.path.exists(logic_path):
            self.logic_mods_frame.setVisible(True)
        else:
            self.logic_mods_frame.setVisible(False)
    def load_current_directory(self):
        self.fetch_mod_name_map()
        if not self.mods_root or not os.path.exists(self.mods_root):
            self.file_table.setRowCount(0)
            self.path_label.setText("模组根目录不存在")
            return
        if self.current_path is None:
            self.current_path = self.mods_root
        if not os.path.exists(self.current_path):
            self.path_label.setText(f"路径不存在: {self.current_path}")
            self.file_table.setRowCount(0)
            return
        if self.current_path.startswith(self.mods_root):
            rel = os.path.relpath(self.current_path, self.mods_root)
            if rel == '.':
                display = self.mods_root + " (根目录)"
            else:
                display = f"{self.mods_root} → {rel}"
        else:
            display = self.current_path
        self.path_label.setText(f"📂 {display}")
        self.all_items.clear()
        try:
            items = os.listdir(self.current_path)
        except Exception as e:
            self.status_label.setText(f"无法读取目录：{str(e)}")
            return
        dirs = []
        files = []
        for name in items:
            full = os.path.join(self.current_path, name)
            if os.path.isdir(full):
                dirs.append((name, full, True))
            else:
                if name == "EscapeTheBackrooms-WindowsNoEditor.pak":
                    continue
                files.append((name, full, False))
        dirs.sort(key=lambda x: x[0].lower())
        def sort_key(item):
            name = item[0]
            if name.endswith('.disabled'):
                return name[:-9]
            return name
        files.sort(key=sort_key)
        for name, full, is_dir in dirs:
            display_name = name
            chinese_name = ""
            is_disabled = False
            self.all_items.append((display_name, chinese_name, full, is_dir, is_disabled, name))
        for name, full, is_dir in files:
            is_disabled = False
            display_name = name
            if name.lower().endswith('.pak.disabled'):
                is_disabled = True
                display_name = name[:-9]
            elif name.lower().endswith('.pak'):
                is_disabled = False
                display_name = name
            chinese_name = self.get_chinese_name(display_name) if not is_dir else ""
            self.all_items.append((display_name, chinese_name, full, is_dir, is_disabled, name))
        self.filter_items(self.search_edit.text())
        self.back_btn.setEnabled(self.current_path != self.mods_root)
        self.check_logic_mods()
    def import_mod(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择模组文件或压缩包", "", "PAK Files (*.pak);;ZIP Archives (*.zip);;All Files (*)")
        if not files:
            return
        success = 0
        for f in files:
            try:
                if f.lower().endswith('.zip'):
                    with zipfile.ZipFile(f, 'r') as zf:
                        zf.extractall(self.current_path)
                        for name in zf.namelist():
                            if os.path.basename(name) == "由逃离后室游戏工具打包生成.txt":
                                try:
                                    os.remove(os.path.join(self.current_path, name))
                                except:
                                    pass
                    success += 1
                    self.parent.log_message(f"📥 解压导入模组压缩包：{os.path.basename(f)}")
                else:
                    dest = os.path.join(self.current_path, os.path.basename(f))
                    if os.path.exists(dest):
                        reply = QMessageBox.question(self, "文件已存在", f"{os.path.basename(f)} 已存在，是否覆盖？", QMessageBox.Yes | QMessageBox.No)
                        if reply != QMessageBox.Yes:
                            continue
                    shutil.copy2(f, dest)
                    success += 1
                    self.parent.log_message(f"📥 导入模组：{os.path.basename(f)}")
            except Exception as e:
                QMessageBox.warning(self, "导入失败", str(e))
        if success:
            self.load_current_directory()
            QMessageBox.information(self, "完成", f"成功导入 {success} 个文件/压缩包")
    def on_cell_double_clicked(self, row, column):
        item = self.file_table.item(row, 0)
        if item:
            full_path, is_dir, _, _ = item.data(Qt.UserRole)
            if is_dir:
                self.enter_directory(full_path)
            elif full_path.lower().endswith('.txt'):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    QMessageBox.information(self, os.path.basename(full_path), content)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法读取文件：{str(e)}")
    def fetch_mod_name_map(self):
        import time
        base_url = "https://raw.giteeusercontent.com/yunjie666/etb-mod-names/raw/master/mod_names.json"
        timestamp = int(time.time() * 1000)
        JSON_URL = f"{base_url}?t={timestamp}"
        try:
            req = urllib.request.Request(JSON_URL, headers={
                'User-Agent': 'Mozilla/5.0',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, dict):
                if data != self.mod_name_map:
                    self.mod_name_map = data
                    self.parent.log_message(f"✅ 已从云端更新 {len(data)} 条模组名称映射")
                else:
                    self.parent.log_message(f"ℹ️ 云端映射无变化，当前共 {len(data)} 条")
                return True
            else:
                self.parent.log_message("⚠️ 云端返回的数据格式错误，应为一个字典")
                return False
        except Exception as e:
            self.parent.log_message(f"❌ 获取模组名称映射失败：{str(e)}")
            return False
    def get_chinese_name(self, filename: str) -> str:
        base = os.path.basename(filename)
        return self.mod_name_map.get(base, "")
    def on_search_text_changed(self, text):
        self.filter_items(text)
    def filter_items(self, text):
        if not text.strip():
            self.filtered_items = self.all_items[:]
        else:
            lower_text = text.lower()
            self.filtered_items = []
            for item in self.all_items:
                name = item[0].lower()
                chinese = item[1].lower()
                if lower_text in name or lower_text in chinese:
                    self.filtered_items.append(item)
        self.refresh_table_display()
        if len(self.filtered_items) == 0 and len(self.all_items) > 0:
            self.show_no_search_result()
        else:
            self.hide_no_search_result()
    def refresh_table_display(self):
        self.file_table.setRowCount(0)
        row = 0
        for item in self.filtered_items:
            display_name, chinese_name, full_path, is_dir, is_disabled, original_name = item
            self._add_table_row(row, display_name, chinese_name, full_path, is_dir, is_disabled, original_name)
            row += 1
        self.status_label.setText(f"共 {len(self.filtered_items)} 个模组（显示过滤结果）" if self.search_edit.text() else f"共 {len(self.all_items)} 个文件夹/文件")
    def show_no_search_result(self):
        self.file_table.setRowCount(1)
        msg_item = QTableWidgetItem(self.parent.tr("no_search_result"))
        msg_item.setTextAlignment(Qt.AlignCenter)
        self.file_table.setSpan(0, 0, 1, 5)
        self.file_table.setItem(0, 0, msg_item)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
    def hide_no_search_result(self):
        if self.file_table.rowCount() == 1 and self.file_table.item(0, 0) and self.file_table.item(0, 0).text() == self.parent.tr("no_search_result"):
            self.file_table.setRowCount(0)
    def _add_table_row(self, row, display_name, chinese_name, full_path, is_dir, is_disabled, original_name):
        self.file_table.insertRow(row)
        icon = "📁" if is_dir else ("🔴" if is_disabled else "🟢")
        name_item = QTableWidgetItem(f"{icon} {display_name}")
        name_item.setData(Qt.UserRole, (full_path, is_dir, is_disabled, original_name))
        if is_dir:
            name_item.setForeground(QBrush(QColor("#1976d2")))
        elif is_disabled:
            name_item.setForeground(QBrush(QColor("#f44336")))
        else:
            name_item.setForeground(QBrush(QColor("#2e7d32")))
        self.file_table.setItem(row, 0, name_item)
        chinese_item = QTableWidgetItem(chinese_name)
        if chinese_name:
            chinese_item.setForeground(QBrush(QColor("#9c27b0")))
        chinese_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.file_table.setItem(row, 1, chinese_item)
        if is_dir:
            size_item = QTableWidgetItem("文件夹")
        else:
            size = os.path.getsize(full_path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            size_item = QTableWidgetItem(size_str)
        size_item.setTextAlignment(Qt.AlignCenter)
        self.file_table.setItem(row, 2, size_item)
        if is_dir:
            status_item = QTableWidgetItem("—")
        else:
            status_item = QTableWidgetItem("已禁用" if is_disabled else "已启用")
            if is_disabled:
                status_item.setForeground(QBrush(QColor("#f44336")))
            else:
                status_item.setForeground(QBrush(QColor("#4caf50")))
        status_item.setTextAlignment(Qt.AlignCenter)
        self.file_table.setItem(row, 3, status_item)
        op_widget = QWidget()
        op_layout = QHBoxLayout(op_widget)
        op_layout.setContentsMargins(0,0,0,0)
        op_layout.setSpacing(4)
        if is_dir:
            btn = QPushButton("打开")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            btn.setStyleSheet("QPushButton { background-color: #e0e0e0; border-radius: 3px; padding: 2px 6px; font-size: 11px; } QPushButton:hover { background-color: #bdbdbd; } QPushButton:pressed { background-color: #9e9e9e; }")
            btn.clicked.connect(lambda _, p=full_path: self.enter_directory(p))
            op_layout.addWidget(btn)
        elif not is_dir:
            btn_text = "启用" if is_disabled else "禁用"
            btn = QPushButton(btn_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            if is_disabled:
                btn.setStyleSheet("QPushButton { background-color: #4caf50; color: white; border-radius: 3px; padding: 2px 6px; font-size: 11px; } QPushButton:hover { background-color: #45a049; } QPushButton:pressed { background-color: #3d8b40; }")
            else:
                btn.setStyleSheet("QPushButton { background-color: #ff9800; color: white; border-radius: 3px; padding: 2px 6px; font-size: 11px; } QPushButton:hover { background-color: #fb8c00; } QPushButton:pressed { background-color: #ef6c00; }")
            if is_disabled:
                btn.clicked.connect(lambda _, p=full_path: self.enable_mod(p, full_path))
            else:
                btn.clicked.connect(lambda _, p=full_path: self.disable_mod(p, full_path))
            op_layout.addWidget(btn)
        else:
            label = QLabel("—")
            label.setAlignment(Qt.AlignCenter)
            op_layout.addWidget(label)
        op_layout.addStretch()
        self.file_table.setCellWidget(row, 4, op_widget)
    def enter_directory(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.load_current_directory()
    def go_up(self):
        if self.current_path == self.mods_root:
            QMessageBox.information(self, self.parent.tr("warning_title"), self.parent.tr("already_top_level"))
            return
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.load_current_directory()
    def open_current_folder(self):
        if self.current_path and os.path.exists(self.current_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.current_path))
        else:
            QMessageBox.warning(self, "提示", "当前路径无效")
    def on_path_label_clicked(self, event):
        if not self.mods_root:
            return
        new_root = QFileDialog.getExistingDirectory(self, "选择 Paks 根目录", self.mods_root)
        if new_root and os.path.exists(new_root):
            self.mods_root = new_root
            self.current_path = self.mods_root
            self.load_current_directory()
    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def drop_event(self, event):
        urls = event.mimeData().urls()
        count = 0
        for url in urls:
            src = url.toLocalFile()
            if os.path.isfile(src):
                if src.lower().endswith('.pak') or src.lower().endswith('.zip'):
                    if src.lower().endswith('.zip'):
                        try:
                            with zipfile.ZipFile(src, 'r') as zf:
                                zf.extractall(self.current_path)
                                for name in zf.namelist():
                                    if os.path.basename(name) == "由逃离后室游戏工具打包生成.txt":
                                        try:
                                            os.remove(os.path.join(self.current_path, name))
                                        except:
                                            pass
                            count += 1
                            self.parent.log_message(f"📥 拖拽解压导入模组压缩包：{os.path.basename(src)}")
                        except Exception as e:
                            QMessageBox.warning(self, "导入失败", str(e))
                    else:
                        dest = os.path.join(self.current_path, os.path.basename(src))
                        if os.path.exists(dest):
                            reply = QMessageBox.question(self, "文件已存在", f"{os.path.basename(src)} 已存在，是否覆盖？", QMessageBox.Yes | QMessageBox.No)
                            if reply != QMessageBox.Yes:
                                continue
                        try:
                            shutil.copy2(src, dest)
                            count += 1
                            self.parent.log_message(f"📥 拖拽导入模组：{os.path.basename(src)}")
                        except Exception as e:
                            QMessageBox.warning(self, "导入失败", str(e))
        if count:
            self.load_current_directory()
            QMessageBox.information(self, "完成", f"成功导入 {count} 个文件/压缩包")
    def pack_selected(self):
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要打包的项目")
            return
        items_to_pack = []
        for row in selected_rows:
            item = self.file_table.item(row, 0)
            if item:
                full_path, is_dir, is_disabled, _ = item.data(Qt.UserRole)
                if is_dir:
                    items_to_pack.append((full_path, is_dir, False))
                else:
                    items_to_pack.append((full_path, is_dir, is_disabled))
        if not items_to_pack:
            QMessageBox.warning(self, "提示", "没有选中任何项目")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "保存打包文件", "", "ZIP Archive (*.zip)")
        if not save_path:
            return
        try:
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                description_content = ("此文件由逃离后室游戏工具打包生成。\n打包时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                                       "\n包含模组列表请查看压缩包内文件。\n\n本工具由逃离后室玩友群制作，下载本工具请加群获得：https://taolihoushiwanyouqun.wordpress.com/contact/")
                zf.writestr("由逃离后室游戏工具打包生成.txt", description_content.encode('utf-8'))
                for path, is_dir, is_disabled in items_to_pack:
                    if is_dir:
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                full = os.path.join(root, file)
                                arcname = os.path.relpath(full, os.path.dirname(path))
                                zf.write(full, arcname)
                    else:
                        if is_disabled:
                            arcname = os.path.basename(path)[:-9]
                        else:
                            arcname = os.path.basename(path)
                        zf.write(path, arcname)
            QMessageBox.information(self, "完成", f"已打包 {len(items_to_pack)} 个项目，并附带了说明文件")
            self.parent.log_message(f"📦 打包选中：{len(items_to_pack)} 个项目 -> {os.path.basename(save_path)}，已添加说明文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打包失败：{str(e)}")
    def delete_selected(self):
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的项目")
            return
        reply = QMessageBox.question(self, "确认删除", f"确定要永久删除 {len(selected_rows)} 个项目吗？", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        count = 0
        for row in sorted(selected_rows, reverse=True):
            item = self.file_table.item(row, 0)
            if item:
                full_path, is_dir, _, _ = item.data(Qt.UserRole)
                try:
                    if is_dir:
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    count += 1
                    self.parent.log_message(f"❌ 删除：{os.path.basename(full_path)}")
                except Exception as e:
                    QMessageBox.warning(self, "删除失败", str(e))
        if count:
            self.load_current_directory()
            QMessageBox.information(self, "完成", f"已删除 {count} 个项目")
    def show_context_menu(self, pos):
        selected_rows = set()
        for item in self.file_table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            return
        pak_rows = []
        for row in selected_rows:
            item = self.file_table.item(row, 0)
            if item:
                _, is_dir, is_disabled, _ = item.data(Qt.UserRole)
                if not is_dir:
                    pak_rows.append((row, is_disabled))
        if not pak_rows:
            return
        menu = QMenu()
        has_enabled = any(not disabled for _, disabled in pak_rows)
        has_disabled = any(disabled for _, disabled in pak_rows)
        if has_enabled:
            disable_action = menu.addAction(self.parent.tr("disable_selected"))
            disable_action.triggered.connect(lambda: self.bulk_disable([r for r, d in pak_rows if not d]))
        if has_disabled:
            enable_action = menu.addAction(self.parent.tr("enable_selected"))
            enable_action.triggered.connect(lambda: self.bulk_enable([r for r, d in pak_rows if d]))
        if menu.actions():
            menu.exec_(self.file_table.viewport().mapToGlobal(pos))
    def bulk_disable(self, rows):
        success = 0
        for row in rows:
            item = self.file_table.item(row, 0)
            full_path, _, _, _ = item.data(Qt.UserRole)
            if full_path.endswith('.disabled'):
                continue
            new_path = full_path + '.disabled'
            try:
                os.rename(full_path, new_path)
                self.parent.log_message(f"禁用模组：{os.path.basename(full_path)}")
                success += 1
            except Exception as e:
                self.parent.log_message(f"❌ 禁用失败：{os.path.basename(full_path)} - {str(e)}")
        if success:
            self.load_current_directory()
            QMessageBox.information(self, "完成", self.parent.tr("bulk_operation_notice") + f" 已禁用 {success} 个模组")
    def bulk_enable(self, rows):
        success = 0
        for row in rows:
            item = self.file_table.item(row, 0)
            full_path, _, _, _ = item.data(Qt.UserRole)
            if not full_path.endswith('.disabled'):
                continue
            new_path = full_path[:-9]
            try:
                os.rename(full_path, new_path)
                self.parent.log_message(f"启用模组：{os.path.basename(new_path)}")
                success += 1
            except Exception as e:
                self.parent.log_message(f"❌ 启用失败：{os.path.basename(new_path)} - {str(e)}")
        if success:
            self.load_current_directory()
            QMessageBox.information(self, "完成", self.parent.tr("bulk_operation_notice") + f" 已启用 {success} 个模组")
    def disable_mod(self, pak_path, full_path):
        if full_path.endswith('.disabled'):
            QMessageBox.information(self, "提示", "该模组已经是禁用状态")
            return
        new_path = full_path + '.disabled'
        try:
            os.rename(full_path, new_path)
            self.parent.log_message(f"禁用模组：{os.path.basename(full_path)}")
            self.load_current_directory()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"禁用失败：{str(e)}")
    def enable_mod(self, pak_path, full_path):
        if not full_path.endswith('.disabled'):
            QMessageBox.information(self, "提示", "该模组已经是启用状态")
            return
        new_path = full_path[:-9]
        try:
            os.rename(full_path, new_path)
            self.parent.log_message(f"启用模组：{os.path.basename(new_path)}")
            self.load_current_directory()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启用失败：{str(e)}")

class IndicatorBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(4)
        self.setStyleSheet("background-color: #2196f3; border-radius: 2px;")
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(200)
    def move_to_button(self, button):
        if not button:
            return
        parent = self.parent()
        if not parent:
            return
        global_pos = button.mapToGlobal(QPoint(0, 0))
        local_pos = parent.mapFromGlobal(global_pos)
        y = local_pos.y()
        height = button.height()
        current_geo = self.geometry()
        self.animation.stop()
        shrink_geo = QRect(current_geo.x(), current_geo.y() + current_geo.height()//2 - 2, 4, 4)
        self.animation.setEndValue(shrink_geo)
        self.animation.start()
        def after_shrink():
            if not self or not parent:
                return
            mid_y = y + height//2 - 2
            move_geo = QRect(local_pos.x(), mid_y, 4, 4)
            self.animation.setEndValue(move_geo)
            self.animation.start()
            def after_move():
                if not self or not parent:
                    return
                expand_geo = QRect(local_pos.x(), y, 4, height)
                self.animation.setEndValue(expand_geo)
                self.animation.start()
            QTimer.singleShot(200, after_move)
        QTimer.singleShot(200, after_shrink)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font_size = 11
        self.log_messages = []
        self.current_button = None
        self.current_panel_class = None
        self.auto_update_thread = None
        self.nav_btn_style = "QPushButton { background-color: transparent; text-align: left; padding: 8px 12px; border-radius: 8px; color: #2c3e50; font-weight: 500; } QPushButton:hover { background-color: #f0f2f5; } QPushButton:pressed { background-color: #e4e7eb; }"
        self.active_style = "QPushButton { background-color: #e4e7eb; text-align: left; padding: 8px 12px; border-radius: 8px; color: #2c3e50; font-weight: 500; }"
        self.init_config()
        self.init_ui()
        self.set_font_size(self.font_size)
        history = load_log_from_file()
        for msg in history:
            self.log_messages.append(msg)
        self.log_message(self.tr('init_complete') + "\n")
        self.setWindowIcon(get_icon())
        self.remove_old_config_flag()
        self.scan_old_config()
        self.mod_panel = ModManagementPanel(self)
        QTimer.singleShot(100, self.init_indicator)
        QTimer.singleShot(3000, self.auto_check_update)
    def init_config(self):
        config = load_config()
        self.font_size = config.get("font_size", 11)
    def set_font_size(self, size):
        self.font_size = size
        save_config(font_size=size)
        font = QFont("Microsoft YaHei", size)
        if not QFont("Microsoft YaHei").exactMatch():
            font = QFont("Segoe UI", size)
        QApplication.setFont(font)
        for widget in QApplication.allWidgets():
            widget.setFont(font)
            if hasattr(widget, 'load_items'):
                QTimer.singleShot(10, widget.load_items)
        if hasattr(self, 'current_panel') and isinstance(self.current_panel, ModManagementPanel):
            self.current_panel.load_current_directory()
    def tr(self, key):
        return LANG["zh"].get(key, key)
    def init_ui(self):
        self.setMinimumSize(1200,800)
        self.resize(1400,900)
        self.setWindowTitle(self.tr("window_title"))
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QWidget { font-family: "Microsoft YaHei","Segoe UI"; font-size: 13px; }
            QPushButton { border: none; border-radius: 6px; padding: 6px 12px; font-weight: 500; }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:pressed { background-color: #d0d0d0; }
            QTableWidget { border: 1px solid #e0e0e0; border-radius: 8px; background-color: white; gridline-color: #f0f0f0; }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section { background-color: #f5f7fa; padding: 8px; border: none; border-bottom: 1px solid #e0e0e0; font-weight: 600; }
            QScrollArea { border: none; background-color: transparent; }
            QFrame { background-color: white; border-radius: 12px; }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #b0b0b0;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4caf50;
                border-color: #4caf50;
            }
            QCheckBox::indicator:hover {
                border-color: #4caf50;
            }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)
        left_panel = QFrame()
        left_panel.setFixedWidth(260)
        left_panel.setStyleSheet("background-color: white; border-radius: 16px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15,20,15,20)
        left_layout.setSpacing(8)
        self.indicator = IndicatorBar(left_panel)
        left_layout.addWidget(self.indicator, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.indicator.raise_()
        self.buttons_with_indicator = []
        self.clean_files_label = QLabel(self.tr('clean_files'))
        self.clean_files_label.setStyleSheet("font-weight: bold; color: #7f8c8d; padding: 4px 12px;")
        left_layout.addWidget(self.clean_files_label)
        self.clean_save_btn = QPushButton(self.tr('clean_save'))
        self.clean_save_btn.setStyleSheet(self.nav_btn_style)
        self.clean_save_btn.setCursor(Qt.PointingHandCursor)
        self.clean_save_btn.setProperty("nav_button", True)
        self.clean_save_btn.clicked.connect(lambda: self.set_active_button(self.clean_save_btn, SaveCleanPanel))
        left_layout.addWidget(self.clean_save_btn)
        self.buttons_with_indicator.append(self.clean_save_btn)
        self.clean_crash_btn = QPushButton(self.tr('clean_crash'))
        self.clean_crash_btn.setStyleSheet(self.nav_btn_style)
        self.clean_crash_btn.setCursor(Qt.PointingHandCursor)
        self.clean_crash_btn.setProperty("nav_button", True)
        self.clean_crash_btn.clicked.connect(lambda: self.set_active_button(self.clean_crash_btn, CrashCleanPanel))
        left_layout.addWidget(self.clean_crash_btn)
        self.buttons_with_indicator.append(self.clean_crash_btn)
        self.file_ops_label = QLabel(self.tr('file_ops'))
        self.file_ops_label.setStyleSheet("font-weight: bold; color: #7f8c8d; padding: 4px 12px; margin-top: 12px;")
        left_layout.addWidget(self.file_ops_label)
        self.open_save_btn = QPushButton(self.tr('open_save'))
        self.open_save_btn.setStyleSheet(self.nav_btn_style)
        self.open_save_btn.setCursor(Qt.PointingHandCursor)
        self.open_save_btn.setProperty("nav_button", True)
        self.open_save_btn.clicked.connect(self.open_save_folder)
        left_layout.addWidget(self.open_save_btn)
        self.open_crash_btn = QPushButton(self.tr('open_crash'))
        self.open_crash_btn.setStyleSheet(self.nav_btn_style)
        self.open_crash_btn.setCursor(Qt.PointingHandCursor)
        self.open_crash_btn.setProperty("nav_button", True)
        self.open_crash_btn.clicked.connect(self.open_crash_folder)
        left_layout.addWidget(self.open_crash_btn)
        self.ue4_management_btn = QPushButton("UE4 管理")
        self.ue4_management_btn.setStyleSheet(self.nav_btn_style)
        self.ue4_management_btn.setCursor(Qt.PointingHandCursor)
        self.ue4_management_btn.setProperty("nav_button", True)
        self.ue4_management_btn.clicked.connect(lambda: self.set_active_button(self.ue4_management_btn, UE4ManagementPanel))
        left_layout.addWidget(self.ue4_management_btn)
        self.buttons_with_indicator.append(self.ue4_management_btn)
        self.mod_management_btn = QPushButton(self.tr('mod_management'))
        self.mod_management_btn.setStyleSheet(self.nav_btn_style)
        self.mod_management_btn.setCursor(Qt.PointingHandCursor)
        self.mod_management_btn.setProperty("nav_button", True)
        self.mod_management_btn.clicked.connect(lambda: self.set_active_button(self.mod_management_btn, ModManagementPanel))
        left_layout.addWidget(self.mod_management_btn)
        self.buttons_with_indicator.append(self.mod_management_btn)
        self.download_mod_btn = QPushButton(self.tr('download_mod'))
        self.download_mod_btn.setStyleSheet(self.nav_btn_style)
        self.download_mod_btn.setCursor(Qt.PointingHandCursor)
        self.download_mod_btn.setProperty("nav_button", True)
        self.download_mod_btn.clicked.connect(lambda: self.set_active_button(self.download_mod_btn, DownloadModPanel))
        left_layout.addWidget(self.download_mod_btn)
        self.other_label = QLabel(self.tr("other"))
        self.other_label.setStyleSheet("font-weight: bold; color: #7f8c8d; padding: 4px 12px; margin-top: 12px;")
        left_layout.addWidget(self.other_label)
        self.show_path_btn = QPushButton(self.tr('show_path'))
        self.show_path_btn.setStyleSheet(self.nav_btn_style)
        self.show_path_btn.setCursor(Qt.PointingHandCursor)
        self.show_path_btn.setProperty("nav_button", True)
        self.show_path_btn.clicked.connect(lambda: self.set_active_button(self.show_path_btn, PathInfoPanel))
        left_layout.addWidget(self.show_path_btn)
        self.buttons_with_indicator.append(self.show_path_btn)
        self.log_btn = QPushButton(self.tr('log'))
        self.log_btn.setStyleSheet(self.nav_btn_style)
        self.log_btn.setCursor(Qt.PointingHandCursor)
        self.log_btn.setProperty("nav_button", True)
        self.log_btn.clicked.connect(lambda: self.set_active_button(self.log_btn, LogPanel))
        left_layout.addWidget(self.log_btn)
        self.buttons_with_indicator.append(self.log_btn)
        self.uninstall_btn = QPushButton(self.tr('uninstall'))
        self.uninstall_btn.setStyleSheet(self.nav_btn_style)
        self.uninstall_btn.setCursor(Qt.PointingHandCursor)
        self.uninstall_btn.setProperty("nav_button", True)
        self.uninstall_btn.clicked.connect(lambda: self.set_active_button(self.uninstall_btn, UninstallPanel))
        left_layout.addWidget(self.uninstall_btn)
        self.buttons_with_indicator.append(self.uninstall_btn)
        left_layout.addStretch()
        self.about_settings_btn = QPushButton(self.tr('about_settings'))
        self.about_settings_btn.setCursor(Qt.PointingHandCursor)
        self.about_settings_btn.setStyleSheet("QPushButton { background-color: #e67e22; color: white; border-radius: 8px; padding: 8px 12px; text-align: left; font-weight: bold; margin-top: 12px; } QPushButton:hover { background-color: #d35400; } QPushButton:pressed { background-color: #a04000; }")
        self.about_menu = QMenu(self)
        self.about_settings_btn.setMenu(self.about_menu)
        update_action = self.about_menu.addAction(self.tr('check_update'))
        update_action.triggered.connect(lambda: self.set_active_button(None, UpdatePanel))
        website_action = self.about_menu.addAction(self.tr('website'))
        website_action.triggered.connect(lambda: self.set_active_button(None, WebsitePanel))
        about_action = self.about_menu.addAction(self.tr('about'))
        about_action.triggered.connect(lambda: self.set_active_button(None, AboutPanel))
        thanks_action = self.about_menu.addAction(self.tr('thanks'))
        thanks_action.triggered.connect(lambda: self.set_active_button(None, ThanksPanel))
        left_layout.addWidget(self.about_settings_btn)
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: white; border-radius: 16px;")
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.right_panel, stretch=1)
        self.mod_panel = ModManagementPanel(self)
        self.set_active_button(None, AboutPanel)
    def init_indicator(self):
        pass
    def set_active_button(self, btn, panel_class):
        for w in self.findChildren(QPushButton):
            if w.property("nav_button"):
                w.setStyleSheet(self.nav_btn_style)
        if btn and btn in self.buttons_with_indicator:
            btn.setStyleSheet(self.active_style)
            self.indicator.move_to_button(btn)
        self.current_button = btn
        self.current_panel_class = panel_class
        panel = panel_class(self)
        if panel_class == ModManagementPanel:
            self.mod_panel = panel
        self.set_right_panel(panel)
    def reload_current_panel(self):
        if self.current_panel_class:
            panel = self.current_panel_class(self)
            if self.current_panel_class == ModManagementPanel:
                self.mod_panel = panel
            self.set_right_panel(panel)
    def set_right_panel(self, panel):
        for i in reversed(range(self.right_layout.count())):
            w = self.right_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.current_panel = panel
        self.right_layout.addWidget(panel)
    def log_message(self, msg):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        full_msg = timestamp + msg
        self.log_messages.append(full_msg)
        append_log_to_file(full_msg)
        if hasattr(self, 'current_panel') and isinstance(self.current_panel, LogPanel):
            self.current_panel.append_log(full_msg)
    def open_save_folder(self):
        if os.path.exists(SAVE_PATH):
            QDesktopServices.openUrl(QUrl.fromLocalFile(SAVE_PATH))
            self.log_message(self.tr('open_save_log').format(SAVE_PATH))
            QMessageBox.information(self, self.tr('warning_title'), self.tr('open_save_log').format(SAVE_PATH).split('\n')[0])
        else:
            QMessageBox.warning(self, self.tr('warning_title'), self.tr('save_folder_not_exist'))
            self.log_message(self.tr('save_folder_not_exist'))
    def open_crash_folder(self):
        if os.path.exists(CRASH_PATH):
            QDesktopServices.openUrl(QUrl.fromLocalFile(CRASH_PATH))
            self.log_message(self.tr('open_crash_log').format(CRASH_PATH))
            QMessageBox.information(self, self.tr('warning_title'), self.tr('open_crash_log').format(CRASH_PATH).split('\n')[0])
        else:
            QMessageBox.warning(self, self.tr('warning_title'), self.tr('crash_folder_not_exist'))
            self.log_message(self.tr('crash_folder_not_exist'))
    def remove_old_config_flag(self):
        if os.path.exists(OLD_CONFIG_CLEANED_FLAG):
            try:
                os.remove(OLD_CONFIG_CLEANED_FLAG)
                self.log_message("🗑️ 已删除旧版配置清理标记文件，本次将重新扫描")
            except Exception as e:
                self.log_message(f"❌ 删除标记文件失败：{str(e)}")
    def scan_old_config(self):
        self.scan_thread = OldConfigScanThread()
        self.scan_thread.finished.connect(self.on_old_config_scan_finished)
        self.scan_thread.start()
    def on_old_config_scan_finished(self, found_list):
        if not found_list:
            return
        for path in found_list:
            self.log_message(self.tr('log_old_config_detected').format(path))
        msg = self.tr('old_config_msg').format("\n".join(found_list))
        reply = QMessageBox.question(self, self.tr('old_config_found'), msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            success_all = True
            for path in found_list:
                try:
                    shutil.rmtree(path)
                    self.log_message(self.tr('log_old_config_cleaned').format(path))
                except Exception as e:
                    success_all = False
                    self.log_message(f"❌ 删除失败：{path} - {str(e)}")
            if success_all:
                QMessageBox.information(self, self.tr('warning_title'), self.tr('old_config_deleted'))
            else:
                QMessageBox.warning(self, self.tr('warning_title'), self.tr('old_config_delete_failed').format("部分文件夹删除失败，请手动删除"))
        else:
            for path in found_list:
                self.log_message(self.tr('log_old_config_skip').format(path))
    def auto_check_update(self):
        self.log_message("🔄 自动检查更新...")
        self.auto_update_thread = UpdateCheckThread()
        self.auto_update_thread.finished.connect(self.on_auto_update_result)
        self.auto_update_thread.start()
    def on_auto_update_result(self, data, error):
        if hasattr(self, 'auto_update_thread'):
            self.auto_update_thread.finished.disconnect(self.on_auto_update_result)
            self.auto_update_thread.deleteLater()
            del self.auto_update_thread
        if error:
            self.log_message(f"❌ 自动检查更新失败：{error}")
            return
        latest = data.get("latest_version", "")
        download_url = data.get("download_url", "")
        notes = data.get("release_notes", "")
        if latest and is_newer(latest, VERSION):
            self.log_message(f"✅ 发现新版本 V{latest}")
            reply = QMessageBox.question(self, "发现新版本",
                                         f"发现新版本 V{latest}\n更新说明：{notes}\n\n是否立即下载？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes and download_url:
                webbrowser.open(download_url)
        else:
            self.log_message("✅ 已自动检查更新：已是最新版本")

def tr(key):
    return LANG["zh"].get(key, key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(get_icon())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())