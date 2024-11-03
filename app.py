import json
import boto3
import logging
from chalice import Chalice
from chalicelib.src.modules.application.commands.create_incident import CreateIncidenceCommand
from chalicelib.src.seedwork.application.commands import execute_command

app = Chalice(app_name='abcall-pqrs-events-microservice')
app.log.setLevel(logging.DEBUG)

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')

sqs = boto3.client('sqs')
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/044162189377/AbcallPqrs'


# @app.on_sns_message(topic='AbcallPqrsTopic')
@app.on_sqs_message(queue='AbcallPqrs', batch_size=1)
def handle_sqs_message(event):
    app.log.debug("Received message with subject: %s, message: %s",
                  event.subject, event.message)

    for record in event:
        incidence_as_json = json.loads(record.body)

        command = CreateIncidenceCommand(
            title=incidence_as_json["title"],
            type=incidence_as_json["type"],
            description=incidence_as_json["description"],
            date=incidence_as_json["date"],
            user_sub=incidence_as_json["user_sub"],
            ticket_number=incidence_as_json["ticket_number"],
        )
        execute_command(command)

        sqs.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=record.receipt_handle
        )