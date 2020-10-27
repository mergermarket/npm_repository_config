import sys
import boto3
import json

from botocore.exceptions import ClientError, BotoCoreError
from base64 import b64encode
from urllib.parse import urlparse


def get_secrets(secretId):
    client = boto3.client(service_name='secretsmanager')
    return client.get_secret_value(SecretId=secretId)['SecretString']


def build_npmrc(data):
    return (
        f"registry = {data['url']}\n"
        f"username = {data['username']}\n"
        f"_password = {b64encode(data['password'].encode('utf8')).decode('utf8')}\n"
    )


def build_scoped_npmrc(data):
    domain = urlparse(data["url"])
    return (
        f"{data['scope']}:registry={data['url']}\n"
        f"//{domain.netloc}/:_authToken={data['token']}\n"
    )


def save_npmrc(data):
    f = open("/home/.npmrc", "w+")
    f.write(data)
    f.close()


def get_env(filepath):
    
    with open(filepath) as json_file:
        data = json.load(json_file)
        region = data['region']
        instance_id = data['instanceId']

    if not (region and instance_id):
        return None
    
    try:
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instance_id)
        tags = instance.tags
    except (ValueError, ClientError, BotoCoreError) as e:
        raise Exception("could not get enviornment: " + str(e))
    
    envs = [tag.get('Value') for  tag in tags if tag.get('Key') == 'Environment']
    env = envs[0] if envs else None
    return env
    

def main():
    env = get_env(sys.argv[1])
    key = "platform/{}/jenkins_npm_repository_config".format(env)

    print(f"npm_repository_config: getting secret...", file=sys.stderr)

    secrets = json.loads(get_secrets(key))
 
    print(f"npm_repository_config: generating config...", file=sys.stderr)

    npmrc_string = ""

    for key in secrets:
        if "scope" in secrets[key] and secrets[key]["scope"] != "":
            npmrc_string += build_scoped_npmrc(secrets[key])
        else:
            npmrc_string += build_npmrc(secrets[key])

    print(f"npm_repository_config: writing config config...", file=sys.stderr)

    save_npmrc(npmrc_string)

    print(f"npm_repository_config: done.", file=sys.stderr)


main()
