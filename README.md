# Online Agent Audit
 
This script will capture online agents in the context of AWS Accounts, Azure Accounts, and computer groups. It shows total agent count as well as the count of agents in each provided DSM.

Simply add the Deep Security managers into the config.json file. This file is in JSON format and each DSM item in the array will need a name, dsm url, port, and API key.

example usage: </br>
```python3 dsm_count.py```

This will create a dsm_count.json output file. Example shown below:
```
{
    "total_agent_count": 3,
    "timestamp": "2024-02-13T08:23:13",
    "Test DSM": {
        "managed_agent_count": 3,
        "aws_accounts": {
            "123456789123": {
                "agent_count": 3,
                "managed_agents": [
                    {
                        "hostName": "ec2-51-199-42-285.us-west-1.compute.amazonaws.com",
                        "displayName": "Deep Security Manager-TESTING_DO_NOT_DELETE",
                        "agentVersion": "20.0.0.8453",
                        "platform": "Amazon Linux 2 (64 bit) (4.14.330-250.540.amzn2.x86_64)"
                    },
                    {
                        "hostName": "ec2-19-142-18-283.us-west-1.compute.amazonaws.com",
                        "displayName": "Test-2-TESTING_DO_NOT_DELETE",
                        "agentVersion": "20.0.0.8453",
                        "platform": "Amazon Linux 2023 (64 bit) (6.1.72-96.166.amzn2023.x86_64)"
                    },
                    {
                        "hostName": "ec2-4-102-78-17.us-west-1.compute.amazonaws.com",
                        "displayName": "Deep Security Manager-TESTING_DO_NOT_DELETE",
                        "agentVersion": "20.0.0.8453",
                        "platform": "Amazon Linux 2 (64 bit) (4.14.330-250.540.amzn2.x86_64)"
                    }
                ]
            }
        },
        "azure_accounts": {},
        "computer_groups": {}
    }

