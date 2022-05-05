from flask import Flask, render_template, request
import json
import requests

from custos.clients.user_management_client import UserManagementClient
from custos.clients.group_management_client import GroupManagementClient
from custos.clients.resource_secret_management_client import ResourceSecretManagementClient
from custos.clients.sharing_management_client import SharingManagementClient
from custos.clients.identity_management_client import IdentityManagementClient


from custos.transport.settings import CustosServerClientSettings
import custos.clients.utils.utilities as utl

from google.protobuf.json_format import MessageToJson
app = Flask(__name__)

# # create custos user management client
# user_management_client = UserManagementClient(custos_settings)
# global orion
class Orion:
    def __init__(self):
        try :
            # read settings
            self.client_id = 'custos-rswfydl920pg7kuvmayc-10003419'
            custos_settings = CustosServerClientSettings(custos_host='custos.scigap.org',
                            custos_port='31499', 
                            custos_client_id='custos-rswfydl920pg7kuvmayc-10003419',
                            custos_client_sec='zGDFZJpx40E0OT5EIS6WL1PZK2hHtiOs2aYFyR1y')

            # create custos user management client
            self.user_management_client = UserManagementClient(custos_settings)

            # create custos group management client
            self.group_management_client = GroupManagementClient(custos_settings)

            # create custos resource secret client
            self.resource_secret_client = ResourceSecretManagementClient(custos_settings)

            # create sharing management client
            self.sharing_management_client = SharingManagementClient(custos_settings)

            # create identity management client
            self.identity_management_client = IdentityManagementClient(custos_settings)


            # obtain base 64 encoded token for tenant
            self.b64_encoded_custos_token = utl.get_token(custos_settings=custos_settings)

            self.created_groups = {}

            self.admin_user_name = "anita1397@gmail.com"
            self.admin_password = "IJR@circ@1"
            
            resource_ids = []
            print("Successfully configured all custos clients")
            print(self.b64_encoded_custos_token)
        except Exception as e:
            print("Custos Id and Secret may wrong "+ str(e))
            raise e
        try:
            # self.verifiy_user(self.admin_user_name,self.admin_password)
            print("Successfully verified user")
        except Exception as e:
            print("verifiy_user is not defined or user may not be created  in the teanant"+ str(e))

    def verifiy_user(self, login_user_id,login_user_password):
        print("Login user "+ login_user_id)
        login_reponse = self.identity_management_client.token(token=self.b64_encoded_custos_token, username=login_user_id, password=login_user_password, grant_type='password')
        login_reponse = MessageToJson(login_reponse)
        print("Login response: ", login_reponse)
        response = self.user_management_client.get_user(token=self.b64_encoded_custos_token, username=login_user_id)
        print(" Updating user profile...  ")
        self.user_management_client.update_user_profile(
            token=self.b64_encoded_custos_token,
            username=response.username,
            email=response.email,
            first_name=response.first_name,
            last_name=response.last_name)
        print(" User  "+ login_user_id + " successfully logged in and updated profile")
        
    def register_users(self, user):
        try:
            resp = self.user_management_client.register_user(token=self.b64_encoded_custos_token,
                                                username=user['username'],
                                                first_name=user['first_name'],
                                                last_name=user['last_name'],
                                                password=user['password'],
                                                email=user['email'],
                                                is_temp_password=False)

            self.user_management_client.enable_user(token=self.b64_encoded_custos_token, username=user['username'])
            return (str(resp), 200, None)
        except Exception as e:
            return (str(e), 500, None)

    def delete_users(self, user):
        try:
            print("Deleting users")
            resp = self.user_management_client.delete_user(token=self.b64_encoded_custos_token,
                                                username=user['username'])
            print("Request processed")
            return (str(resp), 200, None)
        except Exception as e:
            return (str(e), 500, None)

    def create_group(self, group):
        try:
            print("Creating group: " + group['name'])
            grResponse = self.group_management_client.create_group(token=self.b64_encoded_custos_token,
                                                            name=group['name'],
                                                            description=group['description'],
                                                            owner_id=group['owner_id'])

            resp = MessageToJson(grResponse)
            print(resp)
            respData = json.loads(resp)
            print("Created group id of "+ group['name'] + ": " +respData['id'] )
            self.created_groups[respData['name']] = respData['id']
            # temp = Groups_Json()
            # temp.write_groups(respData['name'], group['owner_id'])
            # temp.save_json()
            # del temp
            return (str(resp), 200, None)

        except Exception as e:
            return (str(e), 500, None)

    def get_all_groups(self):
        try:
            groups = self.group_management_client.get_all_groups(self.b64_encoded_custos_token)
            # for x in groups:
            #     print(x)
            resp = MessageToJson(groups)
            respData = json.loads(resp)
            # for x in respData['groups']:
            #     print(x['id'])
            return respData['groups']
        except:
            return 0

    def allocate_user_to_group(self, user, group):
        try:
            group_id = self.created_groups[group]
            print("Assigning user " + user + " to group " + group)
            val = self.group_management_client.add_user_to_group(token=self.b64_encoded_custos_token,
                                                    username=user,
                                                    group_id=group_id,
                                                    membership_type='Member'
                                                    )
            resp = MessageToJson(val)
            print(resp)
            temp = Groups_Json()
            temp.write_groups(group, user)
            temp.save_json()
            del temp
            return 1
        except Exception as e:
            print(e)
            print("User allocation error")
            return 0
    
    def get_all_users_of_group(self, group):
        temp = Groups_Json()
        print(temp.read_groups()[group])
        del temp
        # print(self.group_management_client.group_stub.getAllChildUsers)
        pass

    def test(self):
        print("I am still alive!!!")

@app.route('/register',methods = ['POST', 'GET'])
def register_handler():
    try:  
        # print("Sample data",sample)
        return orion.register_users(request.json)
    except Exception:
        print("please defined method register_users")
        return "Error saving user",500



@app.route('/deleteuser',methods = ['POST'])
def delete_user_handler():
    try:  
        # print("Sample data",sample)
        return orion.delete_users(request.json)
    except Exception:
        print("please defined method delete_users")
        return "Error deleting user",500



@app.route("/creategroup",methods = ['POST'])
def create_group_handler():
    try:  
        print(str(request.json))
        return orion.create_group(request.json)
    except Exception as e:
        print(e)
        print("please defined method create_groups")
        return (str(e), 500, None)



@app.route("/test")
def hello():
    return "I am alive!!!"

@app.route("/")
def index():
    # main()
    global orion
    orion.test()
    groups = orion.get_all_groups()
    return render_template('index.html')

def test_end_point():
    url = "https://dev.portal.usecustos.org/group-management/v1.0.0/groups"

    payload={}
    headers = {
    'Authorization': 'Basic base64(\'custos-rswfydI920pg7kuvmayc-10003419:zGDFZJpx40E0OT5EIS6WL1PZK2hHtiOs2aYFyR1y\');'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text) 

# def 

def init():
    global orion
    orion = Orion()

if __name__ == "__main__":
    # main()
    init()
    app.run()