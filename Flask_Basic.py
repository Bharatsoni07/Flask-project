from flask import Flask,  render_template

app = Flask(__name__,template_folder='template')

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/second")
def Bharat():
    name = "Bharat"
    return render_template('index2.html',name2 = name) 

@app.route("/Image")
def Image():
    return render_template('index3.html')


app.run(debug=True)



#  'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='CodingThunder')