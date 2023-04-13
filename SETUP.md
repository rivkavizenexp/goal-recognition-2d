# Installation

## Python

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install 
the needed libraries described in [requirements.txt](requirements.txt) 

```bash
pip install -r requirements.txt
```

## Generate SVG slides
```[bash]
./main.py update -i <slides dir> -o public/docs/svg
```
## Firebase
Install the firebase CLI for deploying updated SVG files by following
 [this guide](https://firebase.google.com/docs/cli#instalnpm l_the_firebase_cli)

 Generate a private key file for your firebase account:
 - In the Firebase console, open Settings > Service Accounts.
 - Click Generate New Private Key, then confirm by clicking Generate Key.
 - Securely store the JSON file containing the key as firebase_adminsdk.json.

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
[sandbox]
aws_access_key_id=<public key>
aws_secret_access_key=<secret key>
```
the sandbox credential can be identical to the default ones, but doesn't have to

Follow [this guide](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html)
to setup your AWS account and create the access keys 

And follow [this documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client) 
for an API to Mturk through python's boto3  

## MTurk
Enter your parameters to the following file - 
`/.aws/mturk`

The file structure should be:
```text
[default]
reward=<reward of hit in dollars>
bonus=<bonus of hit in dollars>
duration=<duration of hit is seconds>
move_time=<time limit to each slide>
initial_delay=<initial delay>
color_qualification_test_id=<test_id>
candidate_min_hit_approved=<min_appruved_hit>
candidate_min_hit_approved_percent=<min_appruved_pct>
countries=<country_code>,...
[sandbox]
reward=<reward of hit in dollars>
bonus=<bonus of hit in dollars>
duration=<duration of hit is seconds>
move_time=<time limit to each slide>
initial_delay=<initial delay>
color_qualification_test_id=<test_id>
candidate_min_hit_approved=<min_appruved_hit>
candidate_min_hit_approved_percent=<min_appruved_pct>
countries=<country_code>,...
```

make sure you create color blindness qualification test and stored its id in the file:
```[bash]
./main.py mturk [-p] create_test
```
specify -p to create the test on production enviorment

