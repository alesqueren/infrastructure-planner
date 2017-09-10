infrastructure-planner
======================

Generate a server infrastructure from a yaml config file.
Use python-novaclient.

## Usage

```shell
main.py [-c CONFIG_PATH] <create|delete>
```

## Environment

Same as a openstack config file (openrc.sh):
```shell
OS_AUTH_URL=XXX
OS_TENANT_ID=XXX
OS_TENANT_NAME=XXX
OS_USERNAME=XXX
OS_PASSWORD=XXX
OS_REGION_NAME=XXX
```

## Infrastructure config file

Every server must have an image, a flavor and a network unless specified in the default section.

```yaml
default:
  image: Debian 8
  flavor: vps-ssd-1
  network: Ext-Net

servers:
  manager:
    flavor: vps-ssd-2
    meta:
      docker: manager

  worker:
    instances-nb: 2
    meta:
      docker: worker
```

## Docker

```shell
$ docker build -t infrastructure-planner .
$ docker run \
    OS_AUTH_URL=XXX \
    OS_TENANT_ID=XXX \
    OS_TENANT_NAME=XXX \
    OS_USERNAME=XXX \
    OS_PASSWORD=XXX \
    OS_REGION_NAME=XXX \
    infrastructure-planner \
    -c example/config.yml create
```
