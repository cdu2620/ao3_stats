from flask import Flask, render_template, redirect, url_for, request, session
import AO3  
import dill
import operator
from datetime import datetime, timedelta
import secrets
import matplotlib
import json
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

app.secret_key = secrets.token_hex()

def month_year_to_datetime(month, year):
    return datetime(year, month, 1)

def is_within_year(dt, days):
    today = datetime.now()
    ago = today - timedelta(days=days)
    return ago <= dt <= today

def check_date(work, time):
    workDate = month_year_to_datetime(int(work.month), int(work.year))
    if (time == 1 and is_within_year(workDate, 30)) \
        or (time == 6 and is_within_year(workDate, 183)) \
        or (time == 12 and is_within_year(workDate, 365)) or time == 100:
        return True 
    return False

def get_stats(login, date):
    fandomVals = {}
    wordCounts = []
    totalWordCount = 0
    tags = []
    if 'history' in session:
        history = dill.loads(session['history'])
    else:
        history = login.get_history()
        session['history'] = dill.dumps(history)
    mostVisited = 0
    visitedWork = None
    for i in range(len(history)):
        try:
            work = AO3.Work(history[i][0].id, session=login)
            if check_date(history[i][2], int(date)):
                totalWordCount += work.words
                wordCounts.append(work.words)       
                tags.append(work.tags)
                if history[i][1] > mostVisited:
                    mostVisited = history[i][1]
                    visitedWork = work
                if work.fandoms[0] not in fandomVals:
                    fandomVals[work.fandoms[0]] = 1
                else:
                    fandomVals[work.fandoms[0]] += 1
        except:
            pass
    labels = fandomVals.keys()        
    values = fandomVals.values()
    # Create the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    imgUrl = f"static/images/{date}_plot.png"
    plt.savefig(imgUrl)
    flattened_tags = [element for sublist in tags for element in sublist]
    tagCount = {}
    for tag in flattened_tags:
        if tag not in tagCount:
            tagCount[tag] = 1
        else:
            tagCount[tag] +=1
    if len(tagCount) >= 5:
        tagCount = dict(sorted(tagCount.items(), key=operator.itemgetter(1), reverse=True)[:5])
    return (tagCount, mostVisited, visitedWork, totalWordCount, imgUrl)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = AO3.Session(request.form['username'], request.form['password'])
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        try: 
            return redirect(url_for('home', ao3user = request.form['username']))
        except:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/home')
def home():
  return render_template('index.html', ao3user=request.args.get('ao3user'))

@app.route('/stats')
def stats():
    login = AO3.Session(session['username'], session['password'])
    time = request.args.get("time") 
    (tags, mostVisitedWork, visitedWork, totalWordCount, imgUrl) = get_stats(login, time)
    return render_template('stats.html', tags = tags, mostVisited = mostVisitedWork, visitedWork = visitedWork, wordCount = totalWordCount, url=imgUrl)