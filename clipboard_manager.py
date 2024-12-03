import win32clipboard
import keyboard
import time
from logger_manager import LoggerManager

class ClipboardManager:
    @staticmethod
    def get_selected_text():
        """获取选中的文本"""
        logger = LoggerManager.get_logger()
        
        # 保存当前剪贴板内容
        try:
            win32clipboard.OpenClipboard()
            try:
                old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            except:
                old_clipboard = ''
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"保存剪贴板内容失败: {e}")
            return ''

        # 等待热键释放
        while keyboard.is_pressed('alt') or keyboard.is_pressed('\\') or keyboard.is_pressed('ctrl'):
            time.sleep(0.1)

        # 清空剪贴板
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"清空剪贴板失败: {e}")
            return ''

        # 复制选中文本
        time.sleep(0.3)
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.5)

        # 获取选中的文本
        max_attempts = 3
        selected_text = ''
        for _ in range(max_attempts):
            try:
                win32clipboard.OpenClipboard()
                try:
                    selected_text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                except Exception as e:
                    logger.error(f"获取剪贴板数据失败: {e}")
                    selected_text = ''
                win32clipboard.CloseClipboard()
                if selected_text and selected_text.strip():
                    break
            except Exception as e:
                logger.error(f"访问剪贴板失败: {e}")
                selected_text = ''
            time.sleep(0.1)

        # 恢复原始剪贴板内容
        if old_clipboard:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(old_clipboard, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except Exception as e:
                logger.error(f"恢复剪贴板内容失败: {e}")

        # 确保返回的是有效的 Unicode 字符串
        if not selected_text:
            return ''
            
        try:
            # 尝试编码和解码来清理文本
            cleaned_text = selected_text.encode('utf-8', errors='ignore').decode('utf-8')
            return cleaned_text
        except Exception as e:
            logger.error(f"文本编码转换失败: {e}")
            return ''

    @staticmethod
    def write_text(text):
        """写入文本到当前光标位置"""
        # 保存当前剪贴板内容
        try:
            win32clipboard.OpenClipboard()
            try:
                old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            except:
                old_clipboard = ''
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"保存剪贴板内容失败: {e}")
            return ''

        # 将新文本写入剪贴板
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"写入剪贴板失败: {e}")
            return ''

        # 等待一小段时间确保剪贴板内容已更新
        time.sleep(0.2)

        # 粘贴文本
        keyboard.press_and_release('ctrl+v')

        # 等待粘贴完成
        time.sleep(0.2)

        # 恢复原始剪贴板内容
        if old_clipboard:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(old_clipboard, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except Exception as e:
                logger.error(f"恢复剪贴板内容失败: {e}")
