from string import Template


def system(data_source: str) -> str:
    prompt_template = Template("""
Write a concise data driven summary of the response in markdown.
The <response></response> tags contain OCSF information from a $data_source query
Do not include the criteria tags, response tags or filler words.
Do not add opinions or make assumptions.
    """)
    prompt = prompt_template.substitute(
        data_source=data_source)
    return prompt


def system1(data_source: str) -> str:
    prompt_template = Template("""
The <response></response> tags contain OCSF information from a $data_source query
First check if the response is related to the criteria in <search_criteria></search_criteria> in the context of $data_source.
If the response is unrelated to the criteria then respond with the appropriate markdown message between <markdown></markdown> tags.
Otherwise if the response is related to the criteria write a report with the relevant data points between <markdown></markdown> tags. 
Do not include the criteria tags, response tags or filler words.
    """)
    prompt = prompt_template.substitute(
        data_source=data_source)
    return prompt


def user(user_input: str, response: str) -> str:
    prompt_template = Template("""
<user_input>
$user_input
</user_input>                               

<response>
$response
</response>
    """)
    prompt = prompt_template.substitute(user_input=user_input, response=response)
    return prompt
