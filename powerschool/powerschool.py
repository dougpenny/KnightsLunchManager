import base64
import datetime
import json
import os
import sys
import time

import requests


#
# Disable InsecureRequestWarning during testing
#
requests.packages.urllib3.disable_warnings()


class Powerschool:
    def __init__(self):
        """ Initialize a Powerschool object """
        self.base_url = os.getenv('POWERSCHOOL_URL')
        self.client_id = os.getenv('POWERSCHOOL_CLIENT_ID').encode('UTF-8')
        self.client_secret = os.getenv('POWERSCHOOL_CLIENT_SECRET').encode('UTF-8')
        try:
            self.headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': self.access_token()
            }
        except requests.exceptions.SSLError as e:
            sys.stderr.write('An ssl related error occured: %s\n' % e)
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write('A connection error occured: %s\n' % e)
        except Exception as e:
            sys.stderr.write(
                'An unknown error occured trying to connect to PowerSchool.\nError: %s\n' % e)

    def access_token(self):
        """ Retrieve an access token """
        if(hasattr(self, 'access_token_response')):
            if(self.access_token_response['expiration_datetime'] > datetime.datetime.now()):
                return "Bearer " + self.access_token_response['access_token']
        token_url = self.base_url + "/oauth/access_token"
        credentials = base64.b64encode(
            self.client_id + b":" + self.client_secret)
        auth_string = 'Basic {0}'.format(str(credentials, encoding='utf8'))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': auth_string
        }
        data = "grant_type=client_credentials"
        r = requests.post(token_url, data, headers=headers, verify=False)
        response = r.json()
        response['expiration_datetime'] = datetime.datetime.now(
        ) + datetime.timedelta(seconds=int(response['expires_in']))
        self.access_token_response = response
        return "Bearer " + response['access_token']

    # Non-paging endpoints
    def staffInDistrict(self):
        schools = self.schools()
        staff = []
        for school in schools:
            staff.extend(self.staffInSchool(school['id']))
        return staff

    def staffInSchool(self, school_id):
        """ Retrieve all of the staff from a given school """
        resource_endpoint = "ws/v1/school/{}/staff".format(str(school_id))
        return self.resource(resource_endpoint)

    def student_for_dcid(self, student_dcid):
        """ Retrieve the student with a given dcid """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self.access_token()
        }
        resource_endpoint = self.base_url + \
            "ws/v1/student/{}".format(student_dcid)
        student_response = requests.get(
            resource_endpoint, headers=headers, verify=False)
        return student_response.json()['student']

    def teacherWithDCID(self, teacher_dcid):
        """ Retrieve the teacher with a given dcid """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self.access_token()
        }
        resource_endpoint = self.base_url + \
            "ws/v1/staff/{}".format(teacher_dcid)
        teacher_response = requests.get(
            resource_endpoint, headers=headers, verify=False)
        return teacher_response.json()

    # Paging endpoints
    def resource(self, resource_endpoint, expansions=None, extensions=None, query=None):
        """ Retrieve the resource at the given resource_url """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self.access_token()
        }
        resource_name = resource_endpoint[resource_endpoint.rfind('/') + 1:]
        key_1 = resource_name + 's'
        key_2 = resource_name
        resource_url = self.base_url + resource_endpoint
        resource_count = self.resource_count(resource_url)
        params = {}
        if expansions:
            params['expansions'] = expansions
        if extensions:
            params['extensions'] = extensions
        if query:
            params['q'] = query
        data = []
        page_number = 1
        while len(data) < resource_count:
            params['page'] = str(page_number)
            try:
                requested_resource_response = requests.get(
                    resource_url, headers=headers, params=params, verify=False)
                requested_resources = requested_resource_response.json()[
                    key_1][key_2]
                if isinstance(requested_resources, dict):
                    data.extend(requested_resources)
                else:
                    resource_dict = [requested_resources]
                    data.extend(resource_dict)
            except:
                return []
            page_number += 1
        return data

    def resource_count(self, resource_url):
        """ Retrieve the count of the requested resource """
        resource_count_url = resource_url + "/count"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self.access_token()
        }
        try:
            data = requests.get(resource_count_url,
                                headers=headers, verify=False)
            resource_count = data.json()["resource"]["count"]
            return resource_count
        except:
            return 0

    def schools(self):
        """ Retrieve all of the schools """
        resource_endpoint = "ws/v1/district/school"
        return self.resource(resource_endpoint)

    def studentsForSchool(self, school_id, expansions=None, extensions=None, query=None):
        """ Retrieve all of the students in a given school """
        resource_endpoint = "ws/v1/school/{}/student".format(school_id)
        return self.resource(resource_endpoint, expansions)

    def studentsInDistrict(self):
        resource_endpoint = "ws/v1/district/student"
        return self.resource(resource_endpoint)

    def sectionsForSchool(self, school_id):
        """ Retrieve the sections in a given school """
        resource_endpoint = "ws/v1/school/{}/section".format(school_id)
        return self.resource(resource_endpoint)

    def coursesForSchool(self, school_id):
        """ Retrieve all of the courses in a given school """
        resource_endpoint = "ws/v1/school/{}/course".format(school_id)
        return self.resource(resource_endpoint)

    # PowerQuery endpoints
    def powerquery_resource(self, resource_endpoint, params=None):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self.access_token()
        }
        resource_url = self.base_url + resource_endpoint
        data = json.dumps(params) if params else '{}'
        try:
            response = requests.post(
                resource_url, data=data, headers=headers, verify=False)
            return response.json()['record']
        except:
            return []

    def active_staff(self):
        resource_endpoint = "ws/schema/query/com.nrcaknights.knightslunch.teachers.active_staff?pagesize=0"
        return self.powerquery_resource(resource_endpoint)

    def homeroom_roster_for_teacher(self, teacher_dcid):
        resource_endpoint = "ws/schema/query/com.nrcaknights.knightslunch.students.homeroom_roster"
        return self.powerquery_resource(resource_endpoint, {'teacher_dcid': teacher_dcid})

    def students_for_guardian(self, guardian_id):
        resource_endpoint = "ws/schema/query/com.pearson.core.guardian.student_guardian_detail"
        result = self.powerquery_resource(resource_endpoint, {'guardian_id': [guardian_id]})
        students = []
        for student in result:
            students.append(student['id'])
        return students
        
    # POST endpoints for sending data to PowerSchool
    def new_lunch_transaction(self, transaction_info):
        transaction_data = { "tables": { "U_LUNCH_TRANSACTIONS": transaction_info }}
        try:
            response = requests.post(
                self.base_url + "ws/schema/table/U_LUNCH_TRANSACTIONS/",
                data=json.dumps(transaction_data),
                headers=self.headers,
                verify=False
            )
            response = response.json()
            if response['insert_count'] == 1 and response['result'][0]['status'] == 'SUCCESS':
                return response['result'][0]['success_message']['id']
            else:
                return None
        except Exception as e:
            print("An exception occured: {}".format(e))
            return None