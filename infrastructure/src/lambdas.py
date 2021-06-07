import json
from typing import List

from pulumi_aws.ec2 import security_group

from vpc import main, subnet1, subnet2, security_group
from sqs import sqs1
from db import dynamodb_table1

import pulumi
from pulumi_aws import lambda_, iam


iam_role_1 = iam.Role(
    f"role1",
    name=f"role1",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}
            ],
        }
    ),
)


iam.RolePolicy(
    f"policy1",
    name=f"policy1",
    role=iam_role_1.id,
    policy={
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "logs:CreateLogGroup", "Resource": f"arn:aws:logs:*"},
                {
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                    "Resource": [f"arn:aws:logs:*:*:log-group:/aws/lambda/*:*"],
                },
                {
                    "Action": [
                        "ec2:CreateNetworkInterface",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DeleteNetworkInterface",
                    ],
                    "Resource": "*",
                    "Effect": "Allow",
                },
                {
                    "Action": [
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        "sqs:GetQueueUrl",
                        "sqs:SendMessage",
                    ],
                    "Resource": f"arn:aws:sqs:*",
                    "Effect": "Allow",
                },

            ],
        }
    )




lambda1 = lambda_.Function(
    f"lambda1",
    name=f"lambda1",
    handler="app.lambda_handler",
    code=pulumi.asset.FileArchive("simple_lambda"),
    role=iam_role_1.arn,
    runtime="python3.8",
    memory_size=128,
    timeout=10,
    vpc_config={
        "subnet_ids": [subnet1.id],
        "security_group_ids": [security_group.id],
    }
)

sqs_mapping = lambda_.EventSourceMapping(
    "sqs1-lambda-mapping",
    event_source_arn=sqs1.arn,
    function_name=lambda1.name,
)




iam_role_2 = iam.Role(
    f"role2",
    name=f"role2",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}
            ],
        }
    ),
)


iam.RolePolicy(
    f"policy2",
    name=f"policy2",
    role=iam_role_2.id,
    policy={
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "logs:CreateLogGroup", "Resource": f"arn:aws:logs:*"},
                {
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                    "Resource": [f"arn:aws:logs:*:*:log-group:/aws/lambda/*:*"],
                },
                {
                    "Action": [
                        "ec2:CreateNetworkInterface",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DeleteNetworkInterface",
                    ],
                    "Resource": "*",
                    "Effect": "Allow",
                },
                {
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGet*",
                "dynamodb:DescribeStream",
                "dynamodb:DescribeTable",
                "dynamodb:Get*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:BatchWrite*",
                "dynamodb:CreateTable",
                "dynamodb:Delete*",
                "dynamodb:Update*",
                "dynamodb:PutItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:*",
            ]
        }


            ],
        }
    )




lambda2 = lambda_.Function(
    f"lambda2",
    name=f"lambda2",
    handler="app.lambda_handler",
    code=pulumi.asset.FileArchive("simple_lambda"),
    role=iam_role_2.arn,
    runtime="python3.8",
    memory_size=128,
    timeout=10,
    vpc_config={
        "subnet_ids": [subnet2.id],
        "security_group_ids": [security_group.id],
    }
)

dynamodb_mapping = lambda_.EventSourceMapping(
    "dynamodb-lambda-mapping",
    event_source_arn=dynamodb_table1.stream_arn,
    function_name=lambda2.name,
    starting_position="LATEST"
)

