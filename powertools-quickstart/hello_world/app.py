from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
import json
import boto3


logger = Logger(service="APP")
tracer = Tracer(service="APP")
metrics = Metrics(namespace="MyApp", service="APP")
app = APIGatewayRestResolver()


@app.get("/hello/<name>")
@tracer.capture_method
def hello_name(name):
    tracer.put_annotation(key="User", value=name)
    logger.info(f"Request from {name} received")
    metrics.add_metric(name="SuccessfulGreetings", unit=MetricUnit.Count, value=1)
    return {"message": f"hello {name}!"}


@app.get("/hello")
@tracer.capture_method
def hello():
    tracer.put_annotation(key="User", value="unknown")
    logger.info("Request from unknown received")
    metrics.add_metric(name="SuccessfulGreetings", unit=MetricUnit.Count, value=1)
    #return {"message": "hello unknown!"}
    client = boto3.client('s3')
    response = client.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]

    return {
        'statusCode': 200,
        'body': bucket_names
    }
    #for bucket in s3.buckets.all():
    #   print(bucket.name)
    

@tracer.capture_lambda_handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.exception(e)
        raise