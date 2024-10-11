from flask import Flask, render_template, redirect, url_for, request, session
import AO3  
from datetime import datetime
import secrets
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

app.secret_key = secrets.token_hex()


def check_date(work, time):
    if (time == 1 and work.month ==  datetime.now().month and work.year == datetime.now().year) \
        or (time == 12 and work.year == datetime.now().year) \
        or (time == 6 and datetime.now().month - time <= work.month):
        return True 
    return False

def get_stats(session, date):
    fandomVals = {}
    wordCounts = []
    totalWordCount = 0
    tags = []
    history = session.get_history()
    for i in range(len(history)):
        try:
            work = AO3.Work(history[i][0].id)
            if check_date(history[i][2], int(date)):
                totalWordCount += work.words
                wordCounts.append(work.words)       
                tags.append(work.tags)
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
    imgUrl = 'static/images/new_plot.png'
    plt.savefig(imgUrl)
    return (tags, totalWordCount, imgUrl)

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
    (tags, totalWordCount, imgUrl) = get_stats(login, time)
    return render_template('stats.html', wordCount = totalWordCount, url=imgUrl)