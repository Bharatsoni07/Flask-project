from flask import Flask, render_template

app = Flask(__name__,template_folder='template')

@app.route("/Image")
def Image():
    return render_template('index3.html')

app.run(debug=True)