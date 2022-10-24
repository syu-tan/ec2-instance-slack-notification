#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import urllib
import json
def lambda_handler(event, context):
    instance_id = event['detail']['instance-id']
    client = boto3.client('ec2')
    response = client.describe_instances(
        InstanceIds=[
            instance_id,
        ],
    )
    instance = response['Reservations'][0]['Instances'][0]
    fields = []
    # Name
    for tag in instance['Tags']:
        if tag['Key'] != 'Name':
            continue
        instance_name = tag['Value']
        fields.append({
            'title': 'Name',
            'value': instance_name,
            'short': True,
        })
        break
    # InstanceId
    fields.append({
        'title': 'インスタンス ID',
        'value': instance_id,
        'short': True,
    })
    # InstanceType
    fields.append({
        'title': 'インスタンスタイプ',
        'value': instance['InstanceType'],
        'short': True,
    })
    # AvailabilityZone
    fields.append({
        'title': 'アベイラビリティーゾーン',
        'value': instance['Placement']['AvailabilityZone'],
        'short': True,
    })
    # NetworkInterfaces
    for interfaces in instance['NetworkInterfaces']:
        idx = interfaces['Attachment']['DeviceIndex']
        for ip_addresses in interfaces['PrivateIpAddresses']:
            fields.append({
                'title': 'プライベート IP (eth{})'.format(idx),
                'value': ip_addresses.get('PrivateIpAddress'),
                'short': True,
            })
            fields.append({
                'title': 'パブリック IP (eth{})'.format(idx),
                'value': ip_addresses.get('Association', {}).get('PublicIp'),
                'short': True,
            })
    try:
        state = event['detail']['state']
    except:
        state = None
    print(state)
    
    if state == 'running':
        text =  f'インスタンスが起動しました。'
        color = 'good'
    elif state == 'stopped':
         text = f'インスタンスが停止しました。'
         color = 'bad'
    else:
         text = f'インスタンスの状態が変更されました。ステータス:{state}'
         color = 'bad'
            
    data = {
        'attachments': [{
            'pretext': text,
            'color': color,
            'fields': fields,
        }]
    }
    # Slack通知
    url = '********************************'
    req = urllib.request.Request(url, json.dumps(data).encode(), {'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    res.read()
    res.close