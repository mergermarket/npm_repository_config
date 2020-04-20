import sys
import boto3
import json
import requests

from botocore.exceptions import ClientError, BotoCoreError
from requests import RequestException
from string import Template
from urllib.parse import urlparse


def get_secrets(secretId):
    client = boto3.client(service_name='secretsmanager')
    get_secret_value_response = client.get_secret_value(SecretId=secretId)
    return get_secret_value_response['SecretString']


def build_npmrc(data, key):
    msg = "registry=${url} \n_auth=""${token}"" \nalways-auth = true \n"
    template = Template(msg)
    return template.substitute(url=data[key]["url"], token=data[key]["token"])


def build_scoped_npmrc(data, key):
    msg = "${scope}:registry=${url}\n//${domain}/:_authToken=${token}"
    template = Template(msg)
    domain = urlparse(data[key]["url"])
    return template.substitute(
        scope=data[key]["scope"],
        url=data[key]["url"],
        token=data[key]["token"],
        domain=domain.netloc)


def save_npmrc(data):
    f = open("/home/.npmrc", "w+")
    f.write(data)
    f.close()

def get_env():
    try:
        r = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
        r.raise_for_status()
    except RequestException as e:
        print(e)
        return None
    
    try:
        response_json = r.json()
    except RequestException as e:
        print(e)
        return None
    
    region = response_json.get('region')
    instance_id = response_json.get('instanceId')

    if not (region and instance_id):
        return None
    
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        instance = ec2.Instance(instance_id)
        tags = instance.tags
    except (ValueError, ClientError, BotoCoreError) as e:
        print(e)
        return None
    
    tags = tags or []
    envs = [tag.get('Value') for  tag in tags if tag.get('Key') == 'Environment']
    env = envs[0] if env else None
    return env
    

def main():
    env = get_env()
    print('Env:{}'.format(env))
    key = "platform/{}/jenkins_npm_repository_config".format(env)
    print('Key:{}'.format(key))
    secrets = json.loads(get_secrets(key))
 
    npmrc_string = ""

    for key in secrets:
        if "scope" in secrets[key] and secrets[key]["scope"] != "":
            npmrc_string += build_scoped_npmrc(secrets, key)
        else:
            npmrc_string += build_npmrc(secrets, key)

    save_npmrc(npmrc_string)
    print(npmrc_string)


main()
