import pymongo
from flask import Flask, request, redirect, render_template
import time
from hashids import Hashids
import random
import secrets
hashids = Hashids(salt="bebektest")
client = pymongo.MongoClient("mongodb+srv://bebekbengil:BebekCRUD@cluster0.mvr0yit.mongodb.net/?retryWrites=true&w=majority")
dbmain = client.main
dbstats = client.stats

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("BebekBengil.html")

@app.route('/createLink', methods=["POST"])
def createLink():
    idInt = random.randint(0, 100000000000000000)
    hash = secrets.token_urlsafe(5)
    origin = request.json["originLink"]
    result = dbmain.indexCol.insert_one({"hash":hash, "origin":origin})
    print(result, origin)
    return {"shortenLink":"https://bebekbengil.my.id/"+hash}

@app.route("/<id>")
def redirectTo(id):
    try:
        userAgent = request.headers["user-agent"]
        cfIP = request.headers["CF-Connecting-IP"]
    except:
        userAgent = "CONNERR"
        cfIP = "CONNERR"
    accessTime = time.time()
    dbObj = dbmain.indexCol.find_one({"hash":id})
    if dbObj:  
        if "https://" in dbObj["origin"] or "http://" in dbObj["origin"]:
            redirLoc = dbObj["origin"]
        else:
            redirLoc = "https://" + str(dbObj["origin"])
        statsCol = dbstats[dbObj["hash"]]
        statsCol.insert_one({"userAgent":userAgent, "userIP":cfIP, "time":accessTime, "origin":redirLoc})
        return redirect(redirLoc, code=301)
    else:
        return redirect("https://error", code=301)

app.run(host="0.0.0.0", port=80)
