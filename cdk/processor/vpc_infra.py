from aws_cdk import aws_ec2
from constructs import Construct
from processor.namespace import VPC_STACK_VPC, VPC_STACK_PRIVATE_SUBNET, VPC_STACK_PUBLIC_SUBNET


class VpcInfrastructure(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = aws_ec2.Vpc(
            self, 
            id=VPC_STACK_VPC,
            vpc_name=VPC_STACK_VPC,
            ip_addresses=aws_ec2.IpAddresses.cidr('10.37.0.0/16'),
            max_azs=2,
            nat_gateways=2,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    name=VPC_STACK_PUBLIC_SUBNET,
                    cidr_mask=24,
                    map_public_ip_on_launch=False
                ),
                aws_ec2.SubnetConfiguration(
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name=VPC_STACK_PRIVATE_SUBNET,
                    cidr_mask=24
                )
            ]
        )
        self.vpc = vpc