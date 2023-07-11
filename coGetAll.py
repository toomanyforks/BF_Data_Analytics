import requests
import psycopg2
import json
import flatten_to_dict
import io

import getStateRep
import insert_records

# initializing the titles and rows list
fields = []
rows = []
urlcheck = []
listdump = []

def getsize(size):
    if size <25:
        return 1
    elif size <75:
        return 2
    elif size <200:
        return 3
    elif size <750:
        return 4
    elif 1==1:
        return 5

def getinput(domi):
    data = {}
    url = "https://api.apollo.io/v1/organizations/enrich"

    querystring = {
           "api_key": "ON_SERVER",
           "domain": domi
    }

    headers = {
           'Cache-Control': 'no-cache',
           'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    d = json.loads(response.text)


    flat = flatten_to_dict.flatten(d)

    if flat == {}:
        print(domi +" that domain doesn't exist")


    else:
        name = domi + ".csv"
        with io.open(name, "w", encoding="utf-8") as outfile:
            dic = {}
            for key in flat:
                kee = str(key)
                newkey = kee.removeprefix("organization_")
                astr = str(flat[key])
                astr = astr.replace(",", "")

                if newkey == 'estimated_num_employees':
                    newkey = 'ee'
                    cosize = getsize(int((astr)))
                    dic['size'] = cosize
                    outfile.write("size ;" + str(cosize) + "\n")
                    dic[newkey] = astr
                if newkey == 'name':
                    dic['name'] = astr
                    dic['alpha'] = astr[0]

                if newkey =='linkedin_url':
                    dic['li_url'] = astr
                if newkey == 'website_url':
                    dic['url'] = astr

                if newkey == 'primary_phone_number':
                    dic['phone'] = astr
                if newkey == 'seo_description':

                    dic['descr'] = astr

                if newkey == 'state':

                    dic['state_long'] = astr
                outfile.write(newkey + "; " + astr + "\n")

        tup =('name','alpha','url','li_url','phone','size','ee','state_long','descr','terr','rep')

        tupp = []
        state = dic['state_long']

        if dic['size'] == 3:

            ter = getStateRep.getStateTer(dic.get('size'),state)
            rep = getStateRep.getRep(dic['alpha'],ter, dic.get('size'))
            dic['terr'] = ter
            dic['rep_id'] = rep
        else:
            dic['terr'] = str(dic.get('size'))
            dic['rep_id'] = "100"

        for i in dic:
            z = "x"
            if dic.get(i) == "" or dic.get(i) == None:
                tupp.append(z)
            else:
                tupp.append(dic.get(i))


        sd = 'sd'

        tt = tuple(tupp)
        print(tupp)
        insert_records.insertInBulk(sd, tup, tt)


#domi = input("Company Domain to Lookup: ")
#getinput(domi)







