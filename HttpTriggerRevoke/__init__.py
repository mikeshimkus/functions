import os
import logging
import json

# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=unused-variable
import azure.functions as func
from f5sdk.bigiq import ManagementClient
from f5sdk.bigiq.licensing import AssignmentClient
from f5sdk.bigiq.licensing.pools import MemberManagementClient
from f5sdk.logger import Logger


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
    except Exception as _e:
        return func.HttpResponse(
            'Exception parsing JSON body: %s' % _e,
            status_code=400
        )

    logging.info('Request body: ' + json.dumps(req_body))

    operation = req_body['operation']
    group = req_body['context']['resourceGroupName']
    resource = req_body['context']['resourceName']
    
    bigiq_address = os.environ['BIGIQ_ADDRESS']
    bigiq_username = os.environ['BIGIQ_USERNAME'] 
    bigiq_license_pool = os.environ['BIGIQ_LICENSE_POOL']
    bigiq_license_sku = os.environ['BIGIQ_LICENSE_SKU']
    bigiq_license_unit = os.environ['BIGIQ_LICENSE_UNIT']

    logging.info('BIG-IQ password: ' + os.environ['BIGIQ_PASSWORD'])

    # get vmss instance ip addresses

    # get license bigiq assignments

    # revoke any licenses for devices that are not in creating or running state
  
    response = {
        'operation': operation,
        'resourceGroup': group,
        'resourceName': resource,
        'bigiqAddress': bigiq_address,
        'bigiqUsername': bigiq_username,
        'bigiqLicensePool': bigiq_license_pool,
        'bigiqLicenseSku': bigiq_license_sku,
        'bigiqLicenseUnit': bigiq_license_unit,
        'bigiqPassword': os.environ['BIGIQ_PASSWORD']
    }

    if operation:
        return func.HttpResponse(json.dumps(response))
    else:
        return func.HttpResponse(
             "Please pass an operation on the query string or in the request body",
             status_code=400
        )
