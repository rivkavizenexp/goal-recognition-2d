#Installation

## Python

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install 
the needed libraries described in [requirements.txt](requirements.txt) 

```bash
pip install -r requirements.txt
```

## Firebase
Install the firebase CLI for deploying updated SVG files by following
 [this guide](https://firebase.google.com/docs/cli#install_the_firebase_cli)

### Deploy
Open the CLI in a different folder, and copy to it the JsPsych and SVG folders.
Follow [this guide](https://firebase.google.com/docs/hosting/quickstart) 
which can be summarized to these CLI commands -
```bash
firebase login
```
log in with your firebase credentials 
```bash
firebase init hosting
```
Make sure to update the generated `firebase.json` file to add CORS headers to SVG files
```bash
firebase deploy --only hosting -m "<deploy message>"
```
Change `<deploy message>` to some meaningful message. 
After this command the changes are updated in Firebase Hosting and are accessible to any new worker. 

## AWS
Get public and secret access key from AWS and place in the following file -
`/.aws/credentials`

The file structure should be:
```text
[default]
aws_access_key_id=<public key>
aws_secret_access_key=<secret key>
```

Follow [this guide](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html)
to setup your AWS account and create the access keys 

And follow [this documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client) 
for an API to Mturk through python's boto3  