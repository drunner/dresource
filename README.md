# dresource
dService for creating resources (AWS etc)

## Example usage with drunner

```
drunner install infmon/dresource 
dresource configure <<Username>> <<AWS Access key>> <<AWS Secret key>>
dresource create <<Path to Resource List File>>
```
The Resource List File is a JSON file with the following format:
```
{
    "projectname" : "<<Project name (prepended to all resource names)",
    "s3" : {
        "bucket-name": {
            "region" : "<<AWS Region (defaults to us-east-1 if undefined)>>"
        },
        "another-bucket": {}
    }
    "dynamodb" : {
        "table-name" : {
            "region" : "<<AWS Region (defaults to us-east-1 if undefined)>>"
            "hash_key_name" : "<<Hash key name>>",
            "read_capacity" : "<<Read capacity (defaults to 5 if undefined)>>",
            "write_capacity" : "<<Write capacity (defaults to 5 if undefined)>>"
        }
    }
}
```
Note that all resources have 'Username-Projectname-' prepended to them 