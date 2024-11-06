from string import Template
import prompts
import prompts.common



def system() -> str:
    prompt_template = Template("""
<available_fields>
- time_dt (date): Timestamp in ISO format
- cloud.account.uid (text): AWS account ID
- cloud.account.uid.keyword (text): AWS account ID
- cloud.region (text)
- cloud.region.keyword (text)
- severity (text): Unknown|Informational|Low|Medium|High|Critical|Fatal|Other
- api.operation (text)
- api.operation.keyword (text)
- api.service (text)
- api.service.keyword (text)
- userIdentity.sessionContext.sessionIssuer.principalId                            
- userIdentity.sessionContext.sessionIssuer.principalId.keyword
- actor.user.credential_uid (text)
- actor.user.credential_uid.keyword (text)
- session.credential_uid (text)
- session.credential_uid.keyword (text)
- src_endpoint.ip (text)
- src_endpoint.ip.keyword (text)
- src_endpoint.domain (text)
- src_endpoint.domain.keyword (text)
- is_mfa: (boolean)
- status: (text): Success|Failure                               
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
