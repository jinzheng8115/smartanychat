import json

class ConfigManager:
    def __init__(self):
        """初始化配置管理器"""
        self.config_file = 'config.json'
        self._language = 'chinese'  # 添加私有变量
        
        # 默认配置
        self.default_config = {
            "apikey": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
            "text_complete_number": 150,
            "temperature": 0.7,
            "keep_history": True,
            "api_type": "OpenAI",
            "language": "chinese",
            "roles": [
                {
                    "name": "通用助手",
                    "description": "一个通用的AI助手",
                    "input_prompt": "你是一个有用的AI助手。你应该：\n1. 提供准确、有帮助的回答\n2. 使用清晰、易懂的语言\n3. 在合适的时候提供例子\n4. 保持专业和友好的态度",
                    "output_prompt": "在回答时请注意：\n1. 不要使用特殊格式符号（如*、#、`等）\n2. 不要使用项目符号（如•、·、■等）\n3. 使用数字序号代替项目符号\n4. 保持文本简洁清晰，避免不必要的装饰",
                    "temperature": 0.7,
                    "text_complete_number": 2000
                },
                {
                    "name": "代码专家",
                    "description": "专注于编程和代码相关的助手",
                    "input_prompt": "你是一个专业的编程专家，精通多种编程语言和软件开发最佳实践。你应该：\n1. 提供准确的技术建议\n2. 解释代码原理和最佳实践\n3. 考虑性能、安全性和可维护性\n4. 推荐合适的设计模式和架构方案",
                    "output_prompt": "在提供代码和建议时请注意：\n1. 不要使用特殊格式符号\n2. 代码示例使用简单缩进\n3. 使用数字序号列举要点\n4. 保持代码整洁，添加必要的注释\n5. 说明代码的关键部分和注意事项",
                    "temperature": 0.3,
                    "text_complete_number": 4000
                },
                {
                    "name": "文案写手",
                    "description": "专注于文字创作的助手",
                    "input_prompt": "你是一个专业的文案写手，擅长各类文字创作和内容优化。你应该：\n1. 使用优美、准确的语言\n2. 根据上下文调整写作风格\n3. 注意文章的结构和逻辑\n4. 确保内容的可读性和吸引力",
                    "output_prompt": "在创作文案时请注意：\n1. 不要使用特殊格式符号，纯文本输出\n2. 不要使用项目符号和装饰性符号\n3. 使用数字序号代替项目符号\n4. 段落之间使用换行分隔\n5. 文案需要进行排版\n6. 保持文本整洁，突出重点",
                    "temperature": 0.9,
                    "text_complete_number": 3000
                }
            ],
            "current_role": "通用助手",
            "api_configs": {
                "OpenAI": {
                    "apikey": "",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-3.5-turbo"
                },
                "OpenAI兼容": {
                    "apikey": "",
                    "base_url": "",
                    "model": ""
                },
                "Ollama": {
                    "apikey": "",
                    "base_url": "http://localhost:11434",
                    "model": "llama2"
                }
            }
        }
        
        # 加载配置
        self.load_config()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 加载基本配置
                self.api_type_value = config.get('api_type', 'OpenAI')
                
                # 从对应的 API 配置中加载详细设置
                api_configs = config.get('api_configs', self.default_config['api_configs'])
                api_config = api_configs.get(self.api_type_value, {})
                
                self.apikey = api_config.get('apikey', config.get('apikey', ''))
                self.base_url = api_config.get('base_url', config.get('base_url', ''))
                self.model = api_config.get('model', config.get('model', ''))
                
                # 加载其他配置
                self.text_complete_number = config.get('text_complete_number', 150)
                self.temperature = float(config.get('temperature', 0.7))
                self.keep_history = config.get('keep_history', True)
                self._language = config.get('language', 'chinese')
                self.roles = config.get('roles', self.default_config['roles'])
                self.current_role = config.get('current_role', '通用助手')
                
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            self.save_config(self.default_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 使用默认配置
            self.__dict__.update(self.default_config)

    def set_default_config(self):
        """设置默认配置"""
        self.apikey = self.default_config['apikey']
        self.base_url = self.default_config['base_url']
        self.model = self.default_config['model']
        self.text_complete_number = self.default_config['text_complete_number']
        self.temperature = self.default_config['temperature']
        self.keep_history = self.default_config['keep_history']
        self.api_type_value = self.default_config['api_type']
        self._language = self.default_config['language']  # 添加语言设置
        self.roles = self.default_config['roles']
        self.current_role = self.default_config['current_role']

    def get_default_roles(self):
        """获取默认角色配置"""
        return self.default_config['roles']

    def get_role_prompt(self, role_name=None):
        """获取指定角色的提示词"""
        if role_name is None:
            role_name = self.current_role
        
        for role in self.roles:
            if role['name'] == role_name:
                # 组合输入和输出提示词
                input_prompt = role.get('input_prompt', '')
                output_prompt = role.get('output_prompt', '')
                return f"{input_prompt}\n\n{output_prompt}"
        return self.roles[0]['input_prompt'] + "\n\n" + self.roles[0]['output_prompt']  # 如果找不到指定角色，返回默认角色的提示词

    def add_role(self, name, description, input_prompt, output_prompt):
        """添加新角色"""
        self.roles.append({
            "name": name,
            "description": description,
            "input_prompt": input_prompt,
            "output_prompt": output_prompt
        })
        self.save_config(self.get_config())

    def update_role(self, name, description=None, input_prompt=None, output_prompt=None):
        """更新现有角色"""
        for role in self.roles:
            if role['name'] == name:
                if description is not None:
                    role['description'] = description
                if input_prompt is not None:
                    role['input_prompt'] = input_prompt
                if output_prompt is not None:
                    role['output_prompt'] = output_prompt
                self.save_config(self.get_config())
                return True
        return False

    def delete_role(self, name):
        """删除角色"""
        if name == "通用助手":  # 防止删除默认角色
            return False
        
        for i, role in enumerate(self.roles):
            if role['name'] == name:
                del self.roles[i]
                if self.current_role == name:
                    self.current_role = "通用助手"
                self.save_config(self.get_config())
                return True
        return False

    def set_current_role(self, role_name):
        """设置当前角色"""
        for role in self.roles:
            if role['name'] == role_name:
                self.current_role = role_name
                self.save_config(self.get_config())
                return True
        return False

    def save_config(self, config):
        """保存配置到文件"""
        try:
            # 确保 api_configs 存在
            if 'api_configs' not in config:
                current_config = self.get_config()
                config['api_configs'] = current_config.get('api_configs', self.default_config['api_configs'])
            
            # 更新当前 API 类型的配置
            api_type = config['api_type']
            config['api_configs'][api_type] = {
                'apikey': config['apikey'],
                'base_url': config['base_url'],
                'model': config['model']
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            # 更新内部状态
            self.load_config()
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            raise

    def get_config(self):
        """获取当前配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return dict(self.default_config)

    def get_api_config(self, api_type):
        """获取指定API类型的配置"""
        config = self.get_config()
        api_configs = config.get('api_configs', self.default_config['api_configs'])
        return api_configs.get(api_type, {})

    def save_api_config(self, api_type, apikey, base_url, model):
        """保存指定API类型的配置"""
        config = self.get_config()
        if 'api_configs' not in config:
            config['api_configs'] = self.default_config['api_configs']
        
        config['api_configs'][api_type] = {
            "apikey": apikey,
            "base_url": base_url,
            "model": model
        }
        
        self.save_config(config)

    @property
    def language(self):
        """获取语言设置"""
        return self._language

    @language.setter
    def language(self, value):
        """设置语言"""
        self._language = value
