import configparser
# import xml.etree.ElementTree as ET
import boto3
import pandas as pd
import random as rnd

NUM_OF_TASKS = 3
BATCH_SIZE = 10

# XML_ADDITION_1 = "![CDATA[ \n"
# XML_ADDITION_2 = "\n]]"


# def update_question_xml():
#     ET.register_namespace("", "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd")
#     tree = ET.parse("question_template.xml")
#     node = tree.find(".//")
#     with open("Test.html", "r") as question_html:
#         question = XML_ADDITION_1 + question_html.read() + XML_ADDITION_2
#         # node.set("", question)
#         node.append(ET.Element(question))
#     tree.write("question.xml", method="xml")

def generateCSV():
    col_dict = dict()
    df = pd.DataFrame()
    for j in range(BATCH_SIZE):
        for i in range(NUM_OF_TASKS):
            col_dict["task_"+str(i)+"_dynamic"] = "random_dynamic_img_path_from_db"
            col_dict["task_"+str(i)+"_static"] = "random_static_img_path_from_db"
            col_dict["task_"+str(i)+"_x"] = "random_img_x_from_db"
            col_dict["task_"+str(i)+"_y"] = "random_img_y_from_db"
            col_dict["task_"+str(i)+"_height"] = "random_img_height_from_db"
            col_dict["task_"+str(i)+"_width"] = "random_img_width_from_db"
            # check if also height, width, and initial x, y
        df.append(col_dict)
    df.to_csv("./CSV_file")

def run_test():
    config = configparser.ConfigParser()

    config.read('./.aws/config')
    region_name = config['default']['region']

    config.read('./.aws/credentials')
    aws_access_key_id = config['default']['aws_access_key_id']
    aws_secret_access_key = config['default']['aws_secret_access_key']

    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

    # Uncomment this line to use in production
    # endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

    client = boto3.client(
        'mturk',
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    with open("question.xml", "r") as question_xml:
        test_question = question_xml.read()

    response = client.create_hit(
        MaxAssignments=3,
        LifetimeInSeconds=600,
        AssignmentDurationInSeconds=600,
        Reward="0.11",
        Title='Test - Move Shapes',
        Keywords='question, answer, research',
        Description='Answer a simple question',
        Question=test_question
    )

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    print("\nCreated HIT: {}".format(hit_id))

    # This will return $10,000.00 in the MTurk Developer Sandbox
    print(client.get_account_balance()['AvailableBalance'])


if __name__ == '__main__':
    # update_question_xml()
    # run_test()
    generateCSV()
