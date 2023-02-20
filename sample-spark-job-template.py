try:
    import sys
    import os
    from datetime import datetime
    import json
    import boto3
    from pyspark import SparkContext
    from pyspark.sql import SparkSession

    print("All Imports okay")
except Exception as e:
    print("ERROR ", e)

sc = SparkContext()
spark = SparkSession.builder.getOrCreate()


region = 'us-east-1'


client = boto3.client("stepfunctions",
                      aws_access_key_id="XXXX",
                      aws_secret_access_key="XXXX",
                      region_name='us-east-1')


if len(sys.argv) == 1:
    print('no arguments passed')
    sys.exit()

else:
    try:

        """
        SPARK CODE GOES HERE
        """
        tasktoken = json.dumps(sys.argv[1])
        response = client.send_task_success(taskToken=tasktoken, output=tasktoken)
    except Exception as e:
        print("ERROR :{} ".format(e))
        tasktoken = json.dumps(sys.argv[1])
        response = client.send_task_failure(taskToken=tasktoken, output=tasktoken)
        raise Exception(e)
