# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=unused-variable

import os
import logging
import json
import azure.functions as func

from msrestazure.azure_active_directory import MSIAuthentication
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

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

    # set variables
    operation = req_body['operation']
    group = req_body['context']['resourceGroupName']
    resource = req_body['context']['resourceName']
    bigiq_address = os.environ['BIGIQ_ADDRESS']
    bigiq_username = os.environ['BIGIQ_USERNAME'] 
    bigiq_license_pool = os.environ['BIGIQ_LICENSE_POOL']
    bigiq_license_sku = os.environ['BIGIQ_LICENSE_SKU']
    bigiq_license_unit = os.environ['BIGIQ_LICENSE_UNIT']


    # get vmss instance ip addresses
    # Create MSI Authentication
    credentials = MSIAuthentication()

    # Create a Subscription Client
    subscription_client = SubscriptionClient(credentials)
    subscription = next(subscription_client.subscriptions.list())
    subscription_id = subscription.subscription_id

    # Create Management clients
    resourceClient = ResourceManagementClient(credentials, subscription_id)
    computeClient = ComputeManagementClient(credentials, subscription_id)
    networkClient = NetworkManagementClient(credentials, subscription_id)

    # Create a dictionary of instances
    # We may not be able to get NIC information when scaling out
    instances = []
    vmss = computeClient.virtual_machine_scale_set_vms.list(group, resource)
    for item in vmss:
        instance_view = computeClient.virtual_machine_scale_set_vms.get_instance_view(group, resource, item.instance_id)
        nic = resourceClient.resources.get_by_id(
            item.network_profile.network_interfaces[0].id,
            api_version='2017-12-01')
        ip_reference = nic.properties['ipConfigurations'][0]['properties']

        instances.append({
            'instanceName': item.name, 
            'instanceId': item.instance_id, 
            'powerState': instance_view.statuses[1].code.split("/")[1], 
            'provisioningState': ip_reference['provisioningState'], 
            'privateIp': ip_reference['privateIPAddress'], 
            'macAddress': nic.properties['macAddress']})

    logging.info("Instances: " + str(instances))


    # # get license bigiq assignments
    # # create management client
    # mgmt_client = ManagementClient(
    #     os.environ['BIGIQ_ADDRESS'],
    #     user=os.environ['BIGIQ_USERNAME'],
    #     password=os.environ['BIGIQ_PASSWORD'])

    # # create assignment client, member management client
    # assignment_client = AssignmentClient(mgmt_client)
    # member_mgmt_client = MemberManagementClient(mgmt_client)

    # # list assignments
    # assignments = assignment_client.list()

    # # get address assignment - there should only be one
    # assignments = assignments['items']
    # assignment = assignments[0]

    # if not assignment:
    #     raise Exception('Unable to locate assignment from BIG-IQ assignments')
    
    # logging.info('Assignment: ' + str(assignment))
    # logging.info('Address: ' + assignment['deviceAddress'])
    # logging.info('MAC: ' + assignment['macAddress'])

    # # perform revoke - unreachable device
    # response = member_mgmt_client.create(
    #     config={
    #         'licensePoolName': bigiq_license_pool,
    #         'command': 'revoke',
    #         'address': assignment['deviceAddress'],
    #         'assignmentType': 'UNREACHABLE',
    #         'macAddress': assignment['macAddress']
    #     }
    # )


    # format response
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

    if response:
        return func.HttpResponse(json.dumps(response))
    else:
        return func.HttpResponse(
             "Please pass an operation on the query string or in the request body",
             status_code=400
        )
