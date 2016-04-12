from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

@app.route('/')
def showCategories():
    return "This page will show the categories."