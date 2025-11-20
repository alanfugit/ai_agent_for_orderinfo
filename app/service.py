from langchain_community.utilities import SQLDatabase
from langchain_ollama import OllamaLLM
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from .database import engine
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Database
db = SQLDatabase(engine, include_tables=["order", "order_product", "customer"])

from functools import lru_cache

# Initialize LLM
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
llm = OllamaLLM(model="llama3.1:8b", base_url=OLLAMA_HOST)

# Cache for SQL generation (store up to 100 queries)
@lru_cache(maxsize=100)
def generate_sql_cached(question: str):
    """
    Cached version of the SQL generation step.
    """
    # We need to recreate the chain here or just use the llm directly with the prompt.
    # Since the chain depends on 'db' which might not be pickleable or thread-safe for lru_cache if passed directly,
    # we'll assume 'db' and 'llm' are globals or stable.
    # However, 'create_sql_query_chain' returns a Runnable which might be complex to cache directly if it holds state.
    # A better approach for caching is to cache the *result* of the SQL generation chain.
    
    # Re-defining the prompt here to ensure it's available for the cached function
    query_prompt = PromptTemplate.from_template(
        """You are a MySQL expert. Given an input question, create a syntactically correct {dialect} query to run.

Here are some examples of correct queries:

Question: "How many orders are there?"
SQLQuery: SELECT COUNT(`order_id`) FROM `order`;

Question: "Who has the highest total order amount?"
SQLQuery: SELECT `order`.`firstname`, `order`.`lastname`, SUM(`total`) as `total_amount` FROM `order` GROUP BY `customer_id` ORDER BY `total_amount` DESC LIMIT 1;

Question: "Who has the largest total order amount?"
SQLQuery: SELECT `order`.`firstname`, `order`.`lastname`, SUM(`total`) as `total_amount` FROM `order` GROUP BY `customer_id` ORDER BY `total_amount` DESC LIMIT 1;

Question: "那個人買的產品總價最高？"
SQLQuery: SELECT o.`firstname`, o.`lastname`, SUM(op.`total`) as `total_amount` FROM `order` o JOIN `order_product` op ON o.`order_id` = op.`order_id` GROUP BY o.`customer_id` ORDER BY `total_amount` DESC LIMIT 1;

--------------------------------------------------

Now, answer the following question. Do not provide any explanation or extra text. Just provide the SQL query.

Only use the following tables:
{table_info}

IMPORTANT SCHEMA NOTES:
- Customer information (firstname, lastname, email, telephone) is in the `customer` table
- The `order` table contains firstname and lastname for the order, linked to customer via customer_id
- The `order_product` table contains product details for each order, linked via order_id
- To get customer names with order information, use the firstname/lastname from the `order` table directly (they are already there)
- To get customer contact info, JOIN with the `customer` table using customer_id

Limit the results to {top_k}.

IMPORTANT: You MUST use backticks (`) around ALL table names and column names, especially the `order` table which is a reserved keyword.

Question: {input}
SQLQuery:"""
    )
    
    write_query = create_sql_query_chain(llm, db, prompt=query_prompt)
    return write_query.invoke({"question": question})

def ask_question(session, question: str, summary: bool = True) -> str:
    """
    Uses LangChain to answer a question about the database.
    :param summary: If True, generates a natural language summary. If False, returns the raw data.
    """
    try:
        logger.info(f"Invoking LangChain for question: {question}")
        
        # 1. Generate SQL (Cached)
        generated_query = generate_sql_cached(question)
        
        # 2. Clean SQL
        def clean_sql(query: str) -> str:
            """
            Cleans the generated SQL query to ensure table names are properly quoted using regex.
            """
            import re
            
            # Try to find the start of the SQL query using regex
            match = re.search(r'(?i)(\*\*|#)?\s*SQL\s*Query\s*(\*\*|#)?\s*:', query)
            if match:
                query = query[match.end():]
            
            # Remove markdown formatting if present
            if "```" in query:
                code_match = re.search(r'```(?:sql)?(.*?)```', query, re.DOTALL)
                if code_match:
                    query = code_match.group(1)
                else:
                    query = query.replace("```sql", "").replace("```", "")
            
            # Truncate at SQLResult: or Answer:
            stop_match = re.search(r'(?i)(\*\*|#)?\s*(SQL\s*Result|Answer)\s*(\*\*|#)?\s*:', query)
            if stop_match:
                query = query[:stop_match.start()]
            
            query = query.strip()
            
            # Protect 'ORDER BY'
            query = re.sub(r'(?i)\bORDER\s+BY\b', '###ORDER_BY###', query)
            
            # Regex to add backticks to 'order'
            query = re.sub(r'(?i)\border\b', '`order`', query)
            
            # Restore 'ORDER BY'
            query = query.replace('###ORDER_BY###', 'ORDER BY')
            
            # Ensure we didn't double backtick
            query = query.replace("``order``", "`order`")
            
            return query

        cleaned_query = clean_sql(generated_query)
        logger.info(f"Generated SQL: {generated_query}")
        logger.info(f"Cleaned SQL: {cleaned_query}")
        
        # 3. Execute SQL
        # execute_query = QuerySQLDataBaseTool(db=db)
        # QuerySQLDataBaseTool returns a string, but we want the raw list for formatting.
        # We'll use a custom function to execute the query and return the raw result.
        
        def execute_query_raw(query: str):
            try:
                # Use the database instance to execute the query
                result = db._execute(query, fetch="all")
                # db._execute might return different types depending on the query
                # For SELECT queries with no results, it returns an empty list []
                # For aggregate queries with no matching rows, it might return [(0,)] or similar
                if result is None:
                    return []
                return result
            except Exception as e:
                logger.error(f"Query execution failed: {e}", exc_info=True)
                # Return empty list instead of error string to allow format_result to handle it
                return []

        result = execute_query_raw(cleaned_query)
        logger.info(f"Raw result type: {type(result)}, value: {result}")
        
        # 4. Format Result
        def format_result(x):
            logger.info(f"SQL Result: {x}")
            if isinstance(x, list):
                if not x:
                    return "0"  # Return "0" for empty results
                
                # Check if first element is dict-like (RowMapping)
                first_row = x[0]
                is_dict_like = isinstance(first_row, dict) or hasattr(first_row, 'keys')
                
                # If single row
                if len(x) == 1:
                    if is_dict_like:
                        # Dict-like row (RowMapping)
                        values = list(first_row.values()) if isinstance(first_row, dict) else [first_row[k] for k in first_row.keys()]
                        if len(values) == 1:
                            return str(values[0])
                        return ", ".join([f"{k}: {v}" for k, v in (first_row.items() if isinstance(first_row, dict) else zip(first_row.keys(), values))])
                    else:
                        # Tuple-like row
                        if len(first_row) == 1:
                            return str(first_row[0])
                        return str(first_row)
                
                # Multiple rows
                if is_dict_like:
                    # Check if all rows have single value
                    if all(len(list(row.values() if isinstance(row, dict) else [row[k] for k in row.keys()])) == 1 for row in x):
                        return ", ".join([str(list(row.values() if isinstance(row, dict) else [row[k] for k in row.keys()])[0]) for row in x])
                    # Multiple columns
                    return "\n".join([", ".join([f"{k}: {v}" for k, v in (row.items() if isinstance(row, dict) else zip(row.keys(), [row[k] for k in row.keys()]))]) for row in x])
                else:
                    # Tuple-like rows
                    if all(len(row) == 1 for row in x):
                        return ", ".join([str(row[0]) for row in x])
                    return "\n".join([str(row) for row in x])
            return str(x)
            
        formatted_result = format_result(result)
        
        # 5. Generate Answer (Optional)
        if not summary:
            logger.info("Skipping summary generation.")
            return formatted_result

        answer_prompt = PromptTemplate.from_template(
            """Question: {question}
SQL: {query}
Data: {result}

IMPORTANT: Answer in the SAME LANGUAGE as the question. If the question is in Chinese, answer in Chinese. If in English, answer in English.

Answer the question concisely based on the Data. 
- If the question asks for a count/sum/total and Data is empty or "0", answer with "0" or "總額為0" (in Chinese) or "Total is 0" (in English).
- If Data is empty for other types of questions, say "No data found" or "沒有找到數據" (in Chinese).
Answer: """
        )
        
        chain = (
            RunnablePassthrough.assign(
                question=lambda x: question,
                query=lambda x: cleaned_query,
                result=lambda x: formatted_result
            )
            | answer_prompt
            | llm
            | StrOutputParser()
        )
        
        response = chain.invoke({})
        logger.info(f"LangChain response: {response}")
        
        return response

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        return f"Error: {str(e)}"
