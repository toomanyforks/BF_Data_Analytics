from bs4 import BeautifulSoup
import requests
import callLookup
import coLookup
import dodSizeState
import getRepInfo
import insert_records

pageindex=1
articles = []
articledate ={}
url = "https://www.defense.gov/News/Contracts/?Page=1"
for i in range(0,10):
    req = requests.get(url)
    da = BeautifulSoup(req.text, "html.parser")
    for art in da.find_all('listing-titles-only'):
        txtt = art
        artt = txtt.get("article-id")
        artd = txtt.get("publish-date-ap")
        if not artt == None and artt not in articles:
            articles.append(artt)
            articledate.update({artt:artd})

        else:

            url = "https://www.defense.gov/News/Contracts/?Page=" + str(i)
            print(url)
print(articles)


for a in articles:
    aurl = "https://www.defense.gov/News/Contracts/Contract/Article/" + a + "/"
    print(f"reviewing article : {a}")
    req = requests.get(aurl)
    da = BeautifulSoup(req.text, "html.parser")
    datea = articledate.get(a)
    for parag in da.find_all('p'):
        tx = parag.text
        if tx.__contains__("cost-plus"):

            chunks = tx.split(',')
            work = tx.split('.')
            works = work[1] + " " + work[2]
            comp = chunks[0]
            state = chunks[2]

            ruleout=["Lockheed",
                     "Boeing",
                    "General Dynamics",
                    "ManTech",
                    "Northrop",
                    "Raytheon",
                    "Rockwell Collins",
                    "BAE Systems",
                    "AECOM",
                    "L-3",
                    "L3",
                    "Sikorsky",
                    "Serco",
                    "Booz",
                    "Bechtel",
                    "Leidos",
                    "Huntington-Ingalls",
                    "Huntington Ingalls",
                    "Science Applications International Corp.",
                    "General Atomics",
                    "CACI",
                    "KBR"
                    ]
            rulebit = 1
            for rul in ruleout:
                if rul in comp:
                    rulebit = 1

            if rulebit == 1:
                #print(comp + ";" + state + ";" + date + ";" + aurl + "\n")
                getdomai = callLookup.getDom(comp)
                print (getdomai + " =  Domain for " + comp)
                if getdomai == "DNF":
                    sql = "INSERT INTO DNF (company,domain,ee) VALUES ('" + comp + "', 'DNF', -1)"
                    insert_records.updateOne(sql)
                else:
                    #domain could be found in domain lookup service but not exist in Apollo.io, so create into DNF
                    getdomain = dodSizeState.getinput(getdomai)
                    if getdomain == "DNF":
                        sql = "INSERT INTO DNF (company,domain,ee) VALUES ('" + comp + "','%s', -2)"%getdomai
                        insert_records.updateOne(sql)

                    else:
                        print(f"Getdomai: {getdomai}")
                        name = getdomain['name']
                        ee = getdomain['ee']
                        size = getRepInfo.getSizeInt(ee)
                        url = getdomai
                        statee = getdomain['state_long']
                        alpha = getdomain['alpha']
                        ter = getRepInfo.getTer(size,statee)
                        if ter ==None:
                            ter = ""

                        rep = int(getRepInfo.getRep(alpha,ter,size))

                        email = getRepInfo.getRepEmail(rep)

                        sql2 = "INSERT INTO mailer (rep_id,date,url,email,comp,ee,domain,ter,alpha,state) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        varz= (rep,datea,aurl,email,name,ee,getdomai,ter,alpha,statee)
                        insert_records.updateOnePrep(sql2,varz)
