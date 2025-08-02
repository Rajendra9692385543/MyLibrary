## 📚 MyLibrary – Smart Library Management System  
A role-based platform to manage library books, track borrow history, and streamline user management for institutions.

🚀 Features

📖 Book Management  
➤ Add books manually (ISBN, title, author)  
➤ Upload Excel sheet to bulk insert books  
➤ View all books with availability, return date & added date

📤 Excel Upload Support  
➤ Supports `.xlsx` files with columns:  
- `isbn`, `title`, `author`  
➤ Validates required fields before upload

👤 User Management  
➤ Add users (student, faculty, admin, superadmin)  
➤ Search users by name  
➤ Edit or delete user entries  
➤ Role-based restriction: Admins can't create/edit other admins

🔐 Role-Based Dashboards  
➤ Superadmin & Admin: full access to user/book management  
➤ Faculty & Student: view borrowed books from their own account  

📚 Borrow & Return  
➤ Admins can issue books by ISBN + Reg No  
➤ Select expected return date  
➤ Return books manually by ISBN & Reg No  
➤ Tracks borrowing status with timestamps

📊 Borrow History  
➤ Each user can view their personal borrow history  
➤ Includes book title, issue date, due date, and return status

📞 Contact Admin Page  
➤ Shows librarian contact (email, phone) for support  
➤ Linked in homepage for quick access

🛠️ Tech Stack  
Layer | Tech  
------|------  
Frontend | HTML5, Bootstrap 5  
Backend | Flask (Python)  
Database | Supabase (PostgreSQL)  
File Handling | Pandas  
Hosting | Render / Replit / Localhost  

📥 Required Supabase Tables  
**1. users**  
Fields: name, email, reg_no, role, password  

**2. books**  
Fields: isbn, title, author, available, added_on, expected_return_date  

**3. borrow_records**  
Fields: book_id, book_name, reg_no, status, issued_by, borrowed_on, due_date, returned_on  

🔑 Default Superadmin (for testing)  
```json
{
  "name": "Super Admin",
  "email": "admin@mylibrary.com",
  "reg_no": "LIB001",
  "role": "superadmin",
  "password": "admin123"
}
🧪 Security Notes
➤ Use hashed passwords (e.g., bcrypt) in production
➤ Store Supabase credentials securely via environment variables

💡 Future Enhancements
🧾 Borrow receipt PDF generator
🔔 Email reminders before due date
📈 Borrow statistics charts for admin
📷 Book cover image upload
📱 Progressive Web App version

🧑‍💻 Created By
Rajendra
💌 rajubhaiprojects@gmail.com
🌐 GitHub: Rajendra9692385543

yaml
Copy
Edit
