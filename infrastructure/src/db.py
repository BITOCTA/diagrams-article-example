from pulumi_aws import dynamodb

dynamodb_table1 = dynamodb.Table("dynamotable1",
    name="dynamotable1",
    attributes=[
        dynamodb.TableAttributeArgs(
            name="Id",
            type="S"
        )
    ],
    hash_key = "Id",
    read_capacity=5,
    write_capacity=5,
    stream_enabled=True,
    stream_view_type="KEYS_ONLY"
)
