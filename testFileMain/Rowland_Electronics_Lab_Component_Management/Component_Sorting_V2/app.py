from cs50 import SQL
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import os


app = Flask(__name__)

db = SQL("sqlite:///components.db")

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/newComponent", methods=["POST", "GET"])
def newComponent():
    lastBin = db.execute("SELECT MAX(binID) FROM partIndex")[0]['MAX(binID)']
    lastComp = db.execute("SELECT MAX(ID) FROM partIndex")[0]['MAX(ID)']
    if not isinstance(lastComp, int):
        lastComp = 0
    if not isinstance(lastBin, int):
        lastBin = 1
    currentBinContents = db.execute("SELECT * FROM partIndex WHERE binID = ?", lastBin)

    return render_template("newComponent.html", currentBinContents = currentBinContents, lastBin = lastBin, newComp = (lastComp + 1))

@app.route("/addNewComponent", methods=["POST", "GET"])
def addNewComponent():
    binID = request.form.get("binID")
    compID = request.form.get("compID")
    compName = request.form.get("compName")
    qty = request.form.get("qty")
    type = request.form.get("type")
    functionality = request.form.get("functional")

    now = datetime.now()
    dateAndTime = now.strftime("%Y-%m-%d_%H:%M:%S")

    rows = db.execute("SELECT * FROM partIndex WHERE ID = ?", compID)

    if not rows:
        db.execute("INSERT INTO partIndex (ID, binID, name, type, functionality, qty, dateAndTime) VALUES(?, ?, ?, ?, ?, ?, ?)", compID, binID, compName, type, functionality, qty, dateAndTime)

    currentBinContents = db.execute("SELECT * FROM partIndex WHERE binID = ?", binID)
    lastComp = db.execute("SELECT MAX(ID) FROM partIndex")[0]['MAX(ID)']
    return render_template("newComponent.html", currentBinContents = currentBinContents, lastBin = binID, newComp = (lastComp + 1), type = type)

@app.route("/diffBin", methods=["POST", "GET"])
def diffBin():
    binID = request.form.get("binID")
    type = request.form.get("type")

    currentBinContents = db.execute("SELECT * FROM partIndex WHERE binID = ?", binID)
    lastComp = db.execute("SELECT MAX(ID) FROM partIndex")[0]['MAX(ID)']
    return render_template("newComponent.html", currentBinContents = currentBinContents, lastBin = binID, newComp = (lastComp), type = type)

@app.route("/newBin", methods=["POST"])
def newBin():
    lastBin = db.execute("SELECT MAX(binID) FROM partIndex")[0]['MAX(binID)']
    lastComp = db.execute("SELECT MAX(ID) FROM partIndex")[0]['MAX(ID)']
    if not isinstance(lastComp, int):
        lastComp = 0
    if not isinstance(lastBin, int):
        lastBin = 1

    currentBinContents = db.execute("SELECT * FROM partIndex WHERE binID = ?", (lastBin + 1))

    return render_template("newComponent.html", currentBinContents = currentBinContents, lastBin = (lastBin + 1), newComp = (lastComp + 1))

@app.route("/delete", methods=["POST", "GET"])
def delete():
    data = request.get_json()
    component_id = data['id']

    db.execute("DELETE FROM partIndex WHERE ID = ?", component_id)

    return jsonify({'result': 'success'})

@app.route("/deleteFromSearch", methods=["POST", "GET"])
def deleteFromSearch():
    data = request.get_json()
    component_id = data['id']

    db.execute("DELETE FROM partIndex WHERE ID = ?", component_id)

    return jsonify({'result': 'success'})

@app.route("/search", methods=["POST"])
def search():
    return render_template("search.html")

@app.route("/searching", methods=["POST"])
def searching():
    lastSearchedName = request.form.get("nameSearchBox")
    lastSearchedID = request.form.get("IDSearchBox")
    lastSearchedBox = request.form.get("boxSearchBox")
    lastSearchedBin = request.form.get("binSearchBox")
    searchTermName = "%" + lastSearchedName + "%"
    searchTermID = "%" + lastSearchedID + "%"
    searchTermBox = "%" + lastSearchedBox + "%"
    searchTermBin = "%" + lastSearchedBin + "%"

    componentsList = db.execute("SELECT * FROM partIndex JOIN binIndex ON partIndex.binID = binIndex.binID WHERE partIndex.name LIKE ? AND partIndex.ID LIKE ? AND partIndex.binID LIKE ? AND binIndex.boxID LIKE ?", searchTermName, searchTermID, searchTermBin, searchTermBox)
    return render_template("search.html", componentsList = componentsList, lastSearchedName = lastSearchedName, lastSearchedID = lastSearchedID, lastSearchedBin = lastSearchedBin, lastSearchedBox = lastSearchedBox)

@app.route("/history", methods=["POST"])
def history():

    currentBinContents = db.execute("SELECT * FROM partIndex ORDER BY dateAndTime DESC")
    return render_template("history.html",currentBinContents = currentBinContents)

@app.route("/backups", methods=["POST"])
def backups():
    backup_dates = sorted(os.listdir('dbBackups'), reverse=True)
    return render_template("backups.html", backup_dates=backup_dates)

@app.route('/create_backup', methods=["POST"])
def create_backup():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"{formatted_date}.db"
    subprocess.run(["sqlite3", "components.db", f".backup dbBackups/{filename}"])

    backup_dates = sorted(os.listdir('dbBackups'), reverse=True)
    return render_template("backups.html", backup_dates=backup_dates)

@app.route("/download_backup/<date>")
def download_backup(date):
    return send_from_directory('dbBackups', date, as_attachment=True)

@app.route("/boxManagement", methods=["POST"])
def boxManagement():
    lastBox = request.form.get("boxID");
    if not lastBox:
        lastBox = 1
    bins = db.execute("SELECT * FROM binIndex WHERE boxID = ?", lastBox)
    boxContents = db.execute("SELECT * FROM partIndex JOIN binIndex ON partIndex.binID = binIndex.binID WHERE binIndex.boxID = ?",lastBox)
    boxInfo = db.execute("SELECT * FROM boxIndex WHERE boxID = ?", lastBox)
    if boxInfo:
        boxName = boxInfo[0]['boxName']
        boxDesc = boxInfo[0]['boxDesc']
    else:
        boxName = ""
        boxDesc = ""
    return render_template("boxManagement.html", lastBox = lastBox, bins = bins, boxContents = boxContents, boxName = boxName, boxDesc = boxDesc)

@app.route("/updateBoxDesc", methods=["POST"])
def updateBoxDesc():
    lastBox = request.form.get("boxID");
    enteredBoxDesc = request.form.get("desc");
    enteredBoxName = request.form.get("name");
    bins = db.execute("SELECT * FROM boxIndex WHERE boxID = ?", lastBox)
    boxName = enteredBoxName
    boxDesc = enteredBoxDesc

    if not lastBox:
        boxInfo = db.execute("SELECT * FROM boxIndex WHERE boxID = ?", lastBox)
        boxContents = db.execute("SELECT * FROM partIndex JOIN binIndex ON partIndex.binID = binIndex.binID WHERE binIndex.boxID = ?",lastBox)
        return render_template("boxManagement.html", lastBox = lastBox, bins = bins, boxContents = boxContents, boxName = boxName, boxDesc = boxDesc)

    if not bins:
        db.execute("INSERT INTO boxIndex (boxID, boxName, boxDesc) VALUES (?, ?, ?)", lastBox, enteredBoxName, enteredBoxDesc)
    else:
        db.execute("UPDATE boxIndex SET boxName = ?, boxDesc = ? WHERE boxID = ?", enteredBoxName, enteredBoxDesc, lastBox)

    boxInfo = db.execute("SELECT * FROM boxIndex WHERE boxID = ?", lastBox)
    boxContents = db.execute("SELECT * FROM partIndex JOIN binIndex ON partIndex.binID = binIndex.binID WHERE binIndex.boxID = ?",lastBox)
    return render_template("boxManagement.html", lastBox = lastBox, bins = bins, boxContents = boxContents, boxName = boxName, boxDesc = boxDesc)

@app.route("/addBin", methods=["POST"])
def addBin():
    lastBox = request.form.get("boxID");
    newBin = request.form.get("binID");
    db.execute("INSERT INTO binIndex (binID, boxID) VALUES(?, ?)", newBin, lastBox)
    bins = db.execute("SELECT * FROM binIndex WHERE boxID = ?", lastBox)
    return render_template("boxManagement.html", lastBox = lastBox, bins = bins)
