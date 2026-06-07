from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db, login_manager
from datetime import datetime
from models import News, User, Category, Tag
import os
from forms import NewsForm, CategoryForm, TagForm
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db, login_manager
from datetime import datetime
from models import News, User, Category, Tag
import os
from forms import NewsForm, CategoryForm, TagForm, RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_access = datetime.utcnow()
            db.session.commit()
            flash('Вы вошли в систему', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html', form=form)  # ← показываем форму при GET

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    print(64)
    form = RegistrationForm()
    if form.validate_on_submit():
        print(67)
        if User.query.filter_by(email=form.email.data).first():
            flash('Этот email уже зарегистрирован', 'danger')
            return redirect(url_for('register'))
        print(71)
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,  # ← ОБЯЗАТЕЛЬНО!
                first_name=form.first_name.data or None,
                last_name=form.last_name.data or None,
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {e}', 'danger')
            return redirect(url_for('register'))
    print(form.errors)

    print(90)
    return render_template('register.html', form=form)


@app.route("/")
@app.route("/category/<int:category_id>")
def index(category_id=None):
    tag_name = request.args.get("tag")
    query = News.query


    if not current_user.is_authenticated:
        query = query.filter_by(is_private=False)
    # Фильтр по категории, если задана
    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    # Фильтр по тегу, если задан
    if tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            query = query.filter(News.tags.contains(tag))
        else:
            query = query.filter(False)

    news_list = query.order_by(News.created.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template(
        "index.html",
        news_list=news_list,
        categories=Category.query.all(),
        tags=Tag.query.all(),
        selected_category=category_id,
        selected_tag=tag_name,
    )

@app.route("/news/add", methods=["GET", "POST"])
@login_required
def add_news():
    form = NewsForm()
    categories = Category.query.all()
    form.category.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            content=form.content.data,
            user_id=1 if current_user.is_anonymous else current_user.id,
            category_id=form.category.data,
            is_private=form.is_private.data,
            created=datetime.utcnow(),
        )
        tag_names = [t.strip() for t in form.tags.data.split(",") if t.strip()]
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        news.tags = tags
        db.session.add(news)
        db.session.commit()
        flash("Новость успешно добавлена", "success")
        return redirect(url_for("index"))
    return render_template("news_form.html", form=form, title="Добавить новость")


@app.route("/news/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_news(id):
    news = News.query.get_or_404(id)
    form = NewsForm(obj=news)
    categories = Category.query.all()
    form.category.choices = [(category.id, category.name) for category in categories]

    if request.method == "GET":
        form.tags.data = ", ".join([tag.name for tag in news.tags])

    if request.method == "POST" and form.validate_on_submit():
        # import pdb; pdb.set_trace()
        # form.populate_obj(news)
        news.title = form.title.data
        news.content = form.content.data
        news.category_id = form.category.data
        news,is_private = form.is_private.data
        tag_names = [t.strip() for t in form.tags.data.split(",") if t.strip()]
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        news.tags = tags
        db.session.commit()
        flash("Новость успешно обновлена", "success")
        return redirect(url_for("index"))
    return render_template("news_form.html", form=form, title="Редактировать новость")
@app.route("/news/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_news(id):
    news = News.query.get_or_404(id)
    news.is_deleted = True
    db.session.commit()

    flash("Новость успешно удалена", "success")
    return redirect(url_for("index"))

@app.route("/news/<int:id>")
def view_news(id):
    news = News.query.get_or_404(id)
    categories = Category.query.all()
    return render_template("news_detail.html", news=news, categories=categories)


@app.route("/categories")
def categories():
    categories = Category.query.all()
    return render_template("categories.html", categories=categories)


@app.route("/category/add", methods=["GET", "POST"])
@login_required
def add_category():
    form = CategoryForm()
    if request.method == "POST" and form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash("Категория успешно добавлена", "success")
        return redirect(url_for("categories"))
    return render_template("category_form.html", form=form, title="Добавить категорию")


@app.route("/category/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()
        flash("Категория успешно обновлена", "success")
        return redirect(url_for("categories"))
    return render_template("category_form.html", form=form, title="Редактировать категорию")


@app.route("/tags")
def tags():
    tags = Tag.query.all()
    return render_template("tags.html", tags=tags)


@app.route("/tag/add", methods=["GET", "POST"])
@login_required
def add_tag():
    form = TagForm()
    if request.method == "POST" and form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash("Тег успешно добавлен", "success")
        return redirect(url_for("tags"))
    return render_template("tag_form.html", form=form, title="Добавить тег")


@app.route("/tag/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(tag)
        db.session.commit()
        flash("Тег успешно обновлен", "success")
        return redirect(url_for("tags"))
    return render_template("tag_form.html", form=form, title="Редактировать тег")


if __name__ == "__main__":
    app.run(debug=True)



