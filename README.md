# dresource
dService for creating resources (AWS etc)

## Example usage with drunner

```
drunner install infmon/dresource 
dresource configure aws <<Username>> <<AWS Access key>> <<AWS Secret key>>
dresource create <<Path to Resource List File>>
```
The Resource List File is a JSON file with the following format.  Note that MySQL support is untested and unlikely to work at this point:
```
{
    "projectname" : "<<Project name>>",
    "s3" : {
        "<<Bucket name>>": {
            "region" : "<<AWS Region (defaults to us-east-1 if undefined)>>"
        }
    }
    "dynamodb" : {
        "<<Table name>>" : {
            "region" : "<<AWS Region (defaults to us-east-1 if undefined)>>"
            "hash_key_name" : "<<Hash key name>>",
            "read_capacity" : "<<Read capacity (defaults to 5 if undefined)>>",
            "write_capacity" : "<<Write capacity (defaults to 5 if undefined)>>"
        }
    },
    "mysql" : {
        "<<Schema name>>" : {
            "schema_file" : "<<Name of the schema file for this database.  Must be in the same directory as this config file>>",
            "users" : {
                "<<User name>>" : {
                    "privileges" : "<<Privileges to give this user>>"
                }
            }
        }
    }
}
```
The AWS IAM User is expected to have the following policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "dynamodb:*"
            ],
            "Resource": [
                "arn:aws:s3:::<<USERNAME>>-*",
                "arn:aws:s3:::<<USERNAME>>-*/*",
                "arn:aws:dynamodb:*:*:table/<<USERNAME>>-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "dynamodb:ListTables"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
All resources created by dresource will have 'username-projectname-' prepended on their names, so they can be identified.
If you use the special username 'PRODUCTION', then no username is prepended. 

Note that if you change the name of a resource, the existing resource will be deleted and a new resource created with the new name.  Data will not be preserved.