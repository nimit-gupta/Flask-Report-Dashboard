from flask import Flask, render_template, request, send_file, redirect, session
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import pymysql as mx
import pandas as pd
import base64
import io

app = Flask(__name__, template_folder = 'template')
app.secret_key = "abc"

@app.route("/")
def index():
   return render_template("form.html")

@app.route("/datepicker", methods=["GET","POST"])
def datepicker():
    if request.method == 'POST':
        entry_date = request.form.get("DATE")
        url_source = request.form.get("SOURCE")
        session['entry_date'] = entry_date
        session['url_source'] = url_source
        con = mx.connect(host = '127.0.0.1', port = 3306, database= 'trial_db', user = 'root', password = 'root' )
        sql = '''select 
                    * 
                from 
                    url_entry 
                where 
                    entry_date = '%(entry_date)s'
                    and url_source = '%(url_source)s'
            '''%{'entry_date': entry_date,'url_source': url_source}
        df = pd.read_sql_query(sql,con)
        return render_template("table.html", data = df.to_dict(orient='records'), entry_date = entry_date)

@app.route("/datepicker2")
def datepicker2():
    entry_date = session.get('entry_date')
    url_source = session.get('url_source')
    con = mx.connect(host = '127.0.0.1', port = 3306, database= 'trial_db', user = 'root', password = 'root' )
    sql = '''select 
                * 
            from 
                url_entry 
            where 
                entry_date = '%(entry_date)s'
                and url_source = '%(url_source)s'
        '''%{'entry_date': entry_date,'url_source': url_source}
    df = pd.read_sql_query(sql,con)
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine = 'xlsxwriter')
    df.to_excel(writer, sheet_name = 'data')
    writer.save()
    xlsx_io.seek(0)
    return send_file(xlsx_io, attachment_filename= 'test.xlsx')

@app.route("/datepicker3")
def datepicker3():
    entry_date = session.get('entry_date')
    con = mx.connect(host = '127.0.0.1', port = 3306, database= 'trial_db', user = 'root', password = 'root' )
    sql = '''select 
                 url_source as urlsource,
                 count(url_text) as urltext
            from 
                url_entry 
            where 
                entry_date = '%(entry_date)s'
            group by 
                url_source
          '''%{'entry_date': entry_date}
    df = pd.read_sql_query(sql,con)
    
    img_io = io.BytesIO()
    fig = plt.figure()
    plt.bar(df['urlsource'], df['urltext'])
    plt.xlabel("Source")
    plt.ylabel("Count of Urls")
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.title("Source Wise URL Count",fontname="Times New Roman",fontweight="bold")
    for i,j in df['urltext'].items():
        plt.annotate(str(j), xy=(i, j), fontsize = 10)
    plt.savefig(img_io, format='png')

    img_io2 = io.BytesIO()
    fig2 = plt.figure()
    x = df['urltext']
    labels = df['urlsource']
    plt.pie(x, labels = labels,autopct='%.0f%%')
    plt.title("Source Wise %",fontname="Times New Roman",fontweight="bold")
    plt.savefig(img_io2, format='png')

    img_io.seek(0)
    img_io2.seek(0)
    plot_url = base64.b64encode(img_io.getvalue()).decode()
    plot_url2 = base64.b64encode(img_io2.getvalue()).decode()
    return render_template('show.html', plot_url=plot_url, plot_url2 = plot_url2)

if __name__ == '__main__':
    app.run(debug = False)