"""Flask app: routes + wiring. All NLTK logic lives in nlp.py."""
import json
import os
from datetime import date, timedelta

from flask import Flask, flash, redirect, render_template, request, url_for

import nlp
from models import DAYS_PER_LOAN, BorrowRecord, Borrower, Book, Review, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "lms.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lms-dev-secret")
db.init_app(app)


@app.route("/")
def index():
    records = BorrowRecord.query.all()
    stats = {
        "books": Book.query.count(),
        "available": sum(b.available for b in Book.query.all()),
        "borrowers": Borrower.query.count(),
        "active": sum(1 for r in records if not r.is_returned),
        "overdue": sum(1 for r in records if r.is_overdue),
        "fines": sum(r.fine for r in records),
    }
    return render_template("index.html", stats=stats)


# ---------------- Book management (CRUD) ----------------

@app.route("/books")
def books():
    return render_template("books.html", books=Book.query.order_by(Book.title).all())


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        copies = int(request.form.get("copies", 1) or 1)
        book = Book(
            title=title, author=author, description=description,
            category=category, copies=copies,
            keywords=", ".join(nlp.keywords(f"{title} {description}")),  # NLTK tags
        )
        db.session.add(book)
        db.session.commit()
        flash(f"Book '{book.title}' added.")
        return redirect(url_for("books"))
    return render_template("book_form.html", book=None, mode="Add")


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = db.get_or_404(Book, book_id)
    if request.method == "POST":
        book.title = request.form["title"].strip()
        book.author = request.form["author"].strip()
        book.description = request.form.get("description", "").strip()
        book.category = request.form.get("category", "").strip()
        book.copies = int(request.form.get("copies", 1) or 1)
        book.keywords = ", ".join(nlp.keywords(f"{book.title} {book.description}"))
        db.session.commit()
        flash(f"Book '{book.title}' updated.")
        return redirect(url_for("books"))
    return render_template("book_form.html", book=book, mode="Edit")


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' deleted.")
    return redirect(url_for("books"))


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = db.get_or_404(Book, book_id)
    return render_template("book_detail.html", book=book,
                           borrowers=Borrower.query.order_by(Borrower.last_name).all())


# ---------------- Search ----------------

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        q_tokens = set(nlp.normalize(q))
        q_stems = set(nlp.stem(q))
        for book in Book.query.all():
            text = f"{book.title} {book.author} {book.category} {book.keywords}"
            exact = len(set(nlp.normalize(text)) & q_tokens)
            stemmed = len(set(nlp.stem(text)) & q_stems)
            if exact or stemmed:
                results.append((book, exact * 3 + stemmed))  # rank: exact weighs more
        results.sort(key=lambda r: r[1], reverse=True)
    return render_template("search.html", q=q, results=results)


# ---------------- Reviews + sentiment ----------------

@app.route("/books/<int:book_id>/review", methods=["GET", "POST"])
def add_review(book_id):
    book = db.get_or_404(Book, book_id)
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        rating = int(request.form.get("rating", 3) or 3)
        if text:
            scores = nlp.sentiment(text)  # NLTK VADER
            db.session.add(Review(
                book_id=book.id, text=text, rating=rating,
                sentiment_label=scores["label"],
                sentiment_scores=json.dumps(
                    {k: scores[k] for k in ("pos", "neg", "neu", "compound")}),
            ))
            db.session.commit()
            flash("Review submitted.")
        return redirect(url_for("book_detail", book_id=book.id))
    return render_template("review_form.html", book=book)


# ---------------- Borrower management ----------------

@app.route("/borrowers")
def borrowers():
    return render_template("borrowers.html",
                           borrowers=Borrower.query.order_by(Borrower.last_name).all())


@app.route("/borrowers/add", methods=["GET", "POST"])
def add_borrower():
    if request.method == "POST":
        parts = nlp.name_tokens(request.form.get("name", ""))  # NLTK tokenization
        first = " ".join(parts[:-1]) if len(parts) > 1 else (parts[0] if parts else "Unknown")
        last = parts[-1] if parts else "Borrower"
        db.session.add(Borrower(
            first_name=first, last_name=last,
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
        ))
        db.session.commit()
        flash("Borrower added.")
        return redirect(url_for("borrowers"))
    return render_template("borrower_form.html", borrower=None, mode="Add")


@app.route("/borrowers/<int:borrower_id>/edit", methods=["GET", "POST"])
def edit_borrower(borrower_id):
    borrower = db.get_or_404(Borrower, borrower_id)
    if request.method == "POST":
        parts = nlp.name_tokens(request.form.get("name", ""))  # NLTK tokenization
        borrower.first_name = " ".join(parts[:-1]) if len(parts) > 1 else (parts[0] if parts else "Unknown")
        borrower.last_name = parts[-1] if parts else "Borrower"
        borrower.email = request.form.get("email", "").strip()
        borrower.phone = request.form.get("phone", "").strip()
        db.session.commit()
        flash(f"Borrower '{borrower.full_name}' updated.")
        return redirect(url_for("borrowers"))
    return render_template("borrower_form.html", borrower=borrower, mode="Edit")


@app.route("/borrowers/<int:borrower_id>/delete", methods=["POST"])
def delete_borrower(borrower_id):
    borrower = db.get_or_404(Borrower, borrower_id)
    db.session.delete(borrower)
    db.session.commit()
    flash(f"Borrower '{borrower.full_name}' deleted.")
    return redirect(url_for("borrowers"))


@app.route("/borrowers/<int:borrower_id>")
def borrower_detail(borrower_id):
    borrower = db.get_or_404(Borrower, borrower_id)
    records = (BorrowRecord.query.filter_by(borrower_id=borrower.id)
               .order_by(BorrowRecord.borrow_date.desc()).all())
    return render_template("borrower_detail.html", borrower=borrower,
                           records=records, total_fine=sum(r.fine for r in records))


# ---------------- Circulation ----------------

@app.route("/borrow", methods=["POST"])
def borrow_book():
    book = db.get_or_404(Book, int(request.form["book_id"]))
    borrower = db.get_or_404(Borrower, int(request.form["borrower_id"]))
    if book.available > 0:
        db.session.add(BorrowRecord(
            book_id=book.id, borrower_id=borrower.id,
            due_date=date.today() + timedelta(days=DAYS_PER_LOAN),  # +14 days
        ))
        db.session.commit()
        flash(f"'{book.title}' borrowed by {borrower.full_name}.")
    else:
        flash("No copies available.", "error")
    return redirect(url_for("borrower_detail", borrower_id=borrower.id))


@app.route("/return/<int:record_id>", methods=["POST"])
def return_book(record_id):
    record = db.get_or_404(BorrowRecord, record_id)
    if not record.is_returned:
        record.return_date = date.today()
        db.session.commit()
        flash(f"'{record.book.title}' returned.")
    return redirect(url_for("borrower_detail", borrower_id=record.borrower_id))


@app.route("/receipt/<int:record_id>")
def receipt(record_id):
    record = db.get_or_404(BorrowRecord, record_id)
    text = (f"Borrower: {record.borrower.full_name}\nBook: {record.book.title}\n"
            f"Borrowed: {record.borrow_date}\nDue: {record.due_date}\n"
            f"Status: {'Returned' if record.is_returned else 'Active'}\nFine: {record.fine:.2f}")
    tokens = nlp.normalize(text)  # NLTK parses the receipt text
    return render_template("receipt.html", record=record, text=text, token_count=len(tokens))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)