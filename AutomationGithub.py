import requests
import configparser
import pandas as pd



def GitHub_project():

    #initialize endpoint to connect to Github
    ENDPOINT1 = "https://api.github.com/repos/GitHubEventsProject/GitHub_event_Periya/events?per_page=100"

    # Read data from config-prod.ini file:
    config_data = configparser.ConfigParser()
    config_data.read("config-prod.ini")
        
    # Fetch Token from ini file
    token = config_data["GitHub"]["Token"]

    # Fetch Token from ini file
    headers = {"Authorization": "token {}".format(token)}
 
    # print 200 OK Response after get request
    resp = requests.get(ENDPOINT1, headers=headers, verify=False) 
    resp.raise_for_status()

    #Get the commit ID and the respective records in Json format;
    data = sorted(resp.json(), key=lambda x: x["id"]) 
    
    print("Length of the event is", len(data))

    #arrange the columns properly
    df=pd.DataFrame.from_dict(data)
    df=pd.DataFrame.from_dict(data, orient="columns")
    df=df.iloc[:,[0,1,2,7,3,4,5,6]]
            
    # write only organization name in org column 
    df['org']="GitHubEventsProject"

    # Formating date
    df['created_at'] = pd.to_datetime(df['created_at'], format='%Y-%m-%dT%H:%M:%SZ') #2023-02-15T07:26:49Z
            
    # Write Repo name in repo column from Json data
    df1=pd.DataFrame.from_dict(pd.json_normalize(df['repo']), orient='columns')
    df1['name'] = df1['name'].str.replace("GitHubEventsProject"+'/', '')
    df['repo']=df1['name']

    # Write employee ID in actor column from Json data
    df2=pd.DataFrame.from_dict(pd.json_normalize(df['actor']), orient='columns')
    df2['login'] = df2['login'].str.replace(',', '')
    df['actor']=df2['login']

    master_list=pd.read_excel("Github_Report.xlsx", engine='openpyxl')

    # remove duplicates;
    master_list=master_list.drop_duplicates(subset=['id'])

    # Append the new data to the existing dataframe
    updated_data = master_list.append(df)

    # Write the updated data to the same sheet in the Excel file
    with pd.ExcelWriter("Github_Report.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        updated_data.to_excel(writer, sheet_name='ghevents', index=False)  

    master_list=pd.read_excel("Github_Report.xlsx", engine='openpyxl', )
    print("Length of the rows in master list:",len(master_list))
    master_list=master_list.drop_duplicates(subset=['id'])
        

    writer = pd.ExcelWriter('Github_Report.xlsx', engine='openpyxl')
    master_list.to_excel(writer, sheet_name="ghevents", index=False)
    writer.save()                   

GitHub_project()

