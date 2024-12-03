import os
import ollama
from logger_manager import LoggerManager

class OllamaAPI:
    def __init__(self, config_manager):
        """
        初始化 Ollama API
        :param config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.chat_session = None
        self.system_prompt = {"role": "system", "content": "", "input_prompt": "", "output_prompt": ""}
        self.logger = LoggerManager.get_logger()
        
        # 设置环境变量，尝试禁用 rate limit
        os.environ['OLLAMA_ORIGINS'] = '*'  # 允许所有来源
        if config_manager.get_config().get('base_url'):
            os.environ['OLLAMA_HOST'] = config_manager.get_config().get('base_url')

    def set_chat_session(self, model: str = None, system_prompt: dict = None, keep_history: bool = True):
        """
        设置聊天会话
        :param model: 模型名称，如果为None则使用配置中的模型
        :param system_prompt: 系统提示词，包含 input_prompt 和 output_prompt
        :param keep_history: 是否保持历史记录
        """
        try:
            config = self.config_manager.get_config()
            model = model or config.get('model', 'llama2')
            language = config.get('language', 'chinese')
            
            # 更新系统提示词
            if system_prompt:
                self.system_prompt = system_prompt
                
                # 添加语言设置到提示词中
                language_prompt = ""
                if language == 'chinese':
                    language_prompt = "请用中文回复，保持简洁明了的表达。"
                elif language == 'english':
                    language_prompt = "Please reply in English, keep your response concise and clear."
                else:
                    language_prompt = f"Please reply in {language}, keep your response concise and clear."
                
                # 将语言设置添加到输出提示词的开头
                if self.system_prompt.get("output_prompt"):
                    self.system_prompt["output_prompt"] = language_prompt + "\n" + self.system_prompt["output_prompt"]
                else:
                    self.system_prompt["output_prompt"] = language_prompt
            
            # 如果会话不存在或模型变更，创建新会话
            if not self.chat_session or self.chat_session.model != model:
                self.logger.info(f"创建新的聊天会话 - 模型: {model}, 语言: {language}")
                self.chat_session = ChatSession(
                    model=model,
                    keep_history=keep_history,
                    input_prompt=self.system_prompt.get("input_prompt", ""),
                    output_prompt=self.system_prompt.get("output_prompt", "")
                )
            else:
                self.logger.info(f"更新系统提示词 - 语言: {language}")
                self.chat_session.input_prompt = self.system_prompt.get("input_prompt", "")
                self.chat_session.output_prompt = self.system_prompt.get("output_prompt", "")
            
            # 仅在不保持历史记录时清空
            if not keep_history and self.chat_session:
                self.chat_session.history = []
                
        except Exception as e:
            self.logger.error(f"设置聊天会话失败: {e}")
            raise e

    def chat(self, user_input: str, options: dict = None) -> str:
        """
        发送聊天消息并获取回复
        :param user_input: 用户输入的消息
        :param options: 参数字典，包含temperature和num_predict等参数
        :return: AI的回复文本
        """
        if not self.chat_session:
            error_msg = "聊天会话未初始化"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        # 获取当前角色的参数
        config = self.config_manager.get_config()
        current_role = config.get('current_role', '通用助手')
        roles = config.get('roles', [])
        
        # 查找当前角色的配置
        role = next((r for r in roles if r['name'] == current_role), None)
        if not role:
            self.logger.warning(f"未找到角色 {current_role} 的配置，使用默认配置")
            role = next((r for r in roles if r['name'] == '通用助手'), {})
            
        # 使用角色特定的参数，如果没有则使用默认值
        temperature = role.get('temperature', config.get('temperature', 0.7))
        max_tokens = role.get('max_tokens', config.get('max_tokens', 150))
            
        self.logger.info(f"发送聊天请求 - 角色: {current_role}, temperature: {temperature}, max_tokens: {max_tokens}")
        
        try:
            # 如果没有提供options，使用角色配置的参数
            if options is None:
                options = {
                    "num_predict": int(max_tokens),  # 使用 max_tokens 作为输出长度限制
                    "mirostat": 0,
                    "mirostat_eta": float(temperature)
                }
            
            # 确保当前会话使用正确的角色提示词
            if role:
                self.chat_session.input_prompt = role.get('input_prompt', '')
                self.chat_session.output_prompt = role.get('output_prompt', '')
            
            try:
                response = ollama.chat(
                    model=self.chat_session.model,
                    messages=[{"role": "user", "content": user_input}],
                    options=options
                )
                return response['message']['content']
                
            except Exception as e:
                error_msg = str(e).lower()
                if "no such file or directory" in error_msg:
                    return "模型文件未找到。请确保已下载并安装所需的模型。\n\n解决方法：\n1. 运行 'ollama pull 模型名称' 下载模型\n2. 检查模型名称是否正确\n3. 确认模型文件存储位置是否正确"
                elif "connection refused" in error_msg:
                    return "无法连接到Ollama服务。\n\n可能的原因：\n1. Ollama服务未启动\n2. 服务端口被占用\n3. 服务异常退出\n\n解决方法：\n1. 重启Ollama服务\n2. 检查端口11434是否可用\n3. 查看Ollama服务日志"
                elif "out of memory" in error_msg or "resource exhausted" in error_msg or "resource_exhausted" in error_msg:
                    return "系统资源不足。\n\n可能的原因：\n1. 内存不足\n2. GPU显存不足\n\n解决方法：\n1. 关闭其他占用资源的程序\n2. 调小模型参数（如context length）\n3. 使用资源需求较少的模型\n4. 如果使用GPU，尝试切换到CPU模式"
                else:
                    self.logger.error(f"聊天请求失败: {e}")
                    return f"请求失败: {str(e)}\n\n建议：\n1. 检查系统资源使用情况\n2. 查看日志获取详细错误信息\n3. 重启应用后重试"
            
        except Exception as e:
            error_msg = f"文本补全失败: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def clean_response(self, text):
        """清理API响应文本"""
        if not text:
            return text
            
        # 移除所有Markdown格式符号
        text = text.replace('*', '')
        text = text.replace('`', '')
        text = text.replace('#', '')
        text = text.replace('_', '')
        text = text.replace('>', '')
        text = text.replace('•', '')
        text = text.replace('·', '')
        text = text.replace('■', '')
        text = text.replace('□', '')
        text = text.replace('◆', '')
        text = text.replace('◇', '')
        text = text.replace('▲', '')
        text = text.replace('△', '')
        text = text.replace('▼', '')
        text = text.replace('▽', '')
        
        # 移除多余的换行和空格
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text

class ChatSession:
    def __init__(self, model: str, keep_history: bool = True, input_prompt: str = None, output_prompt: str = None):
        """
        初始化聊天会话
        :param model: 模型名称
        :param keep_history: 是否保持历史记录
        :param input_prompt: 输入提示词
        :param output_prompt: 输出提示词
        """
        self.model = model
        self.keep_history = keep_history
        self.history = []
        self.input_prompt = input_prompt
        self.output_prompt = output_prompt
        self.logger = LoggerManager.get_logger()
        
    def chat(self, user_input: str, options: dict = None) -> str:
        """
        发送消息并获取回复
        :param user_input: 用户输入的消息
        :param options: 参数字典，包含temperature和num_predict等参数
        :return: AI的回复文本
        """
        try:
            # 添加用户消息到历史记录
            messages = []
            if self.keep_history:
                messages.extend(self.history)
            messages.append({"role": "user", "content": user_input})
            
            # 如果是新对话，添加系统提示词
            if not self.history:
                if self.input_prompt:
                    messages.insert(0, {"role": "system", "content": self.input_prompt})
                if self.output_prompt:
                    messages.insert(1, {"role": "system", "content": self.output_prompt})
            
            try:
                # 准备参数
                params = {
                    "model": self.model,
                    "messages": messages
                }
                
                # 如果有options，添加到参数中
                if options:
                    params["options"] = options
                
                self.logger.info(f"发送请求 - 模型: {self.model}, 参数: {params}")
                response = ollama.chat(**params)
                
            except Exception as e:
                error_str = str(e).lower()
                if "model not found" in error_str:
                    # 如果模型不存在，尝试使用基础模型
                    base_model = self.model.split(':')[0]
                    self.logger.warning(f"模型未找到，尝试使用基础模型: {base_model}")
                    
                    params["model"] = base_model
                    response = ollama.chat(**params)
                else:
                    # 记录详细的错误信息
                    self.logger.error(f"Ollama API 错误: {str(e)}")
                    self.logger.error(f"请求参数: {params}")
                    raise Exception(f"Ollama API 错误: {str(e)}")

            # 获取回复文本并确保是 UTF-8 编码
            try:
                reply_text = response['message']['content']
                # 尝试将文本编码为 UTF-8
                reply_text = reply_text.encode('utf-8').decode('utf-8')
            except UnicodeEncodeError:
                # 如果编码失败，尝试清理文本
                reply_text = ''.join(char for char in reply_text if ord(char) < 128)
                self.logger.warning("回复包含无法编码的字符，已清理")
            
            # 如果保持历史记录，添加回复到历史
            if self.keep_history:
                self.history.append({"role": "assistant", "content": reply_text})
            
            return reply_text
            
        except Exception as e:
            error_msg = f"聊天请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
