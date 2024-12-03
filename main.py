import tkinter as tk
import keyboard
import threading
import time
import logging
from ollama_api import ChatSession as OllamaChatSession, OllamaAPI
from oai_api import ChatSession as OAIChatSession
from config_manager import ConfigManager
from clipboard_manager import ClipboardManager
from ui_manager import UIManager
from logger_manager import LoggerManager

class SmartCopilot:
    def __init__(self):
        """初始化应用程序"""
        # 初始化日志系统
        self.logger = LoggerManager.get_logger()
        self.logger.info("启动智能写作助手")
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("智能写作助手")
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化UI管理器
        self.ui_manager = UIManager(self.root, self.config_manager, self.on_config_save)
        
        # 初始化API客户端
        self.setup_api_client()
        
        # 设置默认的聊天会话
        self.setup_default_chat_session()
        
        # 绑定快捷键
        self.bind_shortcuts()
        
        self.last_response = ""  # 添加变量存储上一次的回复

    def setup_api_client(self):
        """初始化API客户端"""
        try:
            config = self.config_manager.get_config()
            api_type = config.get('api_type', 'OpenAI兼容')
            
            if api_type == 'Ollama':
                self.api_client = OllamaAPI(self.config_manager)
            else:  # OpenAI 或 OpenAI兼容模式
                self.api_client = None  # OpenAI模式不需要专门的客户端
                
        except Exception as e:
            self.logger.error(f"初始化API客户端失败: {e}")

    def setup_default_chat_session(self):
        """设置默认的聊天会话"""
        try:
            config = self.config_manager.get_config()
            current_role = config.get('current_role', '通用助手')
            roles = config.get('roles', [])
            current_role_config = next((role for role in roles if role['name'] == current_role), None)
            
            if current_role_config:
                api_type = config.get('api_type', 'OpenAI兼容')
                model = config.get('model')
                base_url = config.get('base_url')
                
                # 记录详细的配置信息
                self.logger.info(f"当前配置 - API类型: {api_type}, 模型: {model}, 角色: {current_role}")
                self.logger.info(f"API地址: {base_url}")
                
                if api_type == 'Ollama':
                    self.chat_session = self.api_client.set_chat_session(
                        model=model,
                        system_prompt={
                            "role": "system",
                            "content": current_role_config.get('input_prompt', ''),
                            "input_prompt": current_role_config.get('input_prompt', ''),
                            "output_prompt": current_role_config.get('output_prompt', '')
                        },
                        keep_history=config.get('keep_history', True)
                    )
                else:  # OpenAI 或 OpenAI兼容模式
                    self.chat_session = OAIChatSession(
                        api_key=config.get('apikey'),
                        base_url=base_url,
                        model=model,
                        system_prompt={
                            "role": "system",
                            "content": current_role_config.get('input_prompt', '')
                        }
                    )
                self.logger.info(f"聊天会话已初始化完成")
            else:
                self.logger.warning(f"未找到角色配置: {current_role}")
                
        except Exception as e:
            self.logger.error(f"设置默认聊天会话失败: {str(e)}")

    def bind_shortcuts(self):
        """绑定快捷键"""
        try:
            self.logger.info("绑定快捷键")
            keyboard.add_hotkey('ctrl+alt+\\', self.handle_text_complete)
            keyboard.add_hotkey('ctrl+alt+/', self.continue_output)
            keyboard.add_hotkey('ctrl+esc', self.clear_history_with_notification)
            self.logger.info("快捷键绑定完成")
        except Exception as e:
            self.logger.error(f"绑定快捷键失败: {e}")

    def handle_text_complete(self):
        """处理文本补全"""
        try:
            # 获取选中的文本
            selected_text = ClipboardManager.get_selected_text()
            if not selected_text:
                self.logger.warning("未选中文本")
                return

            self.logger.info("开始文本补全")
            # 获取配置
            config = self.config_manager.get_config()
            
            # 获取当前角色的配置
            current_role = config.get('current_role', '通用助手')
            roles = config.get('roles', [])
            role = next((r for r in roles if r['name'] == current_role), None)
            
            # 使用角色配置，如果没有则使用全局配置
            text_complete_number = role.get('text_complete_number', config['text_complete_number']) if role else config['text_complete_number']
            temperature = role.get('temperature', config['temperature']) if role else config['temperature']

            self.logger.info(f"发送聊天请求 - 角色: {current_role}, temperature: {temperature}, max_tokens: {text_complete_number}")

            # 调用API获取补全
            api_type = config.get('api_type', 'OpenAI兼容')
            
            if api_type == 'Ollama':
                response = self.api_client.chat(
                    selected_text,
                    {
                        "num_ctx": int(text_complete_number),
                        "mirostat": 0,
                        "mirostat_eta": float(temperature)
                    }
                )
            else:  # OpenAI 或 OpenAI兼容模式
                response = self.chat_session.chat(
                    selected_text,
                    temperature=float(temperature),
                    max_tokens=int(text_complete_number)
                )
            
            # 更新最后的响应
            self.last_response = response
            
            # 输出到剪贴板
            ClipboardManager.write_text(response)
            self.logger.info("文本补全完成")
            
        except Exception as e:
            self.logger.error(f"文本补全失败: {e}")

    def clear_history(self):
        """清除历史记录"""
        try:
            if hasattr(self, 'chat_session') and self.chat_session:
                self.chat_session.clear_history()
                self.logger.info("历史记录已清除")
            else:
                self.logger.warning("没有活动的聊天会话")
        except Exception as e:
            self.logger.error(f"清除历史记录失败: {e}")

    def clear_history_with_notification(self):
        """清除历史记录并通知用户"""
        self.clear_history()
        print("历史记录已清除")

    def continue_output(self):
        """继续输出功能"""
        try:
            if not self.last_response:
                self.logger.warning("没有上一次的回复可以继续")
                return

            self.logger.info("开始继续生成")
            # 构建继续输出的提示
            continue_prompt = "请继续上文未完成的内容"
            
            # 获取配置
            config = self.config_manager.get_config()
            
            # 获取当前角色的配置
            current_role = config.get('current_role', '通用助手')
            roles = config.get('roles', [])
            role = next((r for r in roles if r['name'] == current_role), None)
            
            # 使用角色配置，如果没有则使用全局配置
            text_complete_number = role.get('text_complete_number', config['text_complete_number']) if role else config['text_complete_number']
            temperature = role.get('temperature', config['temperature']) if role else config['temperature']

            self.logger.info(f"继续生成 - 角色: {current_role}, temperature: {temperature}, max_tokens: {text_complete_number}")

            # 调用API继续生成
            api_type = config.get('api_type', 'OpenAI兼容')
            
            if api_type == 'Ollama':
                response = self.api_client.chat(
                    continue_prompt,
                    {
                        "num_ctx": int(text_complete_number),
                        "mirostat": 0,
                        "mirostat_eta": float(temperature)
                    }
                )
            else:  # OpenAI 或 OpenAI兼容模式
                response = self.chat_session.chat(
                    continue_prompt,
                    temperature=float(temperature),
                    max_tokens=int(text_complete_number)
                )
                
            # 更新最后的响应
            self.last_response = response
            
            # 输出到剪贴板
            ClipboardManager.write_text(response)
            self.logger.info("继续生成完成")
            
        except Exception as e:
            self.logger.error(f"继续输出失败: {e}")

    def on_config_save(self, config):
        """当配置保存时的回调函数"""
        try:
            # 保存配置
            self.config_manager.save_config(config)
            
            # 更新API客户端配置
            self.setup_api_client()
            
            # 获取当前角色的提示词
            current_role = config.get('current_role', '通用助手')
            roles = config.get('roles', [])
            role = next((r for r in roles if r['name'] == current_role), None)
            
            if role:
                # 获取角色的输入和输出提示词
                input_prompt = role.get('input_prompt', '')
                output_prompt = role.get('output_prompt', '')
                
                # 重新初始化聊天会话
                api_type = config.get('api_type', 'OpenAI兼容')
                
                if api_type == 'Ollama':
                    self.chat_session = self.api_client.set_chat_session(
                        model=config.get('model'),
                        system_prompt={
                            "role": "system",
                            "content": input_prompt,
                            "input_prompt": input_prompt,
                            "output_prompt": output_prompt
                        },
                        keep_history=config.get('keep_history', True)
                    )
                else:  # OpenAI 或 OpenAI兼容模式
                    self.chat_session = OAIChatSession(
                        api_key=config.get('apikey'),
                        base_url=config.get('base_url'),
                        model=config.get('model'),
                        system_prompt={
                            "role": "system",
                            "content": input_prompt
                        }
                    )
                self.logger.info(f"更新聊天会话配置 - 角色: {current_role}, 输入提示词: {input_prompt}, 输出提示词: {output_prompt}")
            else:
                self.logger.warning(f"未找到角色配置: {current_role}")
                
            self.logger.info("配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")

    def run(self):
        """运行程序"""
        try:
            self.logger.info("启动主程序")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"程序运行错误: {e}")
        finally:
            self.logger.info("程序退出")

if __name__ == "__main__":
    app = SmartCopilot()
    app.run()
