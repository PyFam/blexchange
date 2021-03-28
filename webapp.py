from flask import Flask, render_template, request, jsonify, session, redirect
from hashlib import md5
from DBcm import UseDB

app = Flask(__name__)

app.secret_key = 'Thisismyapp'

app.config['db'] = {'host':'blexchange.mysql.pythonanywhere-services.com',
                    'user':'blexchange',
                    'password':'Nov52002#',
                    'database':'blexchange$default'}
# app.config['db'] = {'host':'localhost',
#                     'user':'incharge',
#                     'password':'iamincharge',
#                     'database':'dbexchange'}

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
            email,password = request.form['loginEmail'], md5(request.form['loginPassword'].encode('ascii')).hexdigest()
            if email and password:
                with UseDB(app.config['db']) as cursor:
                    _SQL = '''select email from users_info'''
                    cursor.execute(_SQL)
                    data = cursor.fetchall()
                    for i in data:
                        if email not in i:
                            return jsonify({'emailError':'Email not associated'})
                    _SQL = '''select password from users_info where email = %s'''
                    cursor.execute(_SQL, (email,))
                    data = cursor.fetchall()[0][0]
                    if password == data:
                        return redirect('/links')
                        session['username'] = email
                        session['login'] = True
                    return jsonify({"wrongPass":"Incorrect Password"})
            return jsonify({"missingData":"Email and password needs to be provided"})

        #signup code
        elif request.form['type'] == 'signupVal':
            # data = (request.form['name'], request.form['email'], request.form['username'], md5(request.form['password'].encode('ascii')).hexdigest(), md5(request.form['con_password'].encode('ascii')).hexdigest(), request.remote_addr, request.user_agent.browser)
            data = (request.form['name'], request.form['email'], request.form['username'], request.form['password'], request.form['con_password'], request.remote_addr, request.user_agent.browser)
            name, email, username, password, con_password, IP, brower_string = data
            if name:
                if email:
                    if username:
                        if password:
                            print(password)
                            if con_password:
                                print(con_password)
                                if password == con_password:
                                    with UseDB(app.config['db']) as cursor:
                                        _SQL = '''select email from users_info'''
                                        cursor.execute(_SQL)
                                        emails = cursor.fetchall()
                                        if len(emails) == 0:
                                            pass
                                        else:
                                            for i in emails:
                                                if email in i:
                                                    return jsonify({"usedEmail":"Email has been used by another user"})
                                        _SQL = '''insert into users_info (Name, email, username, password, IP, browser_string)
                                        values (%s, %s, %s, %s, %s)'''
                                        cursor.execute(_SQL, (name, email, username, password, IP, brower_string))
                                        session['logged_in'] = True
                                        session['username'] = username
                                        # return redirect('/links')
                                return jsonify({"passError":"Password and confirm password needs to be the same"})
                            return jsonify({"con_passWarning": "Password needs to be confirmed"})
                        return jsonify({"passWarning":"Password needs to be provided"})
                    return jsonify({"usernameWarning":"Username needs to be provided"})
                return jsonify({"emailWarning":"Valid email address needs to be provided"})
            return jsonify({"nameWarning":"Provide your name"})
            


    return render_template('login.html')


@app.route('/links', methods=['POST', 'GET'])
def links():

    if request.method == 'POST':
        if 'logged_in' in session:
            data = (request.form['link'], request.form['name'], request.form['niche'], session['username'], request.remote_addr, request.user_agent.browser)
            if request.form['link']:
                if request.form['name']:
                    if request.form['niche']:
                        with UseDB(app.config['db']) as cursor:
                            _SQL = '''insert into links_log (link, name, niche, identifier, IP, browser_string
                            values(%s, %s, %s, %s, %s)
                            '''
                            cursor.execute(_SQL, data)
                            _SQL = '''select name, niche, link, identifier'''
                            data = cursor.fetchall()
                            data = (list(i) for i in data)
                            return jsonify({"linkData":data})
                    return jsonify({"nicheEror":"You need to provide the niche"})
                return jsonify({"nameError":"name of website need to be provided"})
            return jsonify({"linkError":"link of the website needs to be provided"})
        return 'Your not logged in'
    return render_template('links.html')
    


if __name__ == '__main__':
    app.run(debug=True, port=9999)

    import webbrowser
    webbrowser.open('http://localhost:9999/')

