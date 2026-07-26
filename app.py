from flask import Flask, render_template, request, jsonify, redirect, session

from ai_model import find_answer
from summarizer import summarize_text

from PyPDF2 import PdfReader
from database import get_connection

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Required for Flask sessions
app.secret_key = "ai-docs-secret-key"


# ========================================
# HOME PAGE
# ========================================

@app.route("/")
def home():

    return redirect("/signup")


# ========================================
# SIGNUP
# ========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Open signup page

    if request.method == "GET":

        return render_template("signup.html")


    # Get form data

    name = request.form.get("name")

    email = request.form.get("email")

    password = request.form.get("password")


    # Connect to database

    connection = get_connection()

    cursor = connection.cursor()


    # Check if email already exists

    cursor.execute(

        """
        SELECT id
        FROM users
        WHERE email = %s
        """,

        (email,)

    )


    existing_user = cursor.fetchone()


    if existing_user:

        cursor.close()

        connection.close()

        return "Email already registered. Please login."


    # Hash password

    hashed_password = generate_password_hash(

        password

    )


    # Insert new user

    cursor.execute(

        """
        INSERT INTO users
        (name, email, password)

        VALUES (%s, %s, %s)
        """,

        (

            name,

            email,

            hashed_password

        )

    )


    connection.commit()


    cursor.close()

    connection.close()


    # Go to login page

    return redirect("/login")


# ========================================
# LOGIN
# ========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")


    email = request.form.get("email")

    password = request.form.get("password")


    connection = get_connection()

    cursor = connection.cursor(

        dictionary=True

    )


    cursor.execute(

        """
        SELECT *

        FROM users

        WHERE email = %s
        """,

        (email,)

    )


    user = cursor.fetchone()


    cursor.close()

    connection.close()


    if not user:

        return "Invalid email or password"


    if not check_password_hash(

        user["password"],

        password

    ):

        return "Invalid email or password"


    # Store user details in session

    session["user_id"] = user["id"]

    session["user_name"] = user["name"]


    return redirect("/dashboard")
# ========================================
# LOGOUT
# ========================================

@app.route("/logout")
def logout():

    # Remove session data

    session.clear()


    # Go back to signup

    return redirect("/signup")


# ========================================
# UPLOAD PDF
# ========================================

@app.route("/upload", methods=["POST"])
def upload_document():

    if "user_id" not in session:

        return jsonify({
            "error": "Please login first"
        }), 401


    file = request.files.get("file")


    if not file:

        return jsonify({
            "error": "No file uploaded"
        }), 400


    # Read PDF

    reader = PdfReader(file)

    extracted_text = ""


    for page in reader.pages:

        text = page.extract_text()

        if text:

            extracted_text += text + "\n"


    if not extracted_text.strip():

        return jsonify({
            "error": "Could not extract text from PDF"
        }), 400


    connection = get_connection()

    cursor = connection.cursor()


    # Insert document

    cursor.execute(
        """
        INSERT INTO documents
        (filename, content, user_id)

        VALUES (%s, %s, %s)
        """,

        (
            file.filename,
            extracted_text,
            session["user_id"]
        )
    )


    # Get newly created document ID

    document_id = cursor.lastrowid


    # Record upload activity

    cursor.execute(
        """
        INSERT INTO document_activity
        (document_id, user_id, action, filename)

        VALUES (%s, %s, %s, %s)
        """,

        (
            document_id,
            session["user_id"],
            "UPLOADED",
            file.filename
        )
    )


    connection.commit()


    cursor.close()

    connection.close()


    return jsonify({

        "message":
        "PDF uploaded and stored successfully!"

    })

# ========================================
# GET USER DOCUMENTS
# ========================================

@app.route("/documents", methods=["GET"])
def get_documents():

    # Only logged-in users can view documents

    if "user_id" not in session:

        return jsonify({

            "error": "Please login first"

        }), 401


    connection = get_connection()


    cursor = connection.cursor(

        dictionary=True

    )


    # Get only this user's documents

    cursor.execute(

        """
        SELECT id, filename, uploaded_at

        FROM documents

        WHERE user_id = %s

        ORDER BY id DESC
        """,

        (session["user_id"],)

    )


    documents = cursor.fetchall()


    cursor.close()

    connection.close()


    return jsonify(documents)


# ========================================
# DELETE DOCUMENT
# ========================================

@app.route(
    "/documents/<int:document_id>",
    methods=["DELETE"]
)
def delete_document(document_id):

    if "user_id" not in session:

        return jsonify({
            "error": "Please login first"
        }), 401


    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    # Find document first

    cursor.execute(
        """
        SELECT filename

        FROM documents

        WHERE id = %s

        AND user_id = %s
        """,

        (
            document_id,
            session["user_id"]
        )
    )


    document = cursor.fetchone()


    if not document:

        cursor.close()

        connection.close()


        return jsonify({
            "error": "Document not found"
        }), 404


    # Record deletion activity

    cursor.execute(
        """
        INSERT INTO document_activity
        (document_id, user_id, action, filename)

        VALUES (%s, %s, %s, %s)
        """,

        (
            document_id,
            session["user_id"],
            "DELETED",
            document["filename"]
        )
    )


    # Delete actual document

    cursor.execute(
        """
        DELETE FROM documents

        WHERE id = %s

        AND user_id = %s
        """,

        (
            document_id,
            session["user_id"]
        )
    )


    connection.commit()


    cursor.close()

    connection.close()


    return jsonify({

        "message":
        "Document deleted successfully"

    })


# ========================================
# ASK AI
# ========================================

@app.route("/ask", methods=["POST"])
def ask_question():

    # Check login

    if "user_id" not in session:

        return jsonify({

            "error": "Please login first"

        }), 401


    data = request.get_json()


    question = data.get("question")

    document_id = data.get("document_id")


    if not question:

        return jsonify({

            "error":

            "Please enter a question"

        }), 400


    if not document_id:

        return jsonify({

            "error":

            "Please select a document"

        }), 400


    connection = get_connection()


    cursor = connection.cursor(

        dictionary=True

    )


    # Get only the user's document

    cursor.execute(

        """
        SELECT content

        FROM documents

        WHERE id = %s

        AND user_id = %s
        """,

        (

            document_id,

            session["user_id"]

        )

    )


    document = cursor.fetchone()


    cursor.close()

    connection.close()


    if not document:

        return jsonify({

            "error":

            "Document not found"

        }), 404


    # Find answer

    answer = find_answer(

        document["content"],

        question

    )


    return jsonify({

        "answer": answer

    })


# ========================================
# SUMMARIZE DOCUMENT
# ========================================

@app.route("/summarize", methods=["POST"])
def summarize_document():

    # Check login

    if "user_id" not in session:

        return jsonify({

            "error": "Please login first"

        }), 401


    data = request.get_json()


    document_id = data.get("document_id")


    if not document_id:

        return jsonify({

            "error":

            "Please select a document"

        }), 400


    connection = get_connection()


    cursor = connection.cursor(

        dictionary=True

    )


    # Get only the user's document

    cursor.execute(

        """
        SELECT content

        FROM documents

        WHERE id = %s

        AND user_id = %s
        """,

        (

            document_id,

            session["user_id"]

        )

    )


    document = cursor.fetchone()


    cursor.close()

    connection.close()


    if not document:

        return jsonify({

            "error":

            "Document not found"

        }), 404


    # Generate summary

    summary = summarize_text(

        document["content"],

        sentence_count=5

    )


    return jsonify({

        "summary": summary

    })

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/signup")

    return render_template(

        "index.html",

        user_name=session["user_name"]

    )

# ========================================
# activity history api
# ========================================

@app.route("/activity", methods=["GET"])
def get_activity():

    if "user_id" not in session:

        return jsonify({
            "error": "Please login first"
        }), 401


    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            action,
            filename,
            action_time

        FROM document_activity

        WHERE user_id = %s

        ORDER BY action_time DESC
        """,

        (
            session["user_id"],
        )
    )


    activities = cursor.fetchall()


    cursor.close()

    connection.close()


    return jsonify(activities)



# ========================================
# RUN APPLICATION
# ========================================

if __name__ == "__main__":

    app.run(

        debug=True

    )