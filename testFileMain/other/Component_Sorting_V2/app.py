from cs50 import SQL
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime


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
    lastSearch = request.form.get("SearchBox")
    searchTerm = "%" + lastSearch + "%"
    componentsList = db.execute("SELECT * FROM partIndex JOIN binIndex ON partIndex.binID = binIndex.binID WHERE partIndex.name LIKE ?", searchTerm)
    return render_template("search.html", componentsList = componentsList, lastSearch = lastSearch)

@app.route("/history", methods=["POST"])
def history():

    currentBinContents = db.execute("SELECT * FROM partIndex ORDER BY dateAndTime DESC")
    return render_template("history.html",currentBinContents = currentBinContents)

@app.route("/backups", methods=["POST"])
def backups():
    return render_template("backups.html")

@app.route('/download_db', methods=["POST"])
def download_db():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"components{formatted_date}.db"

    return send_from_directory('.', 'components.db', as_attachment=True)

@app.route("/boxManagement", methods=["POST"])
def boxManagement():
    lastBox = request.form.get("boxID");
    bins = db.execute("SELECT * FROM binIndex WHERE boxID = ?", lastBox)
    return render_template("boxManagement.html", lastBox = lastBox, bins = bins)

@app.route("/addBin", methods=["POST"])
def addBin():
    lastBox = request.form.get("boxID");
    newBin = request.form.get("binID");
    db.execute("INSERT INTO binIndex (binID, boxID) VALUES(?, ?)", newBin, lastBox)
    bins = db.execute("SELECT * FROM binIndex WHERE boxID = ?", lastBox)
    return render_template("boxManagement.html", lastBox = lastBox, bins = bins)
