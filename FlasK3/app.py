from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from datetime import datetime
from forms import RegistrationForm, LoginForm
from utils import load_json, save_json
import os
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(256)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, username, password, last_login, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.last_login = last_login
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    users_dct = load_json("data", "user.json")
    user_dct = users_dct.get(str(user_id))
    if not user_dct:
        return None
    user_obj = User(str(user_id), user_dct['username'], user_dct['password'], user_dct.get('last_login'), user_dct.get('is_admin', False))
    return user_obj

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    users_dct = load_json("data", "user.json")
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        for key, user in users_dct.items():
            if user['username'] == username and check_password_hash(user['password'], password):
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                users_dct[key]["last_login"] = login_time
                save_json("data", "user.json", users_dct)

                user_obj = User(key, username, password, login_time, user.get('is_admin', False))

                #users_dct[key]['last_login'] =
                login_user(user_obj)
                return redirect(url_for("index"))
        print(form.errors)
    else:
        print(form.errors)
    return render_template("login.html", form=form)


@app.route("/hidden")
@login_required
def hidden():
    return f"Если вы можете прочитать эту надпись, значит вы авторизованный пользователь. Привет, {current_user.username}!"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Успешый выход из профиля!", "success")
    return redirect(url_for("index"))


@app.route("/edit/", methods=["GET", "POST"])
@login_required
def edit():
    if not current_user.is_admin:
        flash("Только администратор может создавать новых пользователей!", "warning")
        return redirect(url_for("index"))

    form = RegistrationForm()
    user_dct = load_json("data", "user.json")

    if request.method == "POST" and form.validate_on_submit():
        # Проверка на дубликат имени
        if any(u['username'] == form.username.data for u in user_dct.values()):
            flash("Пользователь с таким именем уже существует!", "danger")
            return render_template("register.html", form=form)

        hashed_password = generate_password_hash(form.password.data)

        new_user = {
            "username": form.username.data,
            "password": hashed_password,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "last_login": None,
            "is_admin": False
        }
        user_dct[form.username.data] = new_user
        save_json("data", "user.json", user_dct)
        flash("Пользователь успешно зарегистрирован!", "success")
        return redirect(url_for("index"))

    return render_template("register.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Гарантируем, что user_dct всегда dict, даже если файл пуст/отсутствует
    user_dct = load_json("data", "user.json") or {}
    form = RegistrationForm()

    if request.method == "POST" and form.validate_on_submit():
        # Проверка на дубликат имени
        if any(u['username'] == form.username.data for u in user_dct.values()):
            flash("Пользователь с таким именем уже существует!", "warning")
            return render_template("register.html", form=form)

        # Логика доступа
        is_first_user = len(user_dct) == 0

        is_admin_allowed = current_user.is_authenticated and getattr(current_user, 'is_admin', False)

        if not (is_first_user or is_admin_allowed):
            flash("Регистрация закрыта. Только администратор может создавать пользователей.", "warning")
            return redirect(url_for("index"))

        # Создание нового пользователя
        hashed_password = generate_password_hash(form.password.data)
        new_user = {
            "username": form.username.data,
            "password": hashed_password,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "last_login": None,
            "is_admin": is_first_user
        }

        user_dct[form.username.data] = new_user
        save_json("data", "user.json", user_dct)

        # Уведомление и редирект
        msg = "Пользователь зарегистрирован!"
        if is_first_user:
            msg += " Вы стали администратором."
        flash(msg, "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
