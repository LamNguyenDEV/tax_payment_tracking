from flask import Flask, render_template, request, redirect,flash
from datetime import datetime
import sqlite3, secrets
app = Flask(__name__)

# Set a secret key for session management and flashing messages
app.secret_key = secrets.token_hex(16)  # Generates a random 32-character secret key

# Path to your SQLite database
DATABASE = 'mydatabase.db'

# Function to get a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# Initialize the database (for demo purposes)
def init_db():
    with app.app_context():
        db = get_db()
# Create the table      

        db.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        company TEXT NOT NULL,
        amount DOUBLE NOT NULL,
        payment_date DATE NOT NULL,
        status TEXT NOT NULL,
        due_date TEXT
    )
''')
        db.commit()


# Home route to display users
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM payments')
    payments = cur.fetchall()
    return render_template('index.html', payments=payments)

# Home route to display payment

 # Add new payment route (using POST method to add data)   
@app.route('/add', methods=['POST'])
def add_payment():
    company = request.form['company']
    amount= request.form['amount']
    payment_date = request.form['payment_date']
    # Convert the string to a datetime object
    payment_date = datetime.strptime(payment_date,"%Y-%m-%d")
    # Now use strftime to format the datetime object into a string
    payment_date_update = payment_date.strftime("%m/%d/%Y") 
    status= request.form['status']
   
    due_date= request.form['due_date']
     # Get the current year
    current_year = datetime.now().year
     # add the 'year' to due_date variable
    if (due_date == "01/15") : # if due payment is january 15, the year of due date is current year +1
        due_date += '/'+ str(current_year+1)
    else :# if not, the year of due date is current year 
        due_date += '/' + str(current_year)  
    # print(due_date)
    db = get_db()
    db.execute('INSERT INTO payments (company, amount, payment_date, status, due_date ) VALUES (?,?,?,?,?)', (company, amount,payment_date_update,status,due_date))
    
    flash("Successfull added a new record")
    db.commit()

    return redirect('/')

print("Database created successfully!")
db = get_db()
ab =db.execute('PRAGMA table_info(users)')
for m in ab:
    print(m)

# Route to confirm and update a record
@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    db = get_db()
    payment = db.execute('SELECT * FROM payments WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        if request.form['confirm'] == 'yes':
            # Get updated values from user inputs form
            company = request.form['company']
            amount = request.form['amount']
            date = request.form['date']
            status = request.form['status']
            due_date = request.form['due_date']
             # Get the current year
            current_year = datetime.now().year
            # add the 'year' to due_date variable
            if (due_date == "01/15") : # if due payment is january 15, the year of due date is current year +1
                due_date += '/'+ str(current_year+1)
            else :# if not, the year of due date is current year 
                due_date += '/' + str(current_year)  

            # Update the record in the database
            db.execute('''
                UPDATE payments
                SET company = ?, amount = ?, payment_date = ?, status = ?, due_date = ?
                WHERE id = ?
            ''', (company, amount, date, status, due_date, id))

            db.commit()
            db.close()
            flash("Successfull updated a  record")
            return redirect('/')
        else:
            flash("Canceled update record")
            return redirect ('/')   

    return render_template('update.html', payment=payment)


#Delete record
@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id): 
    db = get_db()
    id_search = id
    curr = db.execute('SELECT * FROM payments WHERE id = ? ', (id_search,))
    selectRecords = curr.fetchall()
    # user_input = 'y'
    if request.method == 'POST':
        if request.form['user_input'] == 'yes':
            sql_delete_query = "DELETE FROM payments WHERE id = ?"
            db.execute(sql_delete_query,id_search )
            db.commit()
            print('delete sucessful')
            flash('Record deleted successfully!', 'success')
        else :
            print('Not to delete record')
            flash("  Canceled delete the record .Sucessfully !")
            return redirect('/') 
    return render_template('delete.html', id=id,selectRecords=selectRecords)        



# draft
    # if user_input =='y' or user_input == 'yes':
    #     sql_delete_query = "DELETE FROM payments WHERE id = ?"
    #     db.execute(sql_delete_query,id_search )
    #     db.commit()
    #     print('delete sucessful')
    #     flash('Record deleted successfully!', 'success')
    # else :    
    #     print('Not to delete record')
    #     flash("you choose NOT to delete the record") 
    # return  render_template('index.html', user_input=user_input,payments=payments)
  


# Search bar
@app.route('/search', methods=['GET','POST'])
def search_records():
    tax_rate=0.00
    toggle=False    
    db = get_db()
    total=0.00
    tax_due=0.00

    if request.method == 'POST':
        toggle=True
        query_search= request.form['due_date_query']
        tax_rate= request.form['rate']
        tax_rate= float(tax_rate)
        #Get the current year
        current_year = datetime.now().year
        # add the 'year' to due_date variable
        if (query_search== "01/15") : # if due payment is january 15, the year of due date is current year +1
            query_search += '/'+ str(current_year+1)
        else :# if not, the year of due date is current year 
            query_search += '/' + str(current_year)  

        curr= db.execute('SELECT * FROM payments WHERE due_date = ? ', (query_search,))
        recordSearchs=curr.fetchall()
        for record in recordSearchs:
            total += record[2]
        tax_due= round((total*tax_rate/100),2) 
     
        db.commit()
        
    else:
        recordSearchs=''

        
    return render_template('search.html',recordSearchs=recordSearchs,tax_rate=tax_rate,toggle=toggle,total=total,tax_due=tax_due )

# Run the Flask application
if __name__ == '__main__':
    init_db()  # Initialize the database on startup
    app.run(debug=True)