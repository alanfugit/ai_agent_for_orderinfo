from langchain_ollama import OllamaLLM as Ollama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

from .config import Settings

def get_agent_executor(settings: Settings):
    """
    初始化并返回一个 LangChain SQL Agent Executor。
    """
    # 1. 初始化 LLM #llama3.1:8b
    llm = Ollama(base_url=settings.ollama_base_url, model="deepseek-r1:8b", temperature=0) #llama3.1:8b

    # 2. 连接数据库
    db_uri = f"mysql+mysqlconnector://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"
    db = SQLDatabase.from_uri(
        db_uri,
        # 仅包含我们需要让 Agent 访问的表
        #include_tables=["order", "order_product", "customer"],
        # LangChain 会自动获取表结构信息，但为了更精确，我们将在 Prompt 中提供完整的 CREATE TABLE 语句
    )

    # 3. 创建 SQL Agent
    # --- 更详细的 Prompt 工程 ---
    # 我们将详细的表结构和指令提供给 Agent，以获得更精确的 SQL 生成。
    # 这比默认的 Prompt 或简单的表名列表效果要好得多。
    AGENT_PREFIX = """你是一个 MySQL 专家。给定一个输入问题，请逐步思考并生成一个或多个语法正确的 MySQL 查询来运行，直到找到问题的答案。

**重要格式要求**：你必须严格按照以下 ReAct 格式输出，每行一个部分：

Thought: [你的逐步思考过程]
Action: [要执行的工具名称，例如 'sql_db_query']
Action Input: [工具输入，例如完整的SQL查询]
Observation: [工具执行结果]
... (可以重复 Thought/Action/Action Input/Observation 多次)
Final Answer: [最终答案]

**中文查询处理**：如果问题是中文，先将其翻译为英文数据库操作，然后生成相应的SQL查询。

**强制规则**：
1. 每行必须以 "Thought:", "Action:", "Action Input:", "Observation:" 或 "Final Answer:" 开头
2. 不要在同一行混合多个部分
3. 确保每个Action都有对应的Action Input

你的查询必须遵循以下规则：
- **永远不要**查询表中的所有列（例如 `SELECT * ...`）。必须明确指定你需要的列。
- **永远**用反引号（`）包裹表名和列名，以避免与 SQL 的保留关键字冲突（例如 `SELECT `order_id` FROM `order`;`）。

下面是你需要使用的数据库的详细表结构：

-- 订单表 (`order`)
CREATE TABLE `order` (
 `order_id` int NOT NULL AUTO_INCREMENT,
 `invoice_no` int NOT NULL DEFAULT '0',
 `invoice_prefix` varchar(26) NOT NULL,
 `store_id` int NOT NULL DEFAULT '0',
 `store_name` varchar(64) NOT NULL,
 `store_url` varchar(255) NOT NULL,
 `customer_id` int NOT NULL DEFAULT '0',
 `customer_group_id` int NOT NULL DEFAULT '0',
 `firstname` varchar(32) NOT NULL,
 `lastname` varchar(32) NOT NULL,
 `email` varchar(96) NOT NULL,
 `telephone` varchar(32) NOT NULL,
 `fax` varchar(32) NOT NULL,
 `custom_field` text NOT NULL,
 `payment_firstname` varchar(32) NOT NULL,
 `payment_lastname` varchar(32) NOT NULL,
 `payment_company` varchar(40) NOT NULL,
 `payment_address_1` varchar(150) NOT NULL,
 `payment_address_2` varchar(150) NOT NULL,
 `payment_city` varchar(128) NOT NULL,
 `payment_postcode` varchar(10) NOT NULL,
 `payment_country` varchar(128) NOT NULL,
 `payment_country_id` int NOT NULL,
 `payment_zone` varchar(128) NOT NULL,
 `payment_zone_id` int NOT NULL,
 `payment_address_format` text NOT NULL,
 `payment_custom_field` text NOT NULL,
 `payment_method` varchar(128) NOT NULL,
 `payment_code` varchar(128) NOT NULL,
 `shipping_firstname` varchar(32) NOT NULL,
 `shipping_lastname` varchar(32) NOT NULL,
 `shipping_company` varchar(40) NOT NULL,
 `shipping_address_1` varchar(150) NOT NULL,
 `shipping_address_2` varchar(150) NOT NULL,
 `shipping_city` varchar(128) NOT NULL,
 `shipping_postcode` varchar(10) NOT NULL,
 `shipping_country` varchar(128) NOT NULL,
 `shipping_country_id` int NOT NULL,
 `shipping_zone` varchar(128) NOT NULL,
 `shipping_zone_id` int NOT NULL,
 `shipping_address_format` text NOT NULL,
 `shipping_custom_field` text NOT NULL,
 `shipping_method` varchar(128) NOT NULL,
 `shipping_code` varchar(128) NOT NULL,
 `comment` text NOT NULL,
 `total` decimal(15,4) NOT NULL DEFAULT '0.0000',
 `order_status_id` int NOT NULL DEFAULT '0',
 `affiliate_id` int NOT NULL,
 `commission` decimal(15,4) NOT NULL,
 `marketing_id` int NOT NULL,
 `tracking` varchar(64) NOT NULL,
 `language_id` int NOT NULL,
 `currency_id` int NOT NULL,
 `currency_code` varchar(3) NOT NULL,
 `currency_value` decimal(15,8) NOT NULL DEFAULT '1.00000000',
 `ip` varchar(40) NOT NULL,
 `forwarded_ip` varchar(40) NOT NULL,
 `user_agent` varchar(255) NOT NULL,
 `accept_language` varchar(255) NOT NULL,
 `date_added` datetime NOT NULL,
 `date_modified` datetime NOT NULL,
 PRIMARY KEY (`order_id`)
);

-- 订单产品表 (`order_product`)
CREATE TABLE `order_product` (
 `order_product_id` int NOT NULL AUTO_INCREMENT,
 `order_id` int NOT NULL,
 `product_id` int NOT NULL,
 `name` varchar(255) NOT NULL,
 `model` varchar(64) NOT NULL,
 `quantity` int NOT NULL,
 `price` decimal(15,4) NOT NULL DEFAULT '0.0000',
 `total` decimal(15,4) NOT NULL DEFAULT '0.0000',
 `tax` decimal(15,4) NOT NULL DEFAULT '0.0000',
 `reward` int NOT NULL,
 PRIMARY KEY (`order_product_id`)
);

-- 用户表 (`customer`)
CREATE TABLE `customer` (
 `customer_id` int NOT NULL AUTO_INCREMENT,
 `customer_group_id` int NOT NULL,
 `store_id` int NOT NULL DEFAULT '0',
 `firstname` varchar(50) NOT NULL,
 `lastname` varchar(50) NOT NULL,
 `email` varchar(96) NOT NULL,
 `telephone` varchar(32) NOT NULL,
 `fax` varchar(32) NOT NULL,
 `password` varchar(40) NOT NULL,
 `salt` varchar(9) NOT NULL,
 `cart` text,
 `wishlist` text,
 `newsletter` tinyint(1) NOT NULL DEFAULT '0',
 `address_id` int NOT NULL DEFAULT '0',
 `custom_field` text NOT NULL,
 `ip` varchar(40) NOT NULL,
 `status` tinyint(1) NOT NULL,
 `lastEmpDate` date NOT NULL,
 `approved` tinyint(1) NOT NULL,
 `safe` tinyint(1) NOT NULL,
 `token` varchar(255) NOT NULL,
 `date_added` datetime NOT NULL,
 PRIMARY KEY (`customer_id`)
);

关键关联提示：
- `order.customer_id` 可以与 `customer.customer_id` 关联。
- `order_product.order_id` 可以与 `order.order_id` 关联。
"""
    #3. 创建一个 SQL Agent
    # create_sql_agent 是一个高级工厂函数，它会自动：
    # - 创建一个 SQLDatabaseToolkit，其中包含了查询数据库、列出表、检查表结构等工具。
    # - 创建一个针对 SQL 优化的 Prompt。
    # - 将 LLM、Toolkit 和 Prompt 组合成一个 Agent。
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="zero-shot-react-description", # 这是一个标准的、强大的 Agent 类型
        prefix=AGENT_PREFIX, # 使用我们自定义的、更详细的 Prompt 前缀
        verbose=True, # 设置为 True 可以在控制台看到 Agent 的完整思考过程，非常适合调试
        handle_parsing_errors=True # 关键参数：如果 LLM 的输出格式有问题，Agent 会尝试自行修复
    )

    return agent_executor