import boto3

def lambda_handler(event, context):
    # Create a Redshift client
    redshift = boto3.client('redshift')

    # Get the email address from the event
    email = event['email']

    # Define the username and password for the new account
    username = email.split('@')[0]
    password = 'SecurePassword'

    # Create a Redshift cluster security group
    security_group = redshift.create_cluster_security_group(
        ClusterSecurityGroupName=username + '-security-group',
        Description='Security group for ' + username
    )

    # Add an ingress rule to the security group to allow read-only access from the user's IP address
    redshift.authorize_cluster_security_group_ingress(
        ClusterSecurityGroupName=username + '-security-group',
        CIDRIP=event['ip'],
        EC2SecurityGroupName=username,
        EC2SecurityGroupOwnerId='amazon-redshift'
    )

    # Create the Redshift user account
    redshift.create_user(
        ClusterIdentifier='mycluster',
        UserName=username,
        Password=password,
        DBUser=username,
        VpcSecurityGroupIds=[security_group['ClusterSecurityGroup']['VpcSecurityGroupId']]
    )

    # Grant the user read-only access to the database
    redshift.execute_statement(
        ClusterIdentifier='mycluster',
        Database='mydb',
        SqlStatement='GRANT SELECT ON ALL TABLES IN SCHEMA public TO ' + username
    )

    return {
        'username': username,
        'password': password
    }
