import sys
print(sys.path)

try:
    import langchain
    print(f"langchain: {langchain.__file__}")
except ImportError as e:
    print(f"Import langchain failed: {e}")

try:
    import langchain_community
    print(f"langchain_community: {langchain_community.__file__}")
except ImportError as e:
    print(f"Import langchain_community failed: {e}")

try:
    from langchain.chains import create_sql_query_chain
    print("Import create_sql_query_chain from langchain.chains successful")
except ImportError as e:
    print(f"Import create_sql_query_chain from langchain.chains failed: {e}")

try:
    from langchain_classic.chains.sql_database.query import create_sql_query_chain
    print("Import create_sql_query_chain from langchain_classic successful")
except ImportError as e:
    print(f"Import create_sql_query_chain from langchain_classic failed: {e}")
