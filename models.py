"""SQLAlchemy models for the Library Management System."""
from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DAYS_PER_LOAN = 14  # Number of days a book can be borrowed before it is overdue.
FINE_PER_DAY = 5.0  # Overdue fine per day.


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(100), default="")
    copies = db.Column(db.Integer, default=1)
    keywords = db.Column(db.String(300), default="")

    reviews = db.relationship("Review", backref="book", cascade="all, delete-orphan")
    records = db.relationship("BorrowRecord", backref="book", cascade="all, delete-orphan")

    @property
    def available(self):
        """Copies not currently checked out."""
        out = sum(1 for r in self.records if not r.is_returned)
        return max(0, self.copies - out)


class Borrower(db.Model):
    __tablename__ = "borrowers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, default="")
    phone = db.Column(db.String(11), default="")

    records = db.relationship("BorrowRecord", backref="borrower", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey("borrowers.id"), nullable=False)
    borrow_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def is_overdue(self):
        return not self.is_returned and date.today() > self.due_date

    @property
    def fine(self):
        """Overdue fine computed from due date (0 if not overdue)."""
        if not self.is_overdue:
            return 0.0
        return round((date.today() - self.due_date).days * FINE_PER_DAY, 2)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    sentiment_label = db.Column(db.String(20), default="")
    sentiment_scores = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
