import requests
import sys
import json
import os

API_ENTRY_POINT1 = "https://api.ilovepdf.com/v1/auth"
API_ENTRY_POINT2="https://api.ilovepdf.com/v1/start"

task={
    1:"merge",
    2:"compress",
    3:"imagepdf",
    4:"unlock",
    5:"extract"
}

class ILovePdf:
    def __init__(self,public_key):
        self.public_key=public_key
        self.token=self.get_token()
        
    def get_token(self):

        data={
            "public_key":self.public_key
        }
        response=requests.post(API_ENTRY_POINT1,data).json()
        return response['token']

class operations(ILovePdf):
    
    def __init__(self, public_key):
        super().__init__(public_key)
        self.headers = {"Authorization": "Bearer {}".format(self.token)}
        
    
    def start_task(self,tool):
        self.files = []
        self.tool = tool
        url = "{}/{}".format(API_ENTRY_POINT2,self.tool)
        response=requests.get(url,headers=self.headers).json()
        self.server = response["server"]
        self.task_id = response["task"]
        self.base_api_url = "https://{}/v1".format(self.server)
        return response
    
    def add_file(self, filename):
        url = self.base_api_url + "/upload"
        params = {"task": self.task_id}
        files = {"file": open(filename, "rb")}
        response = requests.post(
            url,
            params,
            files=files,
            headers=self.headers
        ).json()
        self.server_filename = response["server_filename"]
        self.files.append({
            "server_filename": response["server_filename"],
            "filename": filename
        })
        return response
    
    def execute(self):
        url = self.base_api_url + "/process"
        fixed_params = {
            "task": self.task_id,
            "tool": self.tool,
            "files": self.files
        }
        params = fixed_params.copy()
        response = requests.post(url, json=params, headers=self.headers).json()
        self.timer = response["timer"]
        return response
    
    def download(self, output_filename=None):
        url = self.base_api_url + "/download/{}".format(self.task_id)
        response = requests.get(url, headers=self.headers)
        output_filename = self.__get_output_filename(
            output_filename
        )
        with open(output_filename, "wb") as output_file:
            output_file.write(response.content)
        return response.status_code

    def __get_output_filename(self, output_filename=None):
        if self.tool == "merge":
            filetype = "pdf"
        elif self.tool == "extract":
            filetype = "txt"
        else:
            if len(self.files) == 1:
                filetype = "pdf"
            else:
                filetype = "zip"
        if output_filename:
            ft = output_filename[-3:]
            if ft != filetype:
                output_filename += ("." + filetype)
        else:
            output_filename = "out." + filetype
            
        return output_filename



if __name__ == "__main__":
    try :
        def get_creds_path():
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, "creds.json")
            else:
                # Running as a script
                return "creds.json"
    except Exception as e:
        print(e.__str__)
        
    creds_path = get_creds_path().replace('"', '')
    with open(creds_path, 'r') as creds_file:
        creds = json.load(creds_file)
        public_key = creds['public_key']

    i=operations(public_key)

    while True:
        
        print("select the task you want to perfom :\n")
        print(" 1.merge\n","2.compress\n", "3.imagepdf\n", "4.unlock\n","5.extract\n")
        
        task_number=int(input("Enter the task number : "))
        i.start_task(task[task_number])
        
        if task_number==1:
            number_of_files=int(input("Enter number of files you want to merge : "))
            for _ in range(number_of_files):
                path=input("enter the file path : ")
                i.add_file(path.replace('"', ''))
        else:
            path=input("enter the file path : ")
            i.add_file(path.replace('"', ''))
        
        i.execute()
        file_name=input("enter the output file_name with extension : ")
        
        i.download(file_name)
        
        if input("Do you want to quit? (y/n) : ").lower() == "y":
            sys.exit()