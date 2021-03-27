#!/usr/bin/env python3

#        ___         _____
#       |__ \    __ /__  /
#       __/ / __/ /_  / /
#      / __/ /_  __/ / / 
#     /____/  /_/   /_/
#       
# Written by Justus Languell 


# Imports
from flask import Flask,render_template,request,flash,redirect,url_for
from datetime import datetime
import time
import os
import argparse


# Setup
app = Flask(__name__)
sepr = '#$%'
tspace = '-'
path = 'messages'
boardfile = 'BOARDS'
prune = 43200 # 86400 = 1 day


if not os.path.isdir(path):
    os.mkdir(path)


def write(board,thread,name,subject,message):

    f = open(f'{path}/{board}/{thread}','a')
    f.write(f'{name}{sepr}{subject}{sepr}{message}\n')
    f.close()


def read(board,thread):

    f = open(f'{path}/{board}/{thread}','r')
    messages = []

    for l in f:
        l = l.split(sepr)
        print(l)
        messages.append(tuple(l))

    return messages


@app.route('/<board>/<thread>',methods=['GET','POST']) 
def thread(board,thread):

    if request.method == 'POST':

        name = request.form['name'].replace(sepr,'')
        message = request.form['msg'].replace(sepr,'')
        subject = request.form['subject'].replace(sepr,'')

        write(board,thread,name,subject,message)

    messages = read(board,thread)

    name = thread.split(';')
    name = name[0].replace(tspace,' ')
    thread = thread.replace(tspace,' ')

    return render_template('thread.html',
            board=board,
            thread=thread,
            name=name,
            messages=messages
    )


@app.route('/',methods=['GET']) 
def index():

    boards = [tuple(l.replace('\n','').split(':')) for l in open(boardfile)]
    return render_template('index.html',boards=boards)


@app.route('/<board>',methods=['GET','POST']) 
def board(board):

    boards = [tuple(l.replace('\n','').split(':')) for l in open(boardfile)]
    boardpaths = list(zip(*boards))[0]
    board = '/' + board

    if board in boardpaths:

        if not os.path.isdir(path+board):
            os.mkdir(path+board)

        i = boardpaths.index(board)

        if request.method == 'POST':
            name = request.form['name'].replace(' ',tspace).replace(';','.')
            name = name + ';' + str(round(time.time()))

            if not os.path.isfile(path+board+'/'+name):
                f = open(path+board+'/'+name,'x')
                f.close()
                return redirect(board+'/'+name, code=302)

        threads = os.listdir(path+board)

        threadnames = []
        for thread in threads:
            threadpath = thread
            thread = thread.split(';')

            if round(time.time()) - int(thread[1]) > prune:
                os.remove(path+board+'/'+threadpath)

            else:
                threadnames.append(thread[0].replace(tspace,' '))

        threads = zip(threads,threadnames)

        return render_template('board.html',
                    path=path,
                    board=boards[i],
                    threads=threads
        )

    else:
        return '<h1>404, page not found!</h1>'


# Entry
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-d',
        '--debug',
        help='Debug Mode',
        required=False,
        const='debug',
        nargs='?'
    )

    if parser.parse_args().debug == 'debug':
        app.run(debug=True)

    else:
        app.run(host='0.0.0.0', port=80,debug=False)
    
