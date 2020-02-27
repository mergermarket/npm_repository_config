import sys
import boto3
import json

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


def main():
    secrets = json.loads(get_secrets(sys.argv[1]))

    npmrc_string = ""

    for key in secrets:
        if "scope" in secrets[key] and secrets[key]["scope"] != "":
            npmrc_string += build_scoped_npmrc(secrets, key)
        else:
            npmrc_string += build_npmrc(secrets, key)

    save_npmrc(npmrc_string)
    print(npmrc_string)


main()
