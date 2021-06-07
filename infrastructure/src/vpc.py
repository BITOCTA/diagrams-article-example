from typing import List
from pulumi_aws import ec2
import pulumi

main = ec2.Vpc.get(resource_name="main", id="vpc-14e22169")

subnet1 = ec2.Subnet.get(resource_name="subnet1", id="subnet-2cb80f4a")
subnet2 = ec2.Subnet.get(resource_name="subnet2", id="subnet-34c1a83a")

security_group = ec2.SecurityGroup.get(resource_name="security_group", id="sg-0361f632")


