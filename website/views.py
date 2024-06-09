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
import re

# instantiate blueprint for website
views = Blueprint('views', __name__)
options = ['Pie Chart', 'Bar Chart', 'Horizontal Bar Chart']
options2 = ['Classic', 'Solarize_Light2', 'Dark Background', 'BMH', 'Fast', 'Fivethirtyeight', 'Ggplot', 'Grayscale', 'Tableau-colorblind10', 'Classic_test_patch']
options3 = ['Merchant', 'Item', 'Date', 'Receipt Number']
options4 = ['Price', 'Quantity']
# endpoint for root of webpage
@views.route('/', methods=['GET', 'POST'])
@login_required # yes you have to login to come and play here ;)

# first page you see after login
def home():
   return render_template("home.html", user=current_user)

# endpoint for user settings
@views.route('/user-settings', methods=['GET'])
def user_settings():
    return render_template("user_settings.html", user=current_user)


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
        file.save('./receipts/' + filename)
        
        # set API access url and model
        url = 'https://app.nanonets.com/api/v2/OCR/Model/728b9baa-823f-4883-a452-1c0301f21361/LabelFile/?async=false'

        # open saved file
        data = {'file': open('receipts/' + filename, 'rb')}

        # send saved file to API with authentication key and save JSON reply
        response = requests.post(url, auth=requests.auth.HTTPBasicAuth('INSERT KEY HERE', ''), files=data)
       
        # begin the text juggle to extract the right json data
        price_list = []
        item_list = []
        quantity_list = []
        receipt_list = response.text.split(',') # split the json into an array using , as delimiter
        Receipt_Number = 0

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
           if "EACH" in pri[1]:
              pri2 = pri[1].replace("EACH", "")
           price_list.append(pri2.replace('\"', ''))
        for postion in [postion for postion, receipt_data in enumerate(receipt_list) if receipt_data == '\"label\":\"Line_Amount\"']:
           pri = receipt_list[postion + 6].split(':')
           pri2 = pri[1] 
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
        # Remove any HTML tags using regex
        Date = re.sub(r'<[^>]*>', '', Date)
        # Escape special characters to prevent SQL injection
        Date = Date.replace("'", "''")
        Date = Date.replace('"', '""')
        # Remove any HTML tags using regex
        Receipt_Number = re.sub(r'<[^>]*>', '', Receipt_Number)
        # Escape special characters to prevent SQL injection
        Receipt_Number = Receipt_Number.replace("'", "''")
        Receipt_Number = Receipt_Number.replace('"', '""')
        # Remove any HTML tags using regex
        Merchant_Name = re.sub(r'<[^>]*>', '', Merchant_Name)
        # Escape special characters to prevent SQL injection
        Merchant_Name = Merchant_Name.replace("'", "''")
        Merchant_Name = Merchant_Name.replace('"', '""')
        # Remove any HTML tags using regex
        filename = re.sub(r'<[^>]*>', '', filename)
        # Escape special characters to prevent SQL injection
        filename = filename.replace("'", "''")
        filename = filename.replace('"', '""')

        # add new receipt to receipt database
        for item in range(len(item_list)):
            # Remove any HTML tags using regex
            price_list[item] = re.sub(r'<[^>]*>', '', price_list[item])
            # Escape special characters to prevent SQL injection
            price_list[item] = price_list[item].replace("'", "''")
            price_list[item] = price_list[item].replace('"', '""')
            # Remove any HTML tags using regex
            quantity_list[item] = re.sub(r'<[^>]*>', '', quantity_list[item])
            # Escape special characters to prevent SQL injection
            quantity_list[item] = quantity_list[item].replace("'", "''")
            quantity_list[item] = quantity_list[item].replace('"', '""')

            new_item = Receipt(user_id=current_user.id, date=Date, receipt_number=Receipt_Number, merchant_name=Merchant_Name, price=price_list[item], item_name=item_list[item], quantity=quantity_list[item], file_name=filename)
            db.session.add(new_item) 
            db.session.commit()

        flash('Receipt added!', category='success')

        return render_template("home.html", user=current_user)

    return 'No file uploaded'

# endpoint for dashboard 
@views.route('/dashboard', methods=['GET'])
def dashboard():
    Ylist = []
    names = []
    # save merchant name and item pricing to dictionary
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
    Xlabel = 'blank'
    Ylabel ='blank'
    print(session.get('selected_option4'))
    if session.get('selected_option4') == "Price":
        Ylabel = 'Prices'
        print("prices")
        # select X axis label based on settings endpoint
        if session.get('selected_option3') == "Merchant":
            Xlabel = 'Merchant Names'
            results = db.session.query(Receipt.merchant_name, Receipt.price).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Item':
            Xlabel = 'Item Names'
            results = db.session.query(Receipt.item_name, Receipt.price).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Date':
            Xlabel = 'Dates'
            results = db.session.query(Receipt.date, Receipt.price).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Receipt Number':
            Xlabel = 'Receipt Numbers'
            results = db.session.query(Receipt.receipt_number, Receipt.price).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)

    elif session.get('selected_option4') == 'Quantity':
        Ylabel = 'Quantities'
        # select X axis label based on settings endpoint
        if session.get('selected_option3') == 'Merchant':
            Xlabel = 'Merchant Names'
            results = db.session.query(Receipt.merchant_name, Receipt.quantity).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Item':
            Xlabel = 'Item Names'
            results = db.session.query(Receipt.item_name, Receipt.quantity).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Date':
            Xlabel = 'Dates'
            results = db.session.query(Receipt.date, Receipt.quantity).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)
        elif session.get('selected_option3') == 'Receipt Number':
            Xlabel = 'Receipt Numbers'
            results = db.session.query(Receipt.receipt_number, Receipt.quantity).filter_by(user_id=current_user.id).all()
            names, values = zip(*results)
            YList = []
            # clean up input price data from JSON so as to be a number
            for value in values:
                cleaned_value = value.replace(' ', '').replace('$', '')
                integer_value = float(cleaned_value)
                Ylist.append(integer_value)



    user_agent = request.headers.get('User-Agent')
    user_agent = user_agent.lower()
    if "iphone" or "android" in user_agent:
        plt.figure(figsize=(4,4))
    else:
        plt.figure(figsize=(16,16))
    # plot and save file to server
    if session.get('selected_option') == "Pie Chart":

        plt.pie(Ylist, labels=names, autopct=lambda p : '{:.0f}%'.format(p),
        startangle=90, pctdistance=0.85, labeldistance=1.1,
        textprops={'size': 'smaller', 'rotation_mode': 'anchor'})
        plt.axis('equal')

        plt.suptitle('Pie Chart of ' + Xlabel + ' by ' + Ylabel, y=1.1)
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()
    elif session.get('selected_option') == "Bar Chart":
        plt.bar(names, Ylist)
        plt.xticks(rotation=45, ha='right', fontsize=6)
        plt.xlabel(Xlabel)
        plt.ylabel(Ylabel)
        plt.suptitle('Bar Chart of ' + Xlabel + ' by ' + Ylabel, y=1.1)
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()
    elif session.get('selected_option') == "Horizontal Bar Chart":
        plt.barh(names, Ylist)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=6)
        plt.xlabel(Ylabel)
        plt.ylabel(Xlabel)
        plt.suptitle('Horizontal Bar Chart of ' + Ylabel + ' by '+ Xlabel, y=1.1)
        plt.savefig('./website/static/images/chart.png', bbox_inches="tight")
        plt.close()

    return render_template("dashboard.html", user=current_user)

# endpoing for settings for matplotlib plot in the dashboard endpoint
@views.route('/settings', methods=['POST', 'GET'])
def settings():
    selected_option = None
    selected_option2 = None
    selected_option3 = None
    selected_option4 = None
    if request.method == 'POST':

        # Get the selected option from the form
        selected_option = request.form.get('dropdown')
        selected_option2 = request.form.get('dropdown2')
        selected_option3 = request.form.get('dropdown3')
        selected_option4 = request.form.get('dropdown4')
        session['selected_option'] = selected_option
        session['selected_option2'] = selected_option2
        session['selected_option3'] = selected_option3
        session['selected_option4'] = selected_option4

    return render_template('settings.html', options=options, options2=options2, selected_option=selected_option, selected_option2=selected_option2, options3=options3, selected_option3=selected_option3, options4=options4, selected_option4=selected_option4, user=current_user)

# endpoint for updating receipt database from changes made in the javascript table in the home template
@views.route('/update-item', methods=['POST'])
def update_data():
    print("in update function")
    item_data = json.loads(request.data)  # this function expects a JSON from the INDEX.js file
    itemId = item_data['itemId']
    # Remove any HTML tags using regex
    updated_merchant_name = re.sub(r'<[^>]*>', '', item_data['merchant_name'])
    # Escape special characters to prevent SQL injection
    updated_merchant_name = updated_merchant_name.replace("'", "''")
    updated_merchant_name = updated_merchant_name.replace('"', '""')
    # Remove any HTML tags using regex
    updated_item_name = re.sub(r'<[^>]*>', '', item_data['item_name'])
    # Escape special characters to prevent SQL injection
    updated_item_name = updated_item_name.replace("'", "''")
    updated_item_name = updated_item_name.replace('"', '""')
    # Remove any HTML tags using regex
    updated_price = re.sub(r'<[^>]*>', '', item_data['price'])
    # Escape special characters to prevent SQL injection
    updated_price = updated_price.replace("'", "''")
    updated_price = updated_price.replace('"', '""')
    # Remove any HTML tags using regex
    updated_quantity = re.sub(r'<[^>]*>', '', item_data['quantity'])
    # Escape special characters to prevent SQL injection
    updated_quantity = updated_quantity.replace("'", "''")
    updated_quantity = updated_quantity.replace('"', '""')
    # Remove any HTML tags using regex
    updated_date = re.sub(r'<[^>]*>', '', item_data['date'])
    # Escape special characters to prevent SQL injection
    updated_date = updated_date.replace("'", "''")
    updated_date = updated_date.replace('"', '""')
    # Remove any HTML tags using regex
    updated_receipt_number = re.sub(r'<[^>]*>', '', item_data['receipt_number'])
    # Escape special characters to prevent SQL injection
    updated_receipt_number = updated_receipt_number.replace("'", "''")
    updated_receipt_number = updated_receipt_number.replace('"', '""')

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

