import boto3
from botocore.exceptions import ClientError
import datetime
import json
iam_client = boto3.client('iam')


def list_access_key(user, status_filter):
    keydetails = iam_client.list_access_keys(UserName=user)
    key_details = {}
    user_iam_details = []

    # Some users may have 2 access keys.
    for keys in keydetails['AccessKeyMetadata']:
        key_details['UserName'] = keys['UserName']
        key_details['AccessKeyId'] = keys['AccessKeyId']
        key_details['status'] = keys['Status']
        user_iam_details.append(key_details)
        key_details = {}

    return user_iam_details


def time_diff(keycreatedtime):
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now-keycreatedtime
    return diff.days


def create_key(username):
    access_key_metadata = iam_client.create_access_key(UserName=username)
    access_key = access_key_metadata['AccessKey']['AccessKeyId']
    secret_key = access_key_metadata['AccessKey']['SecretAccessKey']
    # secmanagerv=secretmanager.put_secret_value(SecretId=username,SecretString=json_data)
    emailmsg = "New Access Key  "+access_key + \
        " and the Secret Key  "+secret_key+" has been generated."
    ops_sns_topic = 'arn:aws:sns:eu-central-1:AWS-ACCOUNT-NUMBER:SNS-Topic-Name'
    sns_send_report = boto3.client('sns', region_name='eu-central-1')
    sns_send_report.publish(TopicArn=ops_sns_topic, Message=emailmsg,
                            Subject="New Key create for user" + username)


def disable_key(access_key, username):
    try:
        iam_client.update_access_key(
            UserName=username, AccessKeyId=access_key, Status="Inactive")
        print(access_key + " has been disabled.")
    except ClientError as e:
        print("The access key with id %s cannot be found" % access_key)


def delete_key(access_key, username):
    try:
        iam_client.delete_access_key(UserName=username, AccessKeyId=access_key)
        print(access_key + " has been deleted.")
    except ClientError as e:
        print("The access key with id %s cannot be found" % access_key)


def lambda_handler(event, context):
    # details = iam_client.list_users(MaxItems=300)
    # print(details)
    user = event["username"]
    user_iam_details = list_access_key(user=user, status_filter='Active')
    for _ in user_iam_details:
        disable_key(access_key=_['AccessKeyId'], username=_['UserName'])
        delete_key(access_key=_['AccessKeyId'], username=_['UserName'])
        create_key(username=_['UserName'])

    return {
        'statusCode': 200,
        'body': list_access_key(user=user, status_filter='Active')
    }