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
- observables.value (text): Can contain AWS ARNs or IP Addresses
- observables.value.keyword (text)
- unmapped.FindingProviderFields.Severity.Label (text): Unknown|Informational|Low|Medium|High|Critical|Fatal|Other
- unmapped.FindingProviderFields.Severity.Label.keyword (text)
- unmapped.FindingProviderFields.Types[] (text)
- unmapped.FindingProviderFields.Types[].keyword (text)
- unmapped.ProductFields.aws/securityhub/ProductName (text)
- unmapped.ProductFields.aws/securityhub/ProductName.keyword (text)
- unmapped.WorkflowState (text): Resolved|New|Suppressed|Notified
- unmapped.WorkflowState.keyword (text)
- unmapped.AwsAccountName (text)
- unmapped.AwsAccountName.keyword (text)
- unmapped.ProductFields.ControlId (text)
- unmapped.ProductFields.ControlId.keyword (text)
- unmapped.Compliance.Status (text): PASSED|FAILED
- unmapped.Compliance.Status.keyword (text)
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
