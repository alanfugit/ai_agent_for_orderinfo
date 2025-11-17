from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    定义应用的所有配置项。
    pydantic-settings 会自动从环境变量或 .env 文件中读取这些值。
    """
    # 数据库配置
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    
    # Ollama 配置
    # 注意：LangChain 的 Ollama 集成需要的是基础 URL，而不是完整的 /api/generate 路径
    ollama_base_url: str = "http://localhost:11434"

    # model_config 用于指定 .env 文件的位置
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')