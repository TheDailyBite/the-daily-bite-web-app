import json

import boto3
import requests
from botocore.exceptions import ClientError
from news_aggregator_data_access_layer.config import LOCAL_TESTING, REGION_NAME

from the_daily_bite_web_app.exceptions import InvokeFunctionException
from the_daily_bite_web_app.utils.telemetry import setup_logger

logger = setup_logger(__name__)


def process_lambda_response(function_name: str, response: dict) -> dict:
    """
    Processes a response from a Lambda function invocation.

    :param response: The response from the function invocation.
    :return: The response from the function invocation.
    """
    if response["statusCode"] == 500:
        raise RuntimeError(
            f"{function_name} returned status code {response['statusCode']}. Body: {response['body']}"
        )
    return response


def invoke_function(
    function_name: str, function_params: dict, function_url: str = "", get_log: bool = False
) -> dict:
    """
    Invokes a Lambda function.

    :param function_name: The name of the function to invoke.
    :param function_params: The parameters of the function as a dict. This dict
                            is serialized to JSON before it is sent to Lambda.
    :param get_log: When true, the last 4 KB of the execution log are included in
                    the response.
    :return: The response from the function invocation.
    """
    try:
        logger.info(f"Invoking function {function_name} with params {function_params}")
        if not LOCAL_TESTING:
            lambda_client = boto3.client("lambda", region_name=REGION_NAME)
            response = lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params),
                LogType="Tail" if get_log else "None",
            )
            if response["StatusCode"] != 200:
                raise RuntimeError(
                    "%s returned status code %d." % (function_name, response["StatusCode"])
                )
            processed_response = json.loads(response["Payload"].read())
            return process_lambda_response(function_name, processed_response)
        else:
            url = f"{function_url}/2015-03-31/functions/function/invocations"
            logger.info(
                f"Invoking function in local testing at url {url} with params {function_params}"
            )
            response = requests.post(
                url,
                json=function_params,
                timeout=30,
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"{function_name} returned status code {response.status_code}. Response text {response.text}."
                )
            processed_response = response.json()
            return process_lambda_response(function_name, processed_response)
    except ClientError as e:
        logger.error(f"Couldn't invoke function {function_name}. Error: {e}")
        raise InvokeFunctionException(function_name)
    except Exception as e:
        logger.error(f"Couldn't invoke function {function_name}. Error: {e}")
        raise InvokeFunctionException(function_name)
    return processed_response
