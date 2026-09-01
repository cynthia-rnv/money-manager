from flask import Flask, request, render_template, redirect, url_for, session
import json
import os
import matplotlib.pyplot as plt
app=Flask(__name__)

#it's my second project with python and it will be more advanced than the first
#good luck to myself
#this is the function for having the amount of the transaction
income = []
expense =[]
transactions = {"Income" : income, "Expense" : expense}

try :
    with open("transactions.json", "r") as f:
        transactions = json.load(f)
    print("Success")
except FileNotFoundError :
    transactions={"Income" : income, "Expense" : expense}
    print("No file found, creating new data")
import datetime
today = datetime.date.today()
real_date = today.strftime("%d/%m/%Y")
INCOME= ['Family support', 'Part-time job & Side hustle play', 'Financial aid & Scholarship', 'One time inflows']
ESSENTIAL_EXPENSES = ['Rent & Dorm fees', 'Tuitition & Campus fees', 'Groceries & Meal plan', 'Commuting & Transportation', 'Course Material']
LIFESTYLE_EXPENSES = ['Social & Entraitement', 'Food & Snacks & coffee runs', 'Subscriptions', 'Personal Care']
    
#this function is for calculing the total of the amount
def calcul_amount():  
    total_expense = 0
    total_income = 0
    for item in transactions["Income"]:
        total_income += float(item["Amount"])
    for item in transactions["Expense"]:
        total_expense += float(item["Amount"])
    sold = total_income - total_expense
    return total_income, total_expense, sold

def load_language():
    language=session.get("language", "en")
    file_path=os.path.join("translations", f"{language}.json")
    with open(file_path, "r", encoding="utf-8") as file:
        translations=json.load(file)
    return translations

def load_currency():
    currency=session.get("currency", "MGA")
    with open("translations/currency.json", "r", encoding="utf-8") as file:
        currencies = json.load(file)
    return currencies[currency]

def load_amountformat(amount):
    amountformat=session.get("amountformat", "space_comma")
    if amountformat=="space_comma":
        return f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    elif amountformat=="comma_dot":
        return f"{amount:,.2f}".replace(" ", ",")
    elif amountformat=="dot_comma":
        return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(amount)


app.secret_key="money-manager-secret-key"


@app.route('/')
def home():
    total_income, total_expense, sold= calcul_amount()
    recent_income= transactions["Income"][-3:]
    recent_expense= transactions["Expense"][-3:]
    translations=load_language()
    currency=load_currency()
    
    return render_template("home.html",
                           income=load_amountformat(total_income),
                           expense=load_amountformat(total_expense),
                           sold=load_amountformat(sold),
                           recent_income=recent_income,
                           recent_expense=recent_expense,
                           transactions=translations,
                           currency=currency)
    
    
    
@app.route('/newincome')
def new_income():
    return render_template('newincome.html')


@app.route('/newexpense')
def new_expense():
    return render_template('newexpense.html')


@app.route('/historic')
def historic():
    translations=load_language()
    return render_template("historic.html",
                           income=transactions["Income"],
                           expense=transactions["Expense"],
                           transactions=translations)

@app.route('/settings', methods=["GET", "POST"])
def settings():
    translations=load_language()
    if request.method=="POST":
        language=request.form["language"]
        currency=request.form["currency"]
        amountformat=request.form["amountformat"]
        session["language"]= language
        session["currency"]= currency
        session["amountformat"]=amountformat
        return redirect(url_for("home"))
    return render_template("settings.html",
                           transactions=translations)

@app.route('/stat')
def stat():
    translations=load_language()
    total_income, total_expense,_= calcul_amount()
    income=total_income
    expense=total_expense
    labels= ["Income", "Expense"]
    values=[income, expense]
    plt.figure(figsize=(4, 5))
    bars=plt.bar(labels,
                 values,
                 width=0.45)
    bars[0].set_color("green")
    bars[1].set_color("red")
    plt.ylabel("Amount")
    plt.ylim(bottom=0)
    plt.savefig("static/income_expense.png")
    plt.close()
    expenses=transactions["Expense"]
    categories={}
    for transaction in expenses:
        category=transaction["Category"]
        amount=float(transaction["Amount"])
        if category in categories:
            categories[category]+=amount
        else:
            categories[category]=amount
    fig, ax= plt.subplots(figsize=(7, 5))
    wedges, texts=ax.pie(
        categories.values(),
        labels=categories.keys(),
        startangle=90,
        textprops=dict(color="white", weight="bold", size=10)
    )
    centre_circle=plt.Circle((0, 0), 0.55, fc="white")
    ax.add_artist(centre_circle)
    ax.legend(
        wedges,
        categories,
        title="Expense Categories",
        title_fontproperties={"weight": "bold"},
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False
        )

        
    plt.tight_layout()
    plt.savefig("static/expense_chart.png", bbox_inches="tight")
    plt.close()
    return render_template("stat.html",
                           income=income,
                           expense=expense,
                           expenses=expenses,
                           categories=categories,
                           transactions=translations)
    
@app.route('/add', methods=["POST"])
def transdtls():
    tyPE = request.form.get('transaction')
    category = request.form.get('category')
    amount = request.form.get('amount')
    date = real_date
    note = request.form.get('note')
    new_transaction={"Type":tyPE, "Category":category, "Amount": amount, "Date": date, "Note": note}
    if tyPE == "income":
        transactions["Income"].append(new_transaction)
    elif tyPE == "expense":
        transactions["Expense"].append(new_transaction)
    with open("transactions.json", "w") as f:
        json.dump(transactions, f, indent=4)
    return redirect(url_for("home"))

if __name__=="__main__":
    app.run(debug=True)

















