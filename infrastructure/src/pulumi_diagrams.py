import json
from functools import wraps

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.compute import ECS, LambdaFunction


with open(
    "/home/artem/test/diagrams_pulumi_test/infrastructure/src/stack.json"
) as json_file:
    pulumi_stack = json.load(json_file)


def loop_resources(pulumi_stack: dict):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for resource in pulumi_stack["deployment"]["resources"]:
                func(resource, *args, **kwargs)

        return wrapper

    return actual_decorator


connection_nodes = {"dynamodb": Dynamodb, "sqs": SQS}


@loop_resources(pulumi_stack)
def create_connection(resource, lambda_id, lambda_function_node):
    if (
        resource["type"] == "aws:lambda/eventSourceMapping:EventSourceMapping"
        and lambda_id == resource["inputs"]["functionName"]
    ):

        connection_nodes.get(resource["inputs"]["eventSourceArn"].split(":")[2])(
            resource["propertyDependencies"]["eventSourceArn"][0].split("::")[-1]
        ) >> Edge(
            style="dotted", label=resource["urn"].split("::")[-1]
        ) >> lambda_function_node


@loop_resources(pulumi_stack)
def create_lambda_function(resource, subnet_id):
    if (
        resource["type"] == "aws:lambda/function:Function"
        and subnet_id in resource["inputs"]["vpcConfig"]["subnetIds"]
    ):
        lambda_function = LambdaFunction(f"{resource['id']}")
        create_connection(resource["id"], lambda_function)


@loop_resources(pulumi_stack)
def create_subnet(resource):
    if resource["type"] == "aws:ec2/subnet:Subnet":
        with Cluster(f"Subnet {resource['id']}"):
            create_lambda_function(subnet_id=resource["id"])


@loop_resources(pulumi_stack)
def create_vpc(resource):
    if resource["type"] == "aws:ec2/vpc:Vpc":
        with Cluster(f"VPC {resource['id']}"):
            create_subnet()


def create_pulumi_diagram():
    create_vpc()


with Diagram("main diagrams"):
    create_pulumi_diagram()
