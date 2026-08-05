# Library Management System — Next Steps

## What's missing (referenced but not yet built)

These templates are referenced by routes in `app.py` but **do not exist** in `templates/`.
Visiting these routes currently throws a 500 `TemplateNotFound`.

| Missing file              | Used by route                          | What it should contain                                     |
|---------------------------|----------------------------------------|------------------------------------------------------------|
| `templates/borrower_form.html` | `GET/POST /borrowers/add` (`add_borrower`, app.py:140) | Add-borrower form: name, email, phone. Mirror `book_form.html`. |
| `templates/borrower_detail.html` | `GET /borrowers/<id>` (`borrower_detail`, app.py:156) | Borrower info, borrow history table (borrowed/due/returned/fine), total fine, Return button. |
| `templates/receipt.html`  | `GET /receipt/<record_id>` (`receipt`, app.py:191)   | Receipt page showing `text`, `token_count` from the NLTK parse. |

> Note: `add_borrower` uses NLTK to split the full name into first/last automatically
> (`nlp.name_tokens`), so the form only needs a single `name` field.

## UI dead-ends / missing navigation

- `book_detail.html` has a **Borrow** form, but there is no link to `book_detail` from
  `books.html` rows for non-view actions, and **no way to see a borrower's active loans**
  (the borrow action redirects to `borrower_detail`).
- There is **no "Return book" UI** anywhere except the future `borrower_detail` template.
- `base.html` nav only links Books / Search / Borrowers. The index `/` just redirects to Books.

## Minor issues

- `books.html` uses inline `style="display:inline"` on the delete form — should move to a
  `.inline` class in `style.css`.
- `app.py` runs with `debug=True` and a hardcoded `SECRET_KEY` (dev-only, fine for now but
  should be env-configurable).
- `requirements.txt` has no version pins.

## Suggested roadmap (in order)

1. **Fix the 500s** — add `borrower_form.html`, `borrower_detail.html`, `receipt.html`.
2. **Wire up circulation flow** — return button in `borrower_detail`, link detail pages
   between borrowers ↔ books.
3. **Tighten the CSS/JS** — replace inline `display:inline`, add a `.inline` utility class,
   make delete confirms consistent (`.danger` forms already auto-confirm via `app.js`).
4. **Polish** — env-based `SECRET_KEY`, pin dependencies, add flash messages on
   borrow/return/delete.
5. **Nice-to-have** — "Return" from the books view, fine summary on borrowers list,
   a dashboard/home page instead of a bare redirect.
