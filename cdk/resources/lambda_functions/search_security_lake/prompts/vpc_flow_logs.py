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
- cloud.zone (text)
- cloud.zone.keyword (text)
- severity (text): Unknown|Informational|Low|Medium|High|Critical|Fatal|Other
- action (text): Allowed|Denied
- connection_info.direction (text): "Inbound" or "Outbound"
- connection_info.direction.keyword (text): "Inbound" or "Outbound"
- connection_info.protocol_num (long): Protocol number
- dst_endpoint.instance_uid (text)
- dst_endpoint.instance_uid.keyword (text)
- dst_endpoint.interface_uid (text)
- dst_endpoint.interface_uid.keyword (text)
- dst_endpoint.ip (text)
- dst_endpoint.ip.keyword (text)
- dst_endpoint.port (long)
- dst_endpoint.subnet_uid (text)
- dst_endpoint.subnet_uid.keyword (text)
- dst_endpoint.vpc_uid (text)
- dst_endpoint.vpc_uid.keyword (text)
- src_endpoint.instance_uid (text)
- src_endpoint.instance_uid.keyword (text)
- src_endpoint.interface_uid (text)
- src_endpoint.interface_uid.keyword (text)
- src_endpoint.ip (text)
- src_endpoint.ip.keyword (text)
- src_endpoint.port (long)
- src_endpoint.subnet_uid (text)
- src_endpoint.subnet_uid.keyword (text)
- src_endpoint.vpc_uid (text)
- src_endpoint.vpc_uid.keyword (text)
- traffic.bytes (long)
- traffic.packets (long)
                               
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
