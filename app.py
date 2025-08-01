# app.py (MyLibrary Updated Setup with Unified Dashboards)
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
from supabase import create_client, Client
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, session, jsonify

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Supabase setup
SUPABASE_URL = "https://tirasfadukvfuvhhtiwa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpcmFzZmFkdWt2ZnV2aGh0aXdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM5NDM0NTcsImV4cCI6MjA2OTUxOTQ1N30.k_XFln6rlVzP6E23Mqdfkc5nLpcPPHc_uNWJw2GV7YU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books')
def view_books():
    response = supabase.table("books").select("*").execute()
    books_data = response.data
    books = []
    for book in books_data:
        books.append({
            'title': book.get('title'),  # Changed from 'name' to 'title'
            'author': book.get('author'),
            'available': book.get('available'),
            'return_date': book.get('expected_return_date') if not book.get('available') else None
        })
    return render_template('books.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Select relevant fields including 'name'
        response = supabase.table("users").select("email, password, role, reg_no, name").eq("email", email).eq("password", password).execute()
        user_data = response.data

        if user_data:
            user = user_data[0]
            session['user'] = user['email']           # Used as 'issued_by'
            session['reg_no'] = user['reg_no']
            session['role'] = user['role']
            session['name'] = user['name']            # Optional: display purpose
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or 'role' not in session:
        return redirect(url_for('login'))

    role = session['role']

    if role in ['admin', 'superadmin']:
        return render_template('admin_dashboard.html', user=session['user'], role=role)
    elif role in ['student', 'faculty']:
        return render_template('user_dashboard.html', user=session['user'], role=role)
    else:
        return "Unauthorized", 403

@app.route('/manage-users', methods=['GET', 'POST'])
def manage_users():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    role = session['role']

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        reg_no = request.form['reg_no'].strip()
        user_role = request.form['role'].strip()
        password = request.form['password'].strip()

        if role == 'admin' and user_role in ['admin', 'superadmin']:
            return "Unauthorized to create admin/superadmin", 403

        new_user = {
            "name": name,
            "email": email,
            "reg_no": reg_no,
            "role": user_role,
            "password": password
        }

        supabase.table("users").insert(new_user).execute()
        return redirect(url_for('manage_users'))

    page = int(request.args.get('page', 1))
    search_query = request.args.get('q', '').strip()
    page_size = 5
    start = (page - 1) * page_size

    query = supabase.table("users")
    if search_query:
        query = query.ilike("name", f"%{search_query}%")

    all_users = query.select("*").execute().data or []

    if role == 'admin':
        all_users = [u for u in all_users if u['role'] not in ['admin', 'superadmin']]

    total_users = len(all_users)
    total_pages = (total_users + page_size - 1) // page_size
    paginated_users = all_users[start:start + page_size]

    return render_template(
        'manage_users.html',
        users=paginated_users,
        role=role,
        page=page,
        total_pages=total_pages,
        query=search_query
    )

# Display Manage Books Page
@app.route('/manage-books')
def manage_books():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    # Fetch all books (no grouping/summarizing)
    response = supabase.table("books").select("*").order("added_on", desc=True).execute()
    books = response.data or []

    return render_template('manage_books.html', books=books)

@app.route('/add-book', methods=['POST'])
def add_book():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    isbn = request.form['isbn'].strip()
    title = request.form['title'].strip()
    author = request.form['author'].strip()

    # Insert a single book entry
    supabase.table("books").insert({
        "isbn": isbn,
        "title": title,
        "author": author,
        "available": True,
        "added_on": datetime.now().isoformat(),
        "expected_return_date": None
    }).execute()

    return redirect(url_for('manage_books'))

# Upload Excel File and Bulk Insert
@app.route('/upload-books', methods=['POST'])
def upload_books():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    file = request.files['file']
    if not file:
        return "No file selected", 400

    try:
        df = pd.read_excel(file)
        required_cols = ['isbn', 'title', 'author']
        if not all(col in df.columns for col in required_cols):
            return "Missing required columns in Excel file", 400

        for _, row in df.iterrows():
            isbn = str(row['isbn']).strip()
            title = str(row['title']).strip()
            author = str(row['author']).strip()

            supabase.table("books").insert({
                "isbn": isbn,
                "title": title,
                "author": author,
                "available": True,
                "added_on": datetime.now().isoformat(),
                "expected_return_date": None
            }).execute()

        return redirect(url_for('manage_books'))

    except Exception as e:
        print("Upload error:", e)
        return "Error processing file", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/remove_user/<user_id>', methods=['POST'])
def remove_user(user_id):
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    target = supabase.table("users").select("role").eq("id", user_id).execute().data
    if not target:
        return "User not found", 404
    target_role = target[0]['role']

    if session['role'] == 'admin' and target_role in ['admin', 'superadmin']:
        return "Unauthorized", 403

    supabase.table("users").delete().eq("id", user_id).execute()
    return redirect(url_for('manage_users'))

@app.route('/update_user/<user_id>', methods=['POST'])
def update_user(user_id):
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    password = request.form.get('password')

    target = supabase.table("users").select("role").eq("id", user_id).execute().data
    if not target:
        return "User not found", 404
    target_role = target[0]['role']

    if session['role'] == 'admin' and (target_role in ['admin', 'superadmin'] or role in ['admin', 'superadmin']):
        return "Unauthorized", 403

    update_data = {"name": name, "email": email, "role": role}
    if password and session['role'] == 'superadmin':
        update_data["password"] = password

    supabase.table("users").update(update_data).eq("id", user_id).execute()
    return redirect(url_for('manage_users'))

@app.route('/mybooks')
def my_books():
    if 'user' not in session or 'reg_no' not in session:
        return redirect(url_for('login'))

    reg_no = session['reg_no']

    try:
        response = supabase.table("borrow_records") \
            .select("*") \
            .eq("reg_no", reg_no) \
            .order("borrowed_on", desc=True) \
            .execute()
        borrowed_books = response.data or []
    except Exception as e:
        print("Error fetching borrow records:", e)
        borrowed_books = []

    return render_template("my_books.html", books=borrowed_books)

@app.route('/borrow-book', methods=['POST'])
def borrow_book():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    reg_no = request.form.get('reg_no')
    isbn = request.form.get('isbn')
    due_date = request.form.get('due_date')

    if not (reg_no and isbn and due_date):
        return "Missing fields", 400

    # Fetch book details from ISBN
    book_response = supabase.table("books").select("id", "title", "available").eq("isbn", isbn).single().execute()
    if not book_response.data:
        return "Book not found", 400

    book = book_response.data
    if not book['available']:
        return "Book already borrowed", 400

    # Insert borrow record with issued_by (email of admin)
    borrow_data = {
        "reg_no": reg_no,
        "book_id": book["id"],
        "book_name": book["title"],
        "borrowed_on": datetime.now().isoformat(),
        "due_date": due_date,
        "status": "borrowed",
        "issued_by": session.get('user')  # Email or unique identifier
    }
    supabase.table("borrow_records").insert(borrow_data).execute()

    # Update book availability
    supabase.table("books").update({"available": False}).eq("id", book["id"]).execute()

    return redirect(url_for('view_borrowed'))

@app.route('/return-book', methods=['POST'])
def return_book():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    reg_no = request.form.get('reg_no')
    isbn = request.form.get('isbn')

    if not (reg_no and isbn):
        return "Missing fields", 400

    # Get book by ISBN
    book_res = supabase.table("books").select("id", "title").eq("isbn", isbn).single().execute()
    if not book_res.data:
        return "Book not found", 400

    book = book_res.data

    # Update borrow record
    supabase.table("borrow_records").update({
        "status": "returned",
        "returned_on": datetime.now().isoformat()
    }).eq("reg_no", reg_no).eq("book_id", book["id"]).eq("status", "borrowed").execute()

    # Mark book as available again
    supabase.table("books").update({"available": True}).eq("id", book["id"]).execute()

    return redirect(url_for('view_borrowed'))

@app.route('/get-book-title')
def get_book_title():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({"title": None, "available": None}), 400

    result = supabase.table("books").select("title", "available").eq("isbn", isbn).single().execute()
    if result.data:
        return jsonify({
            "title": result.data['title'],
            "available": result.data['available']
        })
    return jsonify({"title": None, "available": None})

@app.route('/borrowed')
def view_borrowed():
    if 'user' not in session or session.get('role') not in ['admin', 'superadmin']:
        return redirect(url_for('login'))

    # Fetch latest borrow records, most recent first
    response = supabase.table("borrow_records").select("*").order("borrowed_on", desc=True).execute()
    records = response.data or []

    return render_template("borrowed_books.html", records=records)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)