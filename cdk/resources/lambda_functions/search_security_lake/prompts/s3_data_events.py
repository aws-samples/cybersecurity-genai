from string import Template
import prompts
import prompts.common



def system() -> str:
    prompt_template = Template("""
<available_fields>
- time_dt (date): Timestamp in ISO format
- cloud.region (text)
- cloud.region.keyword (text)
- severity (text): Unknown|Informational|Low|Medium|High|Critical|Fatal|Other
- severity.keyword (text)
- api.request.data.bucketName (text)
- api.request.data.bucketName.keyword (text)
- api.request.data.key (text)
- api.request.data.key.keyword (text)
- api.request.data.Host (text): s3 bucket by url ie. my-bucket.s3.amazonaws.com
- api.request.data.Host.keyword (text)
- api.operation (text): ie. GetObject, PutObject
- api.operation.keyword (text)
- src_endpoint.ip (text)
- src_endpoint.ip.keyword (text)
- src_endpoint.domain (text)
- src_endpoint.domain.keyword (text)
- actor.user.uid (text): AWS ARN of the IAM Role that accessed the bucket
- actor.user.uid.keyword (text)
- actor.user.account.uid (text)
- actor.user.account.uid.keyword (text)
- actor.user.credential_uid (text): AWS IAM Access Key used to access the bucket
- actor.user.credential_uid.keyword (text)
- actor.session.is_mfa (bool)
- actor.session.is_mfa.keyword (bool)
- status (text): Success|Failure
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
