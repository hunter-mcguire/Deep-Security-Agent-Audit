import datetime
import logging
import json
import sys

import requests
from urllib3.exceptions import InsecureRequestWarning


def list_computer_groups(dsm: dict):
    # Set headers
    headers = {
        'api-secret-key': dsm['ApiKey'],
        'api-version': 'v1'
    }
    
    try:
        response = requests.get(
            url=f"{dsm['Url']}:{dsm['Port']}/api/computergroups",
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            return response.json().get('computerGroups')

        logging.ERROR(f"List Groups Response: {response.reason}")
    except Exception as error:
        logging.ERROR(f"Failure List Computer Groups API on DSM: {dsm['DsmName']}")


def list_computers(dsm: dict):
    # Set headers
    headers = {
        'api-secret-key': dsm['ApiKey'],
        'api-version': 'v1'
    }

    try:
        response = requests.get(
            url=f"{dsm['Url']}:{dsm['Port']}/api/computers",
            headers=headers,
            params={
                'expand': [
                    'computerStatus',
                    'ec2VirtualMachineSummary',
                    'azureVMVirtualMachineSummary'
                ]
            },
            verify=False
        )

        if response.status_code == 200:
            return response.json().get('computers')

        logging.ERROR(f"List Computers Response: {response.reason}")
    except Exception as error:
        logging.ERROR(f"Failure List Computers API on DSM: {dsm['DsmName']}")


if __name__ == '__main__':
    # open config.json
    try:
        with open('config.json') as file:
            dsm_list = json.load(file)
    except FileNotFoundError:
        print("'config.json' missing in script directory.")
        sys.exit()

    # Main variable
    results = {
        'total_agent_count': 0,
        'timestamp': datetime.datetime.now().isoformat('T', 'seconds')
    }

    # Disable ssl cert verification for DS Self Signed Certificates
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    
    for dsm in dsm_list:
        dsm_name = dsm.get('DsmName')

        #get computers in DSM
        dsm_computers = list_computers(dsm)
        
        #get computer groups in DSM
        dsm_computer_groups = list_computer_groups(dsm)

        if dsm_computers and dsm_computer_groups:
            managed = [
                item for item in dsm_computers 
                if item.get('computerStatus').get('agentStatusMessages')[0] == 'Managed (Online)'
            ]

            # Add DSM Agent Count to total count
            results['total_agent_count'] += len(managed)

            # Update Results with attributes
            results[dsm_name] = {
                'managed_agent_count': len(managed),
                'aws_accounts': {},
                'azure_accounts': {},
                'computer_groups': {}
            }

            aws_accounts = results.get(dsm_name).get('aws_accounts')
            azure_accounts = results.get(dsm_name).get('azure_accounts')
            computer_groups = results.get(dsm_name).get('computer_groups')

            # Iterate through computers and get group name and info
            for item in managed:
                computer_object = {
                    'hostName': item.get('hostName'),
                    'displayName': item.get('displayName'),
                    'agentVersion': item.get('agentVersion'),
                    'platform': item.get('platform')
                }

                group_name, group_type = [
                    (group.get('name'), group.get('type')) for group in dsm_computer_groups
                    if group.get('ID') == item.get('groupID')
                ][0]

                if group_type == 'folder':
                    if group_name in computer_groups:
                        count = computer_groups[group_name]['agent_count']
                        computer_groups[group_name]['agent_count'] = count + 1
                        computer_groups[group_name]['managed_agents'].append(computer_object)
                    else:
                        computer_groups[group_name] = {
                            'agent_count': 1,
                            'managed_agents': [computer_object]
                        }

                if group_type.startswith('aws'):
                    aws_info = item.get('ec2VirtualMachineSummary')

                    if aws_info:
                        account_id = aws_info.get('accountID')

                        if account_id in aws_accounts:
                            count = aws_accounts[account_id]['agent_count']
                            aws_accounts[account_id]['agent_count'] = count + 1
                            aws_accounts[account_id]['managed_agents'].append(computer_object)
                        else:
                            aws_accounts[account_id] = {
                                'agent_count': 1,
                                'managed_agents': [computer_object]
                            }

                if group_type.startswith('azure'):
                    azure_info = item.get('azureVMVirtualMachineSummary')
                    if azure_info:
                        subscription_id = azure_info.get('subscriptionID')

                        if subscription_id in azure_accounts:
                            count = azure_accounts[subscription_id]['agent_count']
                            azure_accounts[subscription_id]['agent_count'] = count + 1
                            azure_accounts[subscription_id]['managed_agents'].append(computer_object)
                        else:
                            azure_accounts[subscription_id] = {
                                'agent_count': 1,
                                'managed_agents': [computer_object]
                            }

    #Write results to JSON
    with open('dsm_count.json', 'w') as file:
        json.dump(results, file)