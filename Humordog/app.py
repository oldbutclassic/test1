from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Post, Category
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 실제 운영 시 안전한 키로 변경하세요.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///humordog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    main_post = Post.query.order_by(Post.created_at.desc()).first()
    posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    categories = Category.query.all()
    return render_template('index.html', main_post=main_post, posts=posts, categories=categories)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/category/<int:category_id>')
def category_page(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    return render_template('category.html', category=category, posts=posts, categories=categories)

@app.route('/admin/new_post', methods=['GET', 'POST'])
def new_post():
    # 간단한 인증 구현 (추후 개선 필요)
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form['category']
        file = request.files['thumbnail']

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            thumbnail_path = f'uploads/{filename}'
        else:
            thumbnail_path = None

        new_post = Post(title=title, content=content, category_id=category_id, thumbnail=thumbnail_path)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('new_post.html', categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 매우 기본적인 로그인 기능 (아이디: admin, 비밀번호: password)
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('new_post'))
        else:
            return "로그인 실패"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
