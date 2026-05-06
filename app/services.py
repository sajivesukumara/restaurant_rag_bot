from vectordb.vector_store import query_items
from llm.local_llm import local_generate
from llm.cloud_llm import cloud_generate

def query_menu(user_query: str, use_cloud: bool = True):
    # Step 1: Retrieve relevant items
    results = query_items(user_query)
    if not results.matches:
        return "No matching menu items found."

    context = "\n".join([str(r.metadata) for r in results.matches])

    # Step 2: Route based on flag
    if use_cloud:
        return cloud_generate(user_query, context)
    else:
        return local_generate(user_query, context)
      
