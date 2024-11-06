from datetime import datetime



SYSTEM_PROMPT_RULES = """
- Follow these steps to write an OpenSearch DSL Query.
- Understand the intent of the user_input.
- Understand what each of the available_fields can be used for.
- Do you need a keyword field? Those field names have .keyword at the end.
- If you are going to make a query block what type will it be match, term, multi_match, query_string, etc...
- Full text-search can be performed on text fields without the .keyword in the name.
- To perform partial text searches use multi_match with phrase_prefix with fields": ["*"].
- To perform fuzzy searches use query_string, set fuzziness to auto with fields": ["*"].
- Do you need an aggs block in the query and will it be bucket or metric aggregation?
- Aggregations and Sorting on text fields with .keyword in the name.
- Metric aggregation with sum, min, max or avg can be performed on numeric field types.
- Write the pseudocode for your query first.
- Finally Write the query as JSON between <query></query> tags.
"""


def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_current_time():
    return datetime.now().strftime('%H:%M')
