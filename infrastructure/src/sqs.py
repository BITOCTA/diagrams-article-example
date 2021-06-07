from pulumi_aws import sqs

sqs1 = sqs.Queue(
    f"sqs1",
    name=f"sqs1"
)

