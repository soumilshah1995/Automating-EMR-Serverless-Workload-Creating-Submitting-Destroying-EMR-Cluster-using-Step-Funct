# Automating EMR Serverless  Workload | Creating| Submitting | Destroying EMR Cluster using Step Function

<img width="204" alt="12121" src="https://user-images.githubusercontent.com/39345855/220208798-27728701-cafb-41e4-bde7-43681d07f08a.PNG">


Automating Big Data Workload

* Creating EMR cluster on Fly based on Request
* Start EMR Server less Application
* Submitting Job and Waiting for Callback from EMR Job
* Stop the EMR Server less Application
* Delete Cluster


This is almost similar when you have to develop a data platform. Customer can choose Spark Worker and all other details behind the scene Step function creates cluster spin up resources and submits job and delete and destroy the resources

# Steps
## Step 1: Create Step function 
```
{
  "Comment": "A description of my state machine",
  "StartAt": "Create New EMR Application",
  "States": {
    "Create New EMR Application": {
      "Type": "Task",
      "ResultPath": "$.CreateEMRCluster",
      "Next": "Start EMR Serverless Application",
      "Parameters": {
        "Architecture": "X86_64",
        "ClientToken.$":"States.UUID()",
        "ReleaseLabel.$": "$.emr_cluster.ReleaseLabel",
        "Type.$": "$.emr_cluster.Type",
        "Name": "datateam",
        "NetworkConfiguration": {
          "SecurityGroupIds": [ "sg-0f82bcb99a2878231" ],
          "SubnetIds": [ "subnet-05551ec8e1006b370","subnet-03576afd62b50a982" ]
        }
      },
      "Resource": "arn:aws:states:::aws-sdk:emrserverless:createApplication"
    },
    "Start EMR Serverless Application": {
      "Type": "Task",
      "ResultPath": "$.StartEMRApplication",
      "Next": "Start EMR Job wait for CallBack",
      "Parameters": {
        "ApplicationId.$": "$.CreateEMRCluster.ApplicationId"
      },
      "Resource": "arn:aws:states:::aws-sdk:emrserverless:startApplication"
    },
    "Start EMR Job wait for CallBack": {
      "Type": "Task",
      "ResultPath": "$.WaitForCallBack",
      "Catch":[
        {
          "ErrorEquals":[
            "States.TaskFailed"
          ],
          "Next":"wait_2_minutes"
        },
        {
          "ErrorEquals":[
            "States.ALL"
          ],
          "Next":"wait_2_minutes"
        }
      ],
      "Parameters": {
        "ApplicationId.$": "$.CreateEMRCluster.ApplicationId",
        "ClientToken.$": "States.UUID()",
        "ExecutionRoleArn.$": "$.ExecutionArn",
        "JobDriver": {
          "SparkSubmit": {
            "EntryPoint.$": "$.ScriptPath",
            "EntryPointArguments.$":  "States.Array($$.Task.Token)",
            "SparkSubmitParameters.$": "$.SparkSubmitParameters"
          }
        },
        "Name.$": "$.JobName"
      },
      "Resource": "arn:aws:states:::aws-sdk:emrserverless:startJobRun.waitForTaskToken",
      "Next": "wait_2_minutes"
    },
    "wait_2_minutes": {
      "Type": "Wait",
      "Seconds": 140,
      "Next": "Stop EMR Serverless Application"
    },
    "Stop EMR Serverless Application": {
      "ResultPath": "$.StopApplication",
      "Type": "Task",
      "Next": "Wait for Application to Stop",
      "Resource": "arn:aws:states:::aws-sdk:emrserverless:stopApplication",
      "Parameters": {
        "ApplicationId.$":  "$.CreateEMRCluster.ApplicationId"
      }
    },
    "Wait for Application to Stop": {
      "Type": "Wait",
      "Seconds": 140,
      "Next": "Delete EMR Serverless Application"
    },
    "Delete EMR Serverless Application": {
      "Type": "Task",
      "ResultPath": "$.DeleteEMRJob",
      "End": true,
      "Parameters": {
        "ApplicationId.$": "$.CreateEMRCluster.ApplicationId"
      },
      "Resource": "arn:aws:states:::aws-sdk:emrserverless:deleteApplication"
    }
  }
}
```

## Step 2: Payload to Step function 

```
{

  "ScriptPath": "s3://XXX/hudi-cow.py",
  "SparkSubmitParameters": "--conf spark.archives=s3://XXXX/python-packages/pyspark_venv.tar.gz#environment --conf spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON=./environment/bin/python --conf spark.emr-serverless.driverEnv.PYSPARK_PYTHON=./environment/bin/python --conf spark.executorEnv.PYSPARK_PYTHON=./environment/bin/python --conf spark.hadoop.hive.metastore.client.factory.class=com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory --conf spark.sql.hive.convertMetastoreParquet=false --conf spark.serializer=org.apache.spark.serializer.KryoSerializer",
  "ExecutionTime": 600,
  "JobName": "mytest",
  "ExecutionArn": "arn:aws:iam::XXXX:role/EMRServerlessS3RuntimeRole",
  "emr_cluster": {
    "architecture": "X86_64",
    "name": "datateam",
    "networkConfiguration": {
      "securityGroupIds": [ "sg-XXXXXX8231" ],
      "subnetIds": [ "subnet-XXXXX6b370","subnet-XXXXXX0a982" ]
    },
    "ReleaseLabel": "emr-6.8.0",
    "Type": "Spark"
  }
}

```

