from __future__ import print_function
from botocore.exceptions import ClientError, ParamValidationError
import subprocess
import logging
import os
import boto3
import json
from os import path, makedirs
import urllib3
import time
import traceback
from zipfile import ZipFile

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.resource('s3') # assumes credentials & configuration are handled outside python in lambda permission

def lambda_handler(event, context):
    try:
        print(event)
        if event['RequestType'] == "Delete":
            # dont do any of this if this is not a Delete stack request
            stackName = os.environ['Stackname']
            print(stackName)
            logger.info('Going to delete stack: {}'.format(stackName))
            response = delete_cloudformation_stack(stackName)
            if response:
                send(event, context, SUCCESS, {})
            else:
                send(event, context, FAILED, {})
        if event['RequestType'] == "Create" or event['RequestType'] == "Update":
            LatestStackVersion = os.environ['LatestStackVersion']
            #print(LatestStackVersion)
            DeveloperPortalSourceBucket=os.environ['DeveloperPortalSourceBucket']
            #print(DeveloperPortalSourceBucket)
            LAMBDA_S3=os.environ['LAMBDA_S3BucketName']
            #print(LAMBDA_S3)
            DEVPORTAL_StackName=os.environ['Stackname']
            #print(DEVPORTAL_StackName)
            DEVPORTAL_SiteS3BucketName=os.environ['DevPortalSiteS3BucketName']
            #print(DEVPORTAL_SiteS3BucketName)
            DEVPORTAL_ArtifactsS3BucketName=os.environ['ArtifactsS3BucketName']
            #print(DEVPORTAL_ArtifactsS3BucketName)
            DEVPORTAL_AccountRegistrationMode=os.environ['AccountRegistrationMode']
            #print(DEVPORTAL_AccountRegistrationMode)
            DEVPORTAL_CognitoDomainNameOrPrefix=os.environ['CognitoDomainNameOrPrefix']
            #print(DEVPORTAL_CognitoDomainNameOrPrefix)
            DEVPORTAL_StaticAssetRebuildMode_Input=os.environ['StaticAssetRebuildMode']
            #print(DEVPORTAL_StaticAssetRebuildMode_Input)
            if DEVPORTAL_StaticAssetRebuildMode_Input and DEVPORTAL_StaticAssetRebuildMode_Input.strip():
                DEVPORTAL_StaticAssetRebuildMode=DEVPORTAL_StaticAssetRebuildMode_Input
            else:
                DEVPORTAL_StaticAssetRebuildMode="''"
            #print(DEVPORTAL_StaticAssetRebuildMode)
            #print(DEVPORTAL_StaticAssetRebuildMode)
            DEVPORTAL_StaticAssetRebuildToken=os.environ['StaticAssetRebuildToken']
            #print(DEVPORTAL_StaticAssetRebuildToke)
            DEVPORTAL_DevPortalCustomersTableName=os.environ['DevPortalCustomersTableName']
            #print(DEVPORTAL_DevPortalCustomersTableName)
            DEVPORTAL_DevPortalPreLoginAccountsTableName=os.environ['DevPortalPreLoginAccountsTableName']
            #print(DEVPORTAL_DevPortalPreLoginAccountsTableName)
            DEVPORTAL_DevPortalAdminEmail_Input=os.environ['DevPortalAdminEmail']
            if DEVPORTAL_DevPortalAdminEmail_Input and DEVPORTAL_DevPortalAdminEmail_Input.strip():
                DEVPORTAL_DevPortalAdminEmail=DEVPORTAL_DevPortalAdminEmail_Input
            else:
                DEVPORTAL_DevPortalAdminEmail="''"
            #print(DEVPORTAL_DevPortalAdminEmail)
            DEVPORTAL_DevPortalFeedbackTableName=os.environ['DevPortalFeedbackTableName']
            #print(DEVPORTAL_DevPortalFeedbackTableName)
            DEVPORTAL_CognitoIdentityPoolName=os.environ['CognitoIdentityPoolName']
            #print(DEVPORTAL_CognitoIdentityPoolName)
            DEVPORTAL_CustomDomainName_Input=os.environ['CustomDomainName']
            if DEVPORTAL_CustomDomainName_Input and DEVPORTAL_CustomDomainName_Input.strip():
                DEVPORTAL_CustomDomainName=DEVPORTAL_CustomDomainName_Input
            else:
                DEVPORTAL_CustomDomainName="''"
            #print(DEVPORTAL_CustomDomainName)
            DEVPORTAL_CustomDomainNameAcmCertArn_Input=os.environ['CustomDomainNameAcmCertArn']
            if DEVPORTAL_CustomDomainNameAcmCertArn_Input and DEVPORTAL_CustomDomainNameAcmCertArn_Input.strip():
                DEVPORTAL_CustomDomainNameAcmCertArn=DEVPORTAL_CustomDomainNameAcmCertArn_Input
            else:
                DEVPORTAL_CustomDomainNameAcmCertArn="''"
            #print(DEVPORTAL_CustomDomainNameAcmCertArn)
            DEVPORTAL_UseRoute53Nameservers=os.environ['UseRoute53Nameservers']
            #print(DEVPORTAL_UseRoute53Nameservers)

            #BucketKey = "infrastructure/"+LatestStackVersion+"/aws-api-gateway-developer-portal"
            BucketKey = "infrastructure/"+LatestStackVersion+"/developerportal"
            #print(BucketKey)
            ## down developer package from s3
            download_s3_folder(DeveloperPortalSourceBucket, BucketKey, local_dir="/tmp")

            with ZipFile('/tmp/developerportal.zip', 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall('/tmp')
    
            packdev= subprocess.Popen(['/opt/sam', 'package', '--template-file', '/tmp/cloudformation/template.yaml', '--output-template-file', '/tmp/cloudformation/packaged.yaml', '--s3-bucket', LAMBDA_S3])
            stdout, stderr = packdev.communicate()

            deploydev= subprocess.Popen(['/opt/sam', 'deploy', '--template-file', '/tmp/cloudformation/packaged.yaml', '--stack-name', DEVPORTAL_StackName, '--s3-bucket', LAMBDA_S3, '--capabilities','CAPABILITY_NAMED_IAM',
                                        '--parameter-overrides', 'DevPortalSiteS3BucketName={0}'.format(DEVPORTAL_SiteS3BucketName), 'ArtifactsS3BucketName={0}'.format(DEVPORTAL_ArtifactsS3BucketName),
                                        'CognitoDomainNameOrPrefix={0}'.format(DEVPORTAL_CognitoDomainNameOrPrefix), 'StaticAssetRebuildMode={0}'.format(DEVPORTAL_StaticAssetRebuildMode),
                                        'StaticAssetRebuildToken={0}'.format(DEVPORTAL_StaticAssetRebuildToken), 'DevPortalCustomersTableName={0}'.format(DEVPORTAL_DevPortalCustomersTableName),
                                        'DevPortalPreLoginAccountsTableName={0}'.format(DEVPORTAL_DevPortalPreLoginAccountsTableName), 'DevPortalAdminEmail={0}'.format(DEVPORTAL_DevPortalAdminEmail),
                                        'DevPortalFeedbackTableName={0}'.format(DEVPORTAL_DevPortalFeedbackTableName), 'CognitoIdentityPoolName={0}'.format(DEVPORTAL_CognitoIdentityPoolName),
                                        'AccountRegistrationMode={0}'.format(DEVPORTAL_AccountRegistrationMode), 'CustomDomainName={0}'.format(DEVPORTAL_CustomDomainName),
                                        'CustomDomainNameAcmCertArn={0}'.format(DEVPORTAL_CustomDomainNameAcmCertArn), 'UseRoute53Nameservers={0}'.format(DEVPORTAL_UseRoute53Nameservers)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = deploydev.communicate()
            print(stdout)
            if deploydev.returncode == 0:
                print("Deploy Developer Portal Success!")
                #update_customizatin(DEVPORTAL_ArtifactsS3BucketName)
                send(event, context, SUCCESS, {})
            else:
                print(stderr)
                send(event, context, FAILED, {})
    except Exception as e:
        logger.error("Exception: {}".format(e))
        traceback.print_exc()
        print(str(e))
        send(event, context, FAILED, {})

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, reason=None):
    responseUrl = event['ResponseURL']
    print(responseUrl)
    responseBody = {
        'Status' : responseStatus,
        'Reason' : reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
        'PhysicalResourceId' : physicalResourceId or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : noEcho,
        'Data' : responseData
    }
    json_responseBody = json.dumps(responseBody)
    print("Response body:")
    print(json_responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
        print("Status code:", response.status)
    except Exception as e:
        print("send(..) failed executing http.request(..):", e)

def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    """
    Download the contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            #os.makedirs(os.path.dirname(target), 0o777)
            oldmask = os.umask(000)
            os.makedirs(os.path.dirname(target), 0o777)
            os.umask(oldmask)
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

def update_customizatin(bucketName, region=None):
    client = get_aws_service_client(service_name='s3', region=region)
    try:
        response1 = client.upload_file("/tmp/dev-portal/public/custom-content/nav-logo.png", bucketName, "custom-content/nav-logo.png", ExtraArgs={'ACL': 'public-read'})
        response2 = client.upload_file("/tmp/dev-portal/public/custom-content/api-logos/default.png", bucketName, "custom-content/api-logos/default.png", ExtraArgs={'ACL': 'public-read'})
        response3 = client.upload_file("/tmp/dev-portal/public/custom-content/content-fragments/Home.md", bucketName, "custom-content/content-fragments/Home.md", ExtraArgs={'ACL': 'public-read'})
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_aws_service_client(service_name, region=None):
    client = None
    if region is None:
        client = boto3.client(service_name)
    else:
        client = boto3.client(service_name, region_name=region)
    return client

def delete_cloudformation_stack(stack_name, region=None, retries=3):
    client = get_aws_service_client(service_name='cloudformation', region=region)
    client.delete_stack(StackName=stack_name)
    waiter = client.get_waiter('stack_delete_complete')
    try:
        waiter.wait(StackName=stack_name)
    except Exception as e:
        response = client.describe_stack_events(StackName=stack_name)
        for stack_event in response.get('StackEvents'):
            logger.error('{}: {}'.format(
                stack_event.get('ResourceStatus'),
                stack_event.get('ResourceStatusReason'),
            ))
        raise e
    logger.info('Finished ensure deleted: {}'.format(stack_name))
    return True
