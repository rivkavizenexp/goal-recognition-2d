import configparser
import boto3
from pathlib import Path
from lxml.etree import Element, SubElement, CDATA, tostring

xml_schema_url = 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd'


class MturkHandler(object):

    def __init__(self):
        self.client = self.init_client()

    def init_client(self):
        config = configparser.ConfigParser()

        config_filename = Path.cwd() / '.aws' / 'config'
        config.read(config_filename)
        region_name = config['default']['region']

        cred_filename = Path.cwd() / '.aws' / 'credentials'
        config.read(cred_filename)
        aws_access_key_id = config['default']['aws_access_key_id']
        aws_secret_access_key = config['default']['aws_secret_access_key']

        # Sandbox url
        endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws' \
                       '.com'

        # Uncomment this line to use in production
        # endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

        client = boto3.client(
            'mturk',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        return client

    def create_question_xml(self, slides_lst):
        XHTML_NAMESPACE = xml_schema_url
        XHTML = "{%s}" % XHTML_NAMESPACE
        NSMAP = {
            None: XHTML_NAMESPACE,
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }
        envelope = Element("HTMLQuestion", nsmap=NSMAP)

        index_path = Path.cwd() / 'docs' / 'index.html'
        index_html = index_path.read_text()

        index_html = index_html.replace('var slides_to_test = [12];',
                                        'var slides_to_test = ' +
                                        str(slides_lst) + ';')

        html_content = SubElement(envelope, 'HTMLContent')
        html_content.text = CDATA(index_html)

        frame_height = SubElement(envelope, 'FrameHeight')
        frame_height.text = '0'

        return tostring(envelope, encoding='unicode')

    def create_hit(self, title, slides_lst):
        """
        Creates a HIT and sends it to Mturk
        """
        test_question = self.create_question_xml(slides_lst)

        response = self.client.create_hit(
            # Change/Add to these parameters as you see fit
            MaxAssignments=3,
            LifetimeInSeconds=600,
            AssignmentDurationInSeconds=600,
            Reward="0.11",
            Title=title,
            Keywords='question, answer, research',
            Description='Answer a simple question',
            Question=test_question
        )

        # The response included several fields that will be helpful later
        hit_type_id = response['HIT']['HITTypeId']
        hit_id = response['HIT']['HITId']
        print("\nCreated HIT: {}".format(hit_id))
        print("With shapes from slides: {}".format(slides_lst))
        print("\nCreated HIT type id: {}".format(hit_type_id))

        # This will return $10,000.00 in the MTurk Developer Sandbox
        print(self.client.get_account_balance()['AvailableBalance'])

    def read_hits(self):
        """
        Just an example of a way to read data from Mturk
        full API is in
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#client
        """
        list_hits = self.client.list_hits()
        print(list_hits)
