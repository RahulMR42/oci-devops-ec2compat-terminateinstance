# oci-load-file-into-adw-python version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
from operator import contains
import os
import json
import oci
import logging

from fdk import response

def read_from_json_file(path):
    try:
        json_file = open(path)
        return (json.load(json_file))
    except Exception as error:
        logging.getLogger().error("Exception while reading json file" + str(error))


class oci_sdk_actions:
    def __init__(self,region):
        self.region = region
        self.signer = oci.auth.signers.get_resource_principals_signer()

    def fetch_ad(self,region_config,aws_region):
        logging.getLogger().info("Inside fetch Ad info function")
        identity_client = oci.identity.IdentityClient(config={'region': self.region}, signer = self.signer)
        oci_compartment_id = region_config[aws_region]['oci_compartment_ocid']
        oci_ad = region_config[aws_region]['oci_ad']
        logging.getLogger().info("Doing pagination query")
        availability_domains = oci.pagination.list_call_get_all_results(
            identity_client.list_availability_domains,oci_compartment_id).data
        logging.getLogger().info(str(availability_domains.keys()))

        

def handler(ctx, data: io.BytesIO=None):
    try:
        body = json.loads(data.getvalue())
        logging.getLogger().info("inputs" + str(body))
        logging.getLogger().info("Invoked function with default  image")
        instance_config = read_from_json_file("/function/instance_config.json")
        region_config =  read_from_json_file("/function/region_config.json")
        shape_config = read_from_json_file("/function/shape_config.json")
        image_config = read_from_json_file("/function/image_config.json")
        subnet_config = read_from_json_file("/function/subnet_config.json")

        aws_region = body['Region']
        aws_image_id = body['image-id']
        aws_instance_type = body['instance-type']
        aws_subnet_id = body['subnet-id']

        oci_region = region_config[aws_region]['oci_region']
        oci_sdk_handler = oci_sdk_actions(oci_region)
        oci_sdk_handler.fetch_ad(region_config,aws_region)

        logging.getLogger().info("ivar"+str(region_config))
        return response.Response(
            ctx, 
            response_data=json.dumps({"status": "Ok"}),
            headers={"Content-Type": "application/json"})
    except Exception as error:
        logging.getLogger().error("Exception" + str(error))
    