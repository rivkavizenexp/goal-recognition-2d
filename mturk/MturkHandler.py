import configparser
import boto3
from botocore.config import Config
from pathlib import Path
from lxml.etree import Element, SubElement, CDATA, tostring
config_path = Path(__file__).parent / '..' / '.aws'

xml_schema_url = 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd'


class MturkHandler(object):

    def __init__(self,production=False):
        self.prod = production
        self.client = self.init_client(production)

    def init_client(self,production=False):
        config = configparser.ConfigParser()
        
        config_filename = config_path / 'config'
        config.read(config_filename)
        region_name = config['default']['region']

        cred_filename = config_path / 'credentials'
        config.read(cred_filename)

        if production:
            aws_access_key_id = config['default']['aws_access_key_id']
            aws_secret_access_key = config['default']['aws_secret_access_key']
        else:
            aws_access_key_id = config['sandbox']['aws_access_key_id']
            aws_secret_access_key = config['sandbox']['aws_secret_access_key']


        # Sandbox url
        sandbox_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
        # Production url
        production_url = 'https://mturk-requester.us-east-1.amazonaws.com'

        endpoint_url  = production_url if production else sandbox_url

        config = Config(
            retries = dict(
                max_attempts = 10
            )
        )

        client = boto3.client(
            'mturk',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=config
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

        index_path = Path.cwd() / 'public' / 'docs' / 'index.html'
        index_html = index_path.read_text()

        config = configparser.ConfigParser()


        cred_filename = Path.cwd() / '.aws' / 'mturk'
        config.read(cred_filename)
        conf = config['default' if self.prod else 'sandbox']

        index_html = index_html.replace('{{slides_to_test}}',str(slides_lst))
        index_html = index_html.replace('{{num_pictures}}',str(len(slides_lst)))
        index_html = index_html.replace('{{initial_delay}}',conf['initial_delay'])
        index_html = index_html.replace('{{move_time}}',conf['move_time'])
        index_html = index_html.replace('{{bonus_amount}}',conf['bonus'])
        index_html = index_html.replace('{{payment_amount}}',conf['reward'])

        html_content = SubElement(envelope, 'HTMLContent')
        html_content.text = CDATA(index_html)

        frame_height = SubElement(envelope, 'FrameHeight')
        frame_height.text = '0'

        return tostring(envelope, encoding='unicode')

    def create_color_qualification_test(self):
        path_root=Path.cwd() / 'public' / 'docs' 
        questions = open(path_root/'color_blindness_test.xml', mode='r').read()
        answers = open(path_root/'color_blindness_answers.xml', mode='r').read()

        qual_response = self.client.create_qualification_type(
                        Name='Color blindness test',
                        Keywords='test, qualification, sample, colorblindness, boto',
                        Description='This is a brief colorblindness test',
                        QualificationTypeStatus='Active',
                        Test=questions,
                        AnswerKey=answers,
                        TestDurationInSeconds=300)
        return qual_response['QualificationType']['QualificationTypeId']

    def create_hit(self, title, slides_lst,max_assignments=1,lifetime=1800):
        """
        Creates a HIT and sends it to Mturk
        Parameters:
            title(str): title of the hit
            max_assignments(int): max assignments per hit
            lifetime(int): lifetime in seconds
            duration(int): hit duration in seconds
            reward(int): reward per assignment
            candidate_min_hit_approved(int): minimum approved hits requirement
            candidate_min_hit_approved_percent(int): minimum approved hit percent requirement
        """
        test_question = self.create_question_xml(slides_lst)

        config = configparser.ConfigParser()

        config_filename = Path.cwd() / '.aws' / 'mturk'
        config.read(config_filename)
        conf = config['default' if self.prod else 'sandbox']
        

        #create qualification requirements
        qualification_requirements = [
            {'QualificationTypeId': '000000000000000000L0',#percent hits approved
                'Comparator': 'GreaterThanOrEqualTo',
                'IntegerValues': [int(conf['candidate_min_hit_approved_percent'])],
                'ActionsGuarded': 'Accept'
            },
            {'QualificationTypeId': '00000000000000000040',#number hits approved
                'Comparator': 'GreaterThanOrEqualTo',
                'IntegerValues': [int(conf['candidate_min_hit_approved'])],
                'ActionsGuarded': 'Accept'
            },
            {'QualificationTypeId':conf['color_qualification_test_id'],#color blindness qualification, for prod: 
                'Comparator': 'EqualTo',
                'IntegerValues':[100]
            },
            {'QualificationTypeId': '00000000000000000071',#US only
                'Comparator': 'In',#'EqualTo',
                'LocaleValues': [{ 'Country': c.strip().upper() } for c in conf['countries'].split(',')]
            },
        ]
        
        response = self.client.create_hit(
            # Change/Add to these parameters as you see fit
            MaxAssignments=max_assignments,
            LifetimeInSeconds=lifetime,
            AssignmentDurationInSeconds=int(conf['duration']),
            Reward=conf['reward'],
            Title=title,
            Keywords='question, shapes, research',
            Description='Move shapes to their right place',
            Question=test_question,
            QualificationRequirements=qualification_requirements
        )

        # The response included several fields that will be helpful later
        hit_type_id = response['HIT']['HITTypeId']
        hit_id = response['HIT']['HITId']

        print(f"Created HIT: {hit_id}")
        return response

    def read_hits(self):
        """
        Just an example of a way to read data from Mturk
        full API is in
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#client
        """
        list_hits = self.client.list_hits()
        return list_hits

    def get_hit(self,hit_id):
        return self.client.get_hit(HITId=hit_id)

    def read_reviewable_hits(self):
        list_hits = self.client.list_reviewable_hits()
        return list_hits

    def delete_hit(self,hit_id):
        return self.client.delete_hit(HITId=hit_id)

    def get_account_balance(self):
        # This will return $10,000.00 in the MTurk Developer Sandbox
        return self.client.get_account_balance()['AvailableBalance']

    def get_assignments(self,hit_id):
        assignments = self.client.list_assignments_for_hit(HITId=hit_id)['Assignments']
        return assignments
    
    def approve_assignment(self,assignmrnt_id):
        response = self.client.approve_assignment(AssignmentId=assignmrnt_id)
        return response

    def reject_assignment(self,assignmrnt_id,message):
        response = self.client.reject_assignment(AssignmentId=assignmrnt_id,RequesterFeedback=message)
        return response

    def send_bonus(self,worker_id,assignment_id,bonus_amount,reason):
        response = self.client.send_bonus(
            WorkerId=worker_id,
            BonusAmount=str(bonus_amount),
            AssignmentId=assignment_id,
            Reason=reason,
        )
        return response

    def update_expiration(self,hit_id,time):
        self.client.update_expiration_for_hit(HITId=hit_id,ExpireAt=time)
