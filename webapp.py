from flask import Flask, render_template, request, jsonify, session, redirect
import json
from hashlib import md5
from DBcm import UseDB

app = Flask(__name__)

app.secret_key = 'Thisismyapp'

# app.config['db'] = {'host':'blexchange.mysql.pythonanywhere-services.com',
#                     'user':'blexchange',
#                     'password':'Nov52002#',
#                     'database':'blexchange$default'}
app.config['db'] = {'host':'localhost',
                    'user':'incharge',
                    'password':'iamincharge',
                    'database':'dbexchange'}

@app.route('/')
def index():
    # btn1, btn2 = ('login', 'signup') if 'logged_in' not in session else ('logout', None)
    if 'logged_in' not in session:    
        return render_template('index.html',
                               btn = 'login',
                               btn2 = 'signup')

    return render_template('index.html', btn='logout')

@app.route('/login', methods=['POST','GET'])
#login and signup
def do_log():
    if request.method == 'POST':
        #login code
        if request.form['type'] == 'loginVal':
            email,password = request.form['loginEmail'], md5(request.form['loginPassword'].encode()).hexdigest()
            if email and password:
                with UseDB(app.config['db']) as cursor:
                    _SQL = '''select email from users_info'''
                    cursor.execute(_SQL)
                    data = cursor.fetchall()
                    data = [i[0] for i in data]
                    print(data)
                    if email not in data:
                        return jsonify({'emailError':'Email not associated'})
                    _SQL = '''select password from users_info where email = %s'''
                    cursor.execute(_SQL, (email,))
                    data = cursor.fetchall()[0][0]
                    if password == data:
                        session['username'] = email
                        session['login'] = True
                        return redirect('/links')
                    return jsonify({"wrongPass":"Incorrect Password"})
            return jsonify({"missingData":"Email and password needs to be provided"})

        #signup code
        elif request.form['type'] == 'signupVal':
            data = (request.form['name'], request.form['email'], request.form['username'], md5(request.form['password'].encode()).hexdigest(), md5(request.form['con_password'].encode()).hexdigest(), request.remote_addr, request.user_agent.browser)
            # data = (request.form['name'], request.form['email'], request.form['username'], request.form['password'], request.form['con_password'], request.remote_addr, request.user_agent.browser)
            name, email, username, password, con_password, IP, brower_string = data
            if name:
                if email:
                    if username:
                        if password:
                            if con_password:
                                if password == con_password:
                                    with UseDB(app.config['db']) as cursor:
                                        _SQL = '''select email from users_info'''
                                        cursor.execute(_SQL)
                                        emails = cursor.fetchall()
                                        if len(emails) != 0:
                                            for i in emails:
                                                if email in i:
                                                    return jsonify({"usedEmail":"Email has been used by another user"})
                                        _SQL = '''insert into users_info (Name, email, password, IP, browser_string, username)
                                        values (%s, %s, %s, %s, %s, %s)'''
                                        cursor.execute(_SQL, (name, email, password, IP, brower_string, username))
                                        session['logged_in'] = True
                                        session['username'] = username
                                        return redirect('/links')
                                return jsonify({"passError":"Password and confirm password needs to be the same"})
                            return jsonify({"con_passWarning": "Password needs to be confirmed"})
                        return jsonify({"passWarning":"Password needs to be provided"})
                    return jsonify({"usernameWarning":"Username needs to be provided"})
                return jsonify({"emailWarning":"Valid email address needs to be provided"})
            return jsonify({"nameWarning":"Provide your name"})
            


    return render_template('login.html')


@app.route('/links', methods=['POST', 'GET'])
def links():
    with UseDB(app.config['db']) as cursor:
        if request.method == 'POST':
            data = (request.form['blogName'], request.form['niche'], request.form['url'], request.remote_addr, request.user_agent.browser)
            blogName, niche, url, *_ = data
            if blogName:
                if niche:
                    if url:
                        _SQL = '''insert into links_log(link, name, niche, identifier, IP, browser_string) values(%s, %s, %s, %s, %s, %s)'''
                        cursor.execute(_SQL, data)
        _SQL = '''select name, niche, link, identifier from links_log'''
        cursor.execute(_SQL)
        data = cursor.fetchall()
        data.reverse()
        Data = []
        Data = ([list(i) for i in data if len(Data) != 50])
        return render_template('links.html', linkData=json.dumps(data))



if __name__ == '__main__':
    app.run(debug=True, port=9999)

    import webbrowser
    webbrowser.open('http://localhost:9999/')

