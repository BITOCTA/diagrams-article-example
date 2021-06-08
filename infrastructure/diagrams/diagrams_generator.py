import json
from functools import wraps

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.compute import LambdaFunction


with open(
    "../src/stack.json"
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

nodes_with_connection = []

@loop_resources(pulumi_stack)
def create_connection(resource):
    for node in nodes_with_connection:
        if (
            resource["type"] == "aws:lambda/eventSourceMapping:EventSourceMapping"
            and node[0] == resource["inputs"]["functionName"]
        ):

            connection_nodes.get(resource["inputs"]["eventSourceArn"].split(":")[2])(
                resource["propertyDependencies"]["eventSourceArn"][0].split("::")[-1]
            ) >> Edge(
                style="dotted", label=resource["urn"].split("::")[-1]
            ) >> node[1]


@loop_resources(pulumi_stack)
def create_resource(resource, subnet_id):
    if (
        resource["type"] == "aws:lambda/function:Function"
        and subnet_id in resource["inputs"]["vpcConfig"]["subnetIds"]
    ):
        lambda_function = LambdaFunction(f"{resource['id']}")
        global nodes_with_connection
        nodes_with_connection.append((resource['id'], lambda_function))


@loop_resources(pulumi_stack)
def create_subnet(resource):
    if resource["type"] == "aws:ec2/subnet:Subnet":
        with Cluster(f"Subnet {resource['id']}"):
            create_resource(subnet_id=resource["id"])


@loop_resources(pulumi_stack)
def create_vpc(resource):
    if resource["type"] == "aws:ec2/vpc:Vpc":
        with Cluster(f"VPC {resource['id']}"):
            create_subnet()


def create_pulumi_diagram():
    create_vpc()
    create_connection()


with Diagram("Pulumi stack based diagram"):
    create_pulumi_diagram()
