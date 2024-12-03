import win32clipboard
import keyboard
import time

class ClipboardManager:
    @staticmethod
    def get_selected_text():
        """获取选中的文本"""
        # 保存当前剪贴板内容
        win32clipboard.OpenClipboard()
        try:
            old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            old_clipboard = ''
        win32clipboard.CloseClipboard()

        # 等待热键释放
        while keyboard.is_pressed('alt') or keyboard.is_pressed('\\') or keyboard.is_pressed('ctrl'):
            time.sleep(0.1)

        # 清空剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()

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
                selected_text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                if selected_text.strip():
                    break
            except:
                win32clipboard.CloseClipboard()
                time.sleep(0.3)

        # 恢复原始剪贴板内容
        if old_clipboard:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(old_clipboard)
            win32clipboard.CloseClipboard()

        return selected_text

    @staticmethod
    def write_text(text):
        """写入文本到当前光标位置"""
        # 保存当前剪贴板内容
        win32clipboard.OpenClipboard()
        try:
            old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            old_clipboard = ''
        win32clipboard.CloseClipboard()

        # 将新文本写入剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()

        # 等待一小段时间确保剪贴板内容已更新
        time.sleep(0.2)

        # 粘贴文本
        keyboard.press_and_release('ctrl+v')

        # 等待粘贴完成
        time.sleep(0.2)

        # 恢复原始剪贴板内容
        if old_clipboard:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(old_clipboard)
            win32clipboard.CloseClipboard()
