from conversational_analytics.memory import search_similar_conversations
import asyncio

user_id = "admin"
query = "What is the net sales in each location?"
limit = 3

past = asyncio.wait_for(
    search_similar_conversations(
        user_id=user_id,
        query=query,
        limit=limit,
    ),
    timeout=5.0,
)

print(past)