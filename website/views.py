import requests
import math
from flask import Blueprint, render_template, request, flash, jsonify, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Receipt
from . import db
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('SVG')
import seaborn as sns

# instantiate blueprint for website
views = Blueprint('views', __name__)
options = ['Pie Chart', 'Bar Chart', 'Horizontal Bar Chart']
options2 = ['Classic', 'Solarize_Light2', 'Dark Background', 'BMH', 'Fast', 'Fivethirtyeight', 'Ggplot', 'Grayscale', 'Tableau-colorblind10', 'Classic_test_patch']

# endpoint for root of webpage
@views.route('/', methods=['GET', 'POST'])
@login_required # yes you have to login to come and play here ;)

# first page you see after login
def home():
   return render_template("home.html", user=current_user)

# endpoint for deleting items from receipt database
@views.route('/delete-item', methods=['POST'])
def delete_item():  
    item = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    itemId = item['itemId']
    item = Receipt.query.get(itemId)
    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()

    return jsonify({})

# endpoint for uploading files to server and sending them to API for OCR
@views.route('/upload', methods=['POST'])
def upload_file():

    # save file from user
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save('./' + filename)
        
        # set API access url
        url = 'https://app.nanonets.com/api/v2/OCR/Model/728b9baa-823f-4883-a452-1c0301f21361/LabelFile/?async=false'

        # open saved file
        data = {'file': open(filename, 'rb')}

        # send saved file to API with authentication key and save JSON reply
        response = requests.post(url, auth=requests.auth.HTTPBasicAuth('1c67fd51-cfa6-11ee-864a-baf362ce6189', ''), files=data)
       
        # begin the text juggle to extract the right json data
        price_list = []
        item_list = []
        quantity_list = []
        receipt_list = response.text.split(',') # split the json into an array using , as delimiter
        
        # take the Merchant_Name, Receipt_Number, Date, Description, Price and Quantity from array and append to individual arrays 
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Merchant_Name\"']:
           merch = receipt_list[position + 6].split(':')
           Merchant_Name = merch[1].replace('\"', '')
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Receipt_Number\"']:
           rec = receipt_list[position + 6].split(':')
           Receipt_Number = rec[1].replace('\"', '')
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Date\"']:
           dat = receipt_list[position + 6].split(':')
           Date = dat[1].replace('\"', '')
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Description\"']:
           ite = receipt_list[position + 6].split(':')
           ite2 = ite[1].replace('%', '')
           item_list.append(ite2.replace('\"', ''))
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Price\"']:
           pri = receipt_list[position + 6].split(':')
           pri2 = pri[1].replace("EACH", "")
           price_list.append(pri2.replace('\"', ''))
        for position in [position for position, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Quantity\"']:
           quan = receipt_list[position + 6].split(':')
           quantity_list.append(quan[1].replace('\"', ''))

        # pack arrays so they are all equal in size incase of missing OCR data
        if len(quantity_list) < len(item_list):
           for i in range(len(item_list)):
              quantity_list.append('1')
        if len(price_list) < len(item_list):
           for i in range(len(item_list)):
              price_list.append('0')

        # error checking print statements kept due to nature of OCR to often miss things, prints to server terminal
        print(response.text)
        print(len(price_list))
        print(len(item_list))
        print(len(quantity_list))

        # add new receipt to receipt database
        for item in range(len(item_list)):
           new_item = Receipt(user_id=current_user.id, date=Date, receipt_number=Receipt_Number, merchant_name=Merchant_Name, price=price_list[item], item_name=item_list[item], quantity=quantity_list[item])
           db.session.add(new_item) 
           db.session.commit()

        flash('Receipt added!', category='success')

        return render_template("home.html", user=current_user)

    return 'No file uploaded'

# endpoint for dashboard 
@views.route('/dashboard', methods=['GET'])
def dashboard():

    # save merchant name and item pricing to dictionary
    results = db.session.query(Receipt.merchant_name, Receipt.price).filter_by(user_id=current_user.id).all()
    merchant_names, prices = zip(*results)
    new_prices = []
    
    # clean up input price data from JSON so as to be a number
    for price in prices:
        cleaned_price = price.replace(' ', '').replace('$', '')
        integer_price = float(cleaned_price)
        new_prices.append(integer_price)
    plt.rcParams.update(plt.rcParamsDefault) # setup plot of data with matplotlib
    plt.rcParams.update({'figure.autolayout': True}) 

    # select style of plot based on settings endpoint
    if session.get('selected_option2') == "Classic":
        plt.style.use("classic")
    elif session.get('selected_option2') == "Solarize_Light2":
        plt.style.use("Solarize_Light2")
    elif session.get('selected_option2') == "Dark Background":
        plt.style.use("dark_background")
    elif session.get('selected_option2') == "BHM":
        plt.style.use("bhm")
    elif session.get('selected_option2') == "Fast":
        plt.style.use("fast")
    elif session.get('selected_option2') == "Fivethirtyeight":
        plt.style.use("fivethirtyeight")
    elif session.get('selected_option2') == "Ggplot":
        plt.style.use("ggplot")
    elif session.get('selected.option2') == "Grayscale":
        plt.style.use("grayscale")
    elif session.get('selected_option2') == "Tableau-colorblind10":
        plt.style.use("tableau-colorblind10")
    elif session.get('selected_option2') == "Classic_test_patch":
        plt.style.use("_classic_test_patch")

    # plot and save file to server
    if session.get('selected_option') == "Pie Chart":

        plt.figure(figsize=(8,8))
        plt.pie(new_prices, labels=merchant_names, autopct='%1.1f%%')
        plt.title('Pie Chart of Prices by Merchant')
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()
    elif session.get('selected_option') == "Bar Chart":
        plt.figure(figsize=(8,8))
        plt.bar(merchant_names, new_prices)
        plt.xlabel('Merchant Names')
        plt.ylabel('Prices')
        plt.title('Bar Chart of Prices by Merchant')
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()
    elif session.get('selected_option') == "Horizontal Bar Chart":
        plt.figure(figsize=(8,8))
        plt.barh(merchant_names, new_prices)
        plt.xlabel('Prices')
        plt.ylabel('Merchant Name')
        plt.title('Horizontal Bar Chart of Prices by Merchant')
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()

    return render_template("dashboard.html", user=current_user)

# endpoing for settings for matplotlib plot in the dashboard endpoint
@views.route('/settings', methods=['POST', 'GET'])
def settings():
    selected_option = None
    selected_option2 = None
    if request.method == 'POST':

        # Get the selected option from the form
        selected_option = request.form.get('dropdown')
        selected_option2 = request.form.get('dropdown2')
        session['selected_option'] = selected_option
        session['selected_option2'] = selected_option2

    return render_template('settings.html', options=options, options2=options2, selected_option=selected_option, selected_option2=selected_option2, user=current_user)

# endpoint for updating receipt database from changes made in the javascript table in the home template
@views.route('/update-item', methods=['POST'])
def update_data():
    print("in update function")
    item_data = json.loads(request.data)  # this function expects a JSON from the INDEX.js file
    itemId = item_data['itemId']
    updated_merchant_name = item_data['merchant_name']  
    updated_item_name = item_data['item_name']
    updated_price = item_data['price']
    updated_quantity = item_data['quantity']
    updated_date = item_data['date']
    updated_receipt_number = item_data['receipt_number']

    receipt = Receipt.query.get(itemId)
    print(updated_merchant_name)

    if receipt and receipt.user_id == current_user.id:

        # Update the fields with new values from the updated_data
        receipt.item_name = updated_item_name
        receipt.price = updated_price
        receipt.receipt_number = updated_receipt_number
        receipt.quantity = updated_quantity
        receipt.merchant_name = updated_merchant_name

        db.session.commit()

    return jsonify({})
