# main.py

from flask import Flask, request, jsonify, redirect, render_template, session, url_for
import random, string

from app.models import URL
from app.db import SessionLocal

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session functionality

# Form-based homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None

    if request.method == 'POST':
        original_url = request.form['url']
        db = SessionLocal()
        existing = db.query(URL).filter_by(original_url=original_url).first()

        if existing:
            short_code = existing.short_code
        else:
            short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            new_url = URL(original_url=original_url, short_code=short_code)
            db.add(new_url)
            db.commit()
        db.close()

        session['short_url'] = request.host_url + short_code
        return redirect(url_for('home'))

    if 'short_url' in session:
        short_url = session.pop('short_url')

    return render_template('index.html', short_url=short_url)


# API endpoint to shorten URL
@app.route('/shorten', methods=['POST'])
def shorten_api():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL in request body'}), 400

    original_url = data['url']
    db = SessionLocal()
    existing = db.query(URL).filter_by(original_url=original_url).first()

    if existing:
        short_code = existing.short_code
    else:
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        new_url = URL(original_url=original_url, short_code=short_code)
        db.add(new_url)
        db.commit()

    db.close()

    return jsonify({
        'original_url': original_url,
        'short_url': request.host_url + short_code
    }), 201


# Admin view of all shortened URLs
@app.route('/admin')
def view_all():
    db = SessionLocal()
    all_urls = db.query(URL).all()
    db.close()
    return render_template('admin.html', urls=all_urls)


# Redirection logic
@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    db = SessionLocal()
    url_entry = db.query(URL).filter_by(short_code=short_code).first()

    if url_entry:
        original_url = url_entry.original_url  # ✅ Store before closing session
        url_entry.click_count += 1
        db.commit()
        db.close()
        return redirect(original_url)  # ✅ Safe after session closed
    else:
        db.close()
        return jsonify({'error': 'URL not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
