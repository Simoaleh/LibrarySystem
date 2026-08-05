"""Seed sample data: books, borrowers, borrow records, and reviews."""
import json
from datetime import date, timedelta

import nlp
from app import app
from models import DAYS_PER_LOAN, BorrowRecord, Borrower, Book, Review, db

BOOKS = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "Fiction",
     "description": "A novel about love, wealth, and the American dream in the roaring twenties.", "copies": 3},
    {"title": "1984", "author": "George Orwell", "category": "Dystopian Fiction",
     "description": "A chilling vision of a totalitarian future ruled by surveillance and propaganda.", "copies": 4},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Fiction",
     "description": "A story of racial injustice and childhood innocence in the American South.", "copies": 2},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "category": "Romance",
     "description": "A witty romance about manners, marriage, and misunderstanding.", "copies": 2},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "category": "Fantasy",
     "description": "A hobbit's unexpected adventure to help dwarves reclaim their mountain kingdom.", "copies": 3},
    {"title": "Dune", "author": "Frank Herbert", "category": "Science Fiction",
     "description": "An epic saga of politics, religion, and power on a desert planet.", "copies": 2},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "category": "History",
     "description": "A brief history of humankind from hunter-gatherers to the age of AI.", "copies": 3},
    {"title": "The Art of War", "author": "Sun Tzu", "category": "Philosophy",
     "description": "Ancient Chinese treatise on strategy, leadership, and tactics.", "copies": 2},
    {"title": "Clean Code", "author": "Robert C. Martin", "category": "Programming",
     "description": "A handbook of agile software craftsmanship and readable code.", "copies": 4},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": "Programming",
     "description": "Practical advice for turning a developer into a pragmatic programmer.", "copies": 3},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "category": "Fantasy",
     "description": "A young wizard's first year at Hogwarts School of Witchcraft and Wizardry.", "copies": 5},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "category": "Science",
     "description": "An accessible exploration of the universe, black holes, and time.", "copies": 2},
]

BORROWERS = [
    ("Maria", "Santos", "maria.santos@example.com", "09171234567"),
    ("John", "Dela Cruz", "john.dc@example.com", "09181234568"),
    ("Ana", "Reyes", "ana.reyes@example.com", "09191234569"),
    ("Jose", "Garcia", "jose.garcia@example.com", "09201234570"),
    ("Luz", "Mendoza", "luz.mendoza@example.com", "09211234571"),
]

REVIEWS = [
    (0, "A masterpiece of beautiful prose and unforgettable characters.", 5),
    (1, "Depressingly bleak and tedious from start to finish.", 1),
    (2, "Important themes but it dragged on too long for me.", 3),
    (4, "A fun adventure story, perfect for a lazy weekend.", 4),
    (6, "An interesting and informative overview of human history.", 4),
    (5, "Overhyped, dense, and honestly quite boring.", 2),
]


def seed():
    with app.app_context():
        db.create_all()
        if Book.query.count():
            print("Database already seeded.")
            return

        books = []
        for b in BOOKS:
            book = Book(
                title=b["title"], author=b["author"], category=b["category"],
                description=b["description"], copies=b["copies"],
                keywords=", ".join(nlp.keywords(f"{b['title']} {b['description']}")),
            )
            db.session.add(book)
            books.append(book)
        db.session.flush()

        borrowers = [Borrower(first_name=f, last_name=l, email=e, phone=p)
                     for f, l, e, p in BORROWERS]
        db.session.add_all(borrowers)
        db.session.flush()

        # Circulation sample: one overdue, one active, one returned.
        today = date.today()
        db.session.add_all([
            BorrowRecord(book_id=books[0].id, borrower_id=borrowers[0].id,
                         borrow_date=today - timedelta(days=20),
                         due_date=today - timedelta(days=6)),   # OVERDUE -> fine
            BorrowRecord(book_id=books[4].id, borrower_id=borrowers[1].id,
                         borrow_date=today - timedelta(days=3),
                         due_date=today + timedelta(days=11)),  # active
            BorrowRecord(book_id=books[8].id, borrower_id=borrowers[2].id,
                         borrow_date=today - timedelta(days=30),
                         due_date=today - timedelta(days=16),
                         return_date=today - timedelta(days=2)),  # returned, late
        ])

        for book_idx, text, rating in REVIEWS:
            scores = nlp.sentiment(text)
            db.session.add(Review(
                book_id=books[book_idx].id, text=text, rating=rating,
                sentiment_label=scores["label"],
                sentiment_scores=json.dumps(
                    {k: scores[k] for k in ("pos", "neg", "neu", "compound")}),
            ))

        db.session.commit()
        print("Seeded 12 books, 5 borrowers, 3 records, 6 reviews.")


if __name__ == "__main__":
    seed()