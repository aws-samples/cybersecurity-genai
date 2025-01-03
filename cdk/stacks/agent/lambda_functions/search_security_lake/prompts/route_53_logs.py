from string import Template
import prompts
import prompts.common



def system() -> str:
    prompt_template = Template("""
<available_fields>
- time_dt (date): Timestamp in ISO format
- cloud.account (text)
- cloud.account.keyword (text)
- cloud.region (text)
- cloud.region.keyword (text)
- severity (text): Unknown|Informational|Low|Medium|High|Critical|Fatal|Other
- severity.keyword (text)
- src_endpoint.vpc_uid (text)
- src_endpoint.vpc_uid.keyword (text)
- src_endpoint.instance_uid (text)
- src_endpoint.instance_uid.keyword (text)
- src_endpoint.ip (text)
- src_endpoint.ip.keyword (text)
- query.hostname (text)
- query.hostname.keyword (text)
- query.type (text)
- query.type.keyword (text)
- answers.rdata (text)
- answers.rdata.keyword (text)
- answers.type (text)
- answers.type.keyword (text)
</available_fields>

<rules>
$common_rules
</rules>
                               
Build a query in response to the search criteria using the avialable_fields following the rules.
    """)
    prompt = prompt_template.substitute(
        common_rules=prompts.common.SYSTEM_PROMPT_RULES
    )
    return prompt


def user(user_input: str) -> str:
    prompt_template = Template("""
    CURRENT_DATE=$current_date
    CURRENT_TIME=$current_time     
    <user_input>$user_input<user_input>""")
    prompt = prompt_template.substitute(
        current_date=prompts.common.get_current_date(),
        current_time=prompts.common.get_current_time(),
        user_input=user_input
    )
    return prompt
