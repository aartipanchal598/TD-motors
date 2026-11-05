import os
import csv
import io
from datetime import datetime, timedelta
from uuid import uuid4
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, abort, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key-before-deploying")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "tdmotors.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["PREFERRED_URL_SCHEME"] = "https"

if os.environ.get("FLASK_ENV") == "production" and app.config["SECRET_KEY"] == "dev-only-change-this-secret-key-before-deploying":
    raise RuntimeError("Set a strong SECRET_KEY environment variable before production deployment.")

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to continue."
limiter = Limiter(get_remote_address, app=app, default_limits=["300 per day", "60 per hour"], storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"))

# HTTPS enforcement is enabled only in production, so local development remains easy.
if os.environ.get("FLASK_ENV") == "production":
    Talisman(app, force_https=True, content_security_policy={
        "default-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com", "data:"],
        "img-src": ["'self'", "data:", "https://images.unsplash.com", "https://*. Unsplash.com".replace(" ", "")],
        "script-src": ["'self'", "'unsafe-inline'"],
        "connect-src": ["'self'"]
    }, strict_transport_security=True, session_cookie_secure=True, content_security_policy_nonce_in=["script-src"])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    active = db.Column(db.Boolean, nullable=False, default=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    fuel = db.Column(db.String(30), default="Petrol")
    transmission = db.Column(db.String(30), default="Automatic")
    category = db.Column(db.String(40), default="SUV")
    image_url = db.Column(db.String(500), default="")
    description = db.Column(db.Text, default="")
    mileage = db.Column(db.String(40), default="")
    engine = db.Column(db.String(100), default="")
    seats = db.Column(db.Integer, nullable=True)
    features = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    topic = db.Column(db.String(60), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="New", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(1200), nullable=False)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class CustomerVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    video_path = db.Column(db.String(500), nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class RewardAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    referred_by = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class RewardTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(240), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class IncomeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(240), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    reference = db.Column(db.String(100), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@app.context_processor
def inject_template_globals():
    return {"now_year": datetime.utcnow().year}

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store" if request.path.startswith("/admin") else "public, max-age=0")
    return response

def normalize_phone(value):
    value = "".join(ch for ch in (value or "") if ch.isdigit() or ch == "+")
    if value.startswith("+"):
        return value
    if len(value) == 10:
        return "+91" + value
    if len(value) == 12 and value.startswith("91"):
        return "+" + value
    return value

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Sign in")

class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField("Mobile number", validators=[DataRequired(), Length(min=10, max=16)])
    referral_code = StringField("Referral code (optional)", validators=[Optional(), Length(max=20)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=10, max=128)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")

class InquiryForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    phone = StringField("Phone number", validators=[DataRequired(), Length(min=7, max=30)])
    topic = SelectField("I am interested in", choices=[("Car purchase", "Car purchase"), ("Finance", "Finance"), ("Insurance", "Insurance"), ("Detailing", "Car detailing"), ("Workshop", "Workshop / service"), ("Other", "Other")], validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField("Send enquiry")

class ReviewForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    rating = SelectField("Rating", choices=[("5", "★★★★★ — Excellent"), ("4", "★★★★ — Very good"), ("3", "★★★ — Good"), ("2", "★★ — Fair"), ("1", "★ — Poor")], validators=[DataRequired()])
    message = TextAreaField("Your experience", validators=[DataRequired(), Length(min=5, max=1200)])
    submit = SubmitField("Submit review")

class CarForm(FlaskForm):
    make = StringField("Brand", validators=[DataRequired(), Length(max=80)])
    model = StringField("Model", validators=[DataRequired(), Length(max=100)])
    year = StringField("Year", validators=[DataRequired(), Length(min=4, max=4)])
    price = DecimalField("Price (INR)", validators=[DataRequired(), NumberRange(min=0)])
    fuel = StringField("Fuel", validators=[DataRequired(), Length(max=30)])
    transmission = StringField("Transmission", validators=[DataRequired(), Length(max=30)])
    category = StringField("Body type", validators=[DataRequired(), Length(max=40)])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=500)])
    mileage = StringField("Mileage", validators=[Optional(), Length(max=40)])
    engine = StringField("Engine", validators=[Optional(), Length(max=100)])
    seats = StringField("Seating capacity", validators=[Optional(), Length(max=2)])
    features = TextAreaField("Key features (comma separated)", validators=[Optional(), Length(max=1000)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=3000)])
    status = SelectField("Status", choices=[("Available", "Available"), ("Reserved", "Reserved"), ("Sold", "Sold")])
    submit = SubmitField("Save car")

class IncomeForm(FlaskForm):
    category = SelectField("Income category", choices=[("Car sale", "Car sale"), ("Detailing", "Detailing"), ("Workshop", "Workshop"), ("Finance", "Finance"), ("Insurance", "Insurance"), ("Other", "Other")], validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired(), Length(max=240)])
    amount = DecimalField("Amount (INR)", validators=[DataRequired(), NumberRange(min=0.01)])
    entry_date = StringField("Date (YYYY-MM-DD)", validators=[DataRequired(), Length(min=10, max=10)])
    reference = StringField("Reference / invoice no.", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Save income")

@app.cli.command("init-db")
def init_db():
    """Create tables."""
    db.create_all()
    print("Database tables created.")

@app.cli.command("create-admin")
def create_admin():
    """Create an administrator interactively; never use a hard-coded admin password."""
    import getpass
    db.create_all()
    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()
    password = getpass.getpass("Strong admin password (12+ characters recommended): ")
    if len(password) < 10:
        print("Password must be at least 10 characters.")
        return
    if User.query.filter_by(email=email).first():
        print("An account with that email already exists.")
        return
    user = User(name=name, email=email, role="admin")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print("Admin account created.")

@app.route("/")
def home():
    cars = Car.query.filter_by(status="Available").order_by(Car.created_at.desc()).limit(6).all()
    reviews = Review.query.filter_by(approved=True).order_by(Review.created_at.desc()).limit(3).all()
    videos = CustomerVideo.query.filter_by(approved=True).order_by(CustomerVideo.created_at.desc()).limit(6).all()
    return render_template("index.html", cars=cars, reviews=reviews, videos=videos)

@app.route("/showroom")
def showroom():
    query = Car.query.filter_by(status="Available")
    brand = request.args.get("brand", "").strip()
    fuel = request.args.get("fuel", "").strip()
    transmission = request.args.get("transmission", "").strip()
    max_price = request.args.get("max_price", "").strip()
    if brand:
        query = query.filter(Car.make.ilike(f"%{brand}%"))
    if fuel:
        query = query.filter_by(fuel=fuel)
    if transmission:
        query = query.filter_by(transmission=transmission)
    min_price = request.args.get("min_price", "").strip()
    body = request.args.get("body", "").strip()
    model = request.args.get("model", "").strip()
    sort = request.args.get("sort", "price_asc")
    if model: query = query.filter(Car.model.ilike(f"%{model}%"))
    if body: query = query.filter_by(category=body)
    for raw, op in ((min_price, "min"), (max_price, "max")):
        if raw:
            try:
                query = query.filter(Car.price >= float(raw) if op == "min" else Car.price <= float(raw))
            except ValueError:
                flash("Please enter a valid price range.", "error")
    if sort == "price_desc": query = query.order_by(Car.price.desc())
    elif sort == "newest": query = query.order_by(Car.year.desc(), Car.created_at.desc())
    else: query = query.order_by(Car.price.asc())
    cars = query.all()
    brands = [x[0] for x in db.session.query(Car.make).filter_by(status="Available").distinct().order_by(Car.make).all()]
    bodies = [x[0] for x in db.session.query(Car.category).filter_by(status="Available").distinct().order_by(Car.category).all()]
    return render_template("showroom.html", cars=cars, brands=brands, bodies=bodies)

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact", methods=["GET", "POST"])
@limiter.limit("8 per minute", methods=["POST"])
def contact():
    form = InquiryForm()
    if form.validate_on_submit():
        item = Inquiry(name=form.name.data.strip(), email=form.email.data.lower().strip(), phone=form.phone.data.strip(), topic=form.topic.data, message=form.message.data.strip(), user_id=current_user.id if current_user.is_authenticated else None)
        db.session.add(item)
        db.session.commit()
        flash("Thank you! Your enquiry has been received. Our team will contact you soon.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)

@app.route("/review", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        item = Review(name=form.name.data.strip(), rating=int(form.rating.data), message=form.message.data.strip(), approved=False)
        db.session.add(item)
        db.session.commit()
        flash("Thank you for your feedback. It will appear after our team reviews it.", "success")
        return redirect(url_for("home") + "#reviews")
    return render_template("review.html", form=form)

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        else:
            phone = normalize_phone(form.phone.data)
            if User.query.filter_by(phone=phone).first():
                flash("This mobile number is already linked to an account.", "error")
                return render_template("auth.html", form=form, mode="register")
            user = User(name=form.name.data.strip(), email=email, phone=phone, role="customer")
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()
            code = "TD" + str(user.id).zfill(5)
            ref_code = form.referral_code.data.strip().upper()
            referrer = RewardAccount.query.filter_by(referral_code=ref_code).first() if ref_code else None
            db.session.add(RewardAccount(user_id=user.id, referral_code=code, referred_by=ref_code if referrer else None))
            if referrer:
                db.session.add(RewardTransaction(user_id=user.id, points=0, description="Joined using a referral code"))
            db.session.commit()
            login_user(user)
            flash("Your customer account has been created.", "success")
            return redirect(url_for("home"))
    return render_template("auth.html", form=form, mode="register")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip(), active=True).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=False, fresh=True)
            flash("Welcome back.", "success")
            return redirect(url_for("admin_dashboard" if user.role == "admin" else "account"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth.html", form=form, mode="login")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("home"))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        phone=normalize_phone(request.form.get("phone", ""))
        duplicate=User.query.filter(User.phone == phone, User.id != current_user.id).first()
        if len(phone) < 10 or len(phone) > 16 or duplicate:
            flash("Enter a valid mobile number that is not linked to another account.", "error")
        else:
            current_user.phone=phone; db.session.commit()
            flash("Your registered mobile number has been updated.", "success")
            return redirect(url_for("account"))
    inquiries = Inquiry.query.filter_by(user_id=current_user.id).order_by(Inquiry.created_at.desc()).all()
    return render_template("account.html", inquiries=inquiries)

@app.route("/admin")
@admin_required
def admin_dashboard():
    total_cars = Car.query.count()
    available_cars = Car.query.filter_by(status="Available").count()
    new_inquiries = Inquiry.query.filter_by(status="New").count()
    pending_reviews = Review.query.filter_by(approved=False).count()
    month = datetime.utcnow().strftime("%Y-%m")
    entries = IncomeEntry.query.filter(db.func.strftime("%Y-%m", IncomeEntry.entry_date) == month).all()
    monthly_income = sum(float(e.amount) for e in entries)
    recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(8).all()
    return render_template("admin.html", total_cars=total_cars, available_cars=available_cars, new_inquiries=new_inquiries, pending_reviews=pending_reviews, monthly_income=monthly_income, recent_inquiries=recent_inquiries)

@app.route("/admin/cars", methods=["GET", "POST"])
@admin_required
def admin_cars():
    form = CarForm()
    if form.validate_on_submit():
        try:
            year = int(form.year.data)
            if year < 1990 or year > datetime.utcnow().year + 1:
                raise ValueError()
            image_url = form.image_url.data.strip()
            uploaded = request.files.get("image_file")
            if uploaded and uploaded.filename:
                ext = uploaded.filename.rsplit(".", 1)[-1].lower() if "." in uploaded.filename else ""
                if ext not in ALLOWED_IMAGE_EXTENSIONS:
                    flash("Upload a JPG, PNG or WEBP car image.", "error")
                    return redirect(url_for("admin_cars"))
                filename = f"car_{uuid4().hex}.{ext}"
                uploaded.save(os.path.join(UPLOAD_DIR, filename))
                image_url = url_for("static", filename="uploads/" + filename)
            car = Car(make=form.make.data.strip(), model=form.model.data.strip(), year=year, price=form.price.data, fuel=form.fuel.data.strip(), transmission=form.transmission.data.strip(), category=form.category.data.strip(), image_url=image_url, description=form.description.data.strip(), mileage=form.mileage.data.strip(), engine=form.engine.data.strip(), seats=int(form.seats.data) if form.seats.data.strip().isdigit() else None, features=form.features.data.strip(), status=form.status.data)
            db.session.add(car)
            db.session.commit()
            flash("Car added to inventory.", "success")
            return redirect(url_for("admin_cars"))
        except ValueError:
            flash("Please enter a valid model year.", "error")
    cars = Car.query.order_by(Car.created_at.desc()).all()
    return render_template("admin_cars.html", form=form, cars=cars)

@app.route("/admin/cars/<int:car_id>/status", methods=["POST"])
@admin_required
def admin_car_status(car_id):
    car = db.get_or_404(Car, car_id)
    status = request.form.get("status")
    if status not in {"Available", "Reserved", "Sold"}:
        abort(400)
    car.status = status
    db.session.commit()
    flash("Car status updated.", "success")
    return redirect(url_for("admin_cars"))

@app.route("/admin/inquiries")
@admin_required
def admin_inquiries():
    status = request.args.get("status", "")
    query = Inquiry.query
    if status in {"New", "Contacted", "Closed"}:
        query = query.filter_by(status=status)
    inquiries = query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin_inquiries.html", inquiries=inquiries, selected_status=status)

@app.route("/admin/inquiries/<int:inquiry_id>/status", methods=["POST"])
@admin_required
def admin_inquiry_status(inquiry_id):
    inquiry = db.get_or_404(Inquiry, inquiry_id)
    status = request.form.get("status")
    if status not in {"New", "Contacted", "Closed"}:
        abort(400)
    inquiry.status = status
    db.session.commit()
    flash("Enquiry status updated.", "success")
    return redirect(url_for("admin_inquiries"))

@app.route("/admin/reviews")
@admin_required
def admin_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin_reviews.html", reviews=reviews)

@app.route("/admin/reviews/<int:review_id>/approve", methods=["POST"])
@admin_required
def approve_review(review_id):
    review = db.get_or_404(Review, review_id)
    review.approved = True
    db.session.commit()
    flash("Review approved and published.", "success")
    return redirect(url_for("admin_reviews"))

@app.route("/admin/income", methods=["GET", "POST"])
@admin_required
def admin_income():
    form = IncomeForm()
    if form.validate_on_submit():
        try:
            entry_date = datetime.strptime(form.entry_date.data, "%Y-%m-%d").date()
            entry = IncomeEntry(category=form.category.data, description=form.description.data.strip(), amount=form.amount.data, entry_date=entry_date, reference=form.reference.data.strip())
            db.session.add(entry)
            db.session.commit()
            flash("Income record saved.", "success")
            return redirect(url_for("admin_income"))
        except ValueError:
            flash("Date must use YYYY-MM-DD format.", "error")
    month = request.args.get("month", datetime.utcnow().strftime("%Y-%m"))
    entries = IncomeEntry.query.filter(db.func.strftime("%Y-%m", IncomeEntry.entry_date) == month).order_by(IncomeEntry.entry_date.desc()).all()
    total = sum(float(e.amount) for e in entries)
    return render_template("admin_income.html", form=form, entries=entries, total=total, month=month)

@app.route("/admin/export/<kind>.csv")
@admin_required
def export_csv(kind):
    output = io.StringIO()
    writer = csv.writer(output)
    if kind == "income":
        writer.writerow(["Date", "Category", "Description", "Amount INR", "Reference"])
        for e in IncomeEntry.query.order_by(IncomeEntry.entry_date.desc()).all():
            writer.writerow([e.entry_date.isoformat(), e.category, e.description, str(e.amount), e.reference])
        filename = "td-motors-income.csv"
    elif kind == "inquiries":
        writer.writerow(["ID", "Created at", "Name", "Email", "Phone", "Topic", "Message", "Status"])
        for e in Inquiry.query.order_by(Inquiry.created_at.desc()).all():
            writer.writerow([e.id, e.created_at.isoformat(), e.name, e.email, e.phone, e.topic, e.message, e.status])
        filename = "td-motors-inquiries.csv"
    else:
        abort(404)
    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/admin/videos", methods=["GET", "POST"])
@admin_required
def admin_videos():
    if request.method == "POST":
        title=request.form.get("title", "Customer story").strip()[:120]
        upload=request.files.get("video_file")
        if not upload or not upload.filename:
            flash("Choose a customer-approved video file.", "error")
        else:
            ext=upload.filename.rsplit(".",1)[-1].lower() if "." in upload.filename else ""
            if ext not in {"mp4", "webm", "mov"}:
                flash("Upload MP4, WEBM or MOV video only.", "error")
            else:
                filename=f"customer_{uuid4().hex}.{ext}"
                folder=os.path.join(BASE_DIR,"static","videos"); os.makedirs(folder,exist_ok=True)
                upload.save(os.path.join(folder,filename))
                db.session.add(CustomerVideo(title=title or "Customer story", video_path=url_for("static",filename="videos/"+filename)))
                db.session.commit(); flash("Customer video published on the homepage.","success")
        return redirect(url_for("admin_videos"))
    videos=CustomerVideo.query.order_by(CustomerVideo.created_at.desc()).all()
    return render_template("admin_videos.html", videos=videos)

@app.route("/admin/rewards", methods=["GET", "POST"])
@admin_required
def admin_rewards():
    if request.method == "POST":
        email=request.form.get("email", "").strip().lower(); points=request.form.get("points", "").strip(); note=request.form.get("description", "Eligible purchase/service reward").strip()
        user=User.query.filter_by(email=email, role="customer").first()
        try: value=int(points)
        except ValueError: value=0
        if not user or value < 1 or value > 100000:
            flash("Enter a valid customer email and points amount.", "error")
        else:
            wallet=RewardAccount.query.filter_by(user_id=user.id).first()
            if not wallet:
                wallet=RewardAccount(user_id=user.id, referral_code="TD"+str(user.id).zfill(5)); db.session.add(wallet)
            wallet.points += value
            db.session.add(RewardTransaction(user_id=user.id, points=value, description=note[:240])); db.session.commit()
            flash("Reward points credited successfully.", "success")
        return redirect(url_for("admin_rewards"))
    wallets=RewardAccount.query.order_by(RewardAccount.created_at.desc()).all()
    return render_template("admin_rewards.html", wallets=wallets)

@app.route("/compare")
def compare_cars():
    ids = [int(x) for x in request.args.getlist("car") if x.isdigit()][:3]
    selected = Car.query.filter(Car.id.in_(ids), Car.status == "Available").all() if ids else []
    cars = Car.query.filter_by(status="Available").order_by(Car.make, Car.model).all()
    return render_template("compare.html", cars=cars, selected=selected)

@app.route("/emi")
def emi_calculator():
    return render_template("emi.html")

@app.route("/loyalty", methods=["GET", "POST"])
@login_required
def loyalty():
    if current_user.role != "customer": abort(403)
    reward = RewardAccount.query.filter_by(user_id=current_user.id).first()
    if reward is None:
        reward = RewardAccount(user_id=current_user.id, referral_code="TD" + str(current_user.id).zfill(5))
        db.session.add(reward); db.session.commit()
    if request.method == "POST":
        try: points=int(request.form.get("points", "0"))
        except ValueError: points=0
        package=request.form.get("package", "Selected service package").strip()[:100]
        if points < 1 or points > reward.points:
            flash("Enter a valid number of points within your available balance.", "error")
        else:
            reward.points -= points
            db.session.add(RewardTransaction(user_id=current_user.id, points=-points, description="Redemption request: "+package))
            db.session.commit()
            flash("Your redemption request has been recorded. TD Motors will confirm package eligibility.", "success")
            return redirect(url_for("loyalty"))
    history = RewardTransaction.query.filter_by(user_id=current_user.id).order_by(RewardTransaction.created_at.desc()).all()
    return render_template("loyalty.html", reward=reward, history=history)

@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        phone = normalize_phone(request.form.get("phone", ""))
        user = User.query.filter_by(phone=phone, active=True).first()
        if not user:
            flash("No active account is linked to that mobile number.", "error")
        else:
            sid=os.environ.get("TWILIO_ACCOUNT_SID"); token=os.environ.get("TWILIO_AUTH_TOKEN"); service=os.environ.get("TWILIO_VERIFY_SERVICE_SID")
            if not all([sid, token, service]):
                flash("Mobile OTP is not configured yet. TD Motors must add its SMS provider credentials before password recovery can send an OTP.", "error")
            else:
                try:
                    import requests
                    r=requests.post(f"https://verify.twilio.com/v2/Services/{service}/Verifications", auth=(sid,token), data={"To": phone, "Channel":"sms"}, timeout=12)
                    if r.ok:
                        session["pw_reset_phone"] = phone
                        flash("Verification code sent to your registered mobile.", "success")
                        return redirect(url_for("reset_password"))
                    flash("Could not send OTP. Check the registered number and SMS provider configuration.", "error")
                except Exception:
                    flash("OTP service is temporarily unavailable. Please try again later.", "error")
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def reset_password():
    phone=session.get("pw_reset_phone")
    if not phone: return redirect(url_for("forgot_password"))
    if request.method == "POST":
        code=request.form.get("otp", "").strip(); password=request.form.get("password", ""); confirm=request.form.get("confirm", "")
        if len(password)<10 or password != confirm:
            flash("Use a matching password of at least 10 characters.", "error")
        else:
            sid=os.environ.get("TWILIO_ACCOUNT_SID"); token=os.environ.get("TWILIO_AUTH_TOKEN"); service=os.environ.get("TWILIO_VERIFY_SERVICE_SID")
            try:
                import requests
                r=requests.post(f"https://verify.twilio.com/v2/Services/{service}/VerificationCheck", auth=(sid,token), data={"To":phone,"Code":code}, timeout=12)
                if r.ok and r.json().get("status")=="approved":
                    user=User.query.filter_by(phone=phone).first(); user.set_password(password); db.session.commit(); session.pop("pw_reset_phone",None)
                    flash("Password reset successfully. Please sign in.", "success"); return redirect(url_for("login"))
                flash("The OTP is invalid or expired. Please try again.", "error")
            except Exception: flash("OTP verification is unavailable. Please try again.", "error")
    return render_template("reset_password.html", phone=phone)

@app.errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, message="You do not have permission to view this page."), 403

@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message="We could not find that page."), 404

with app.app_context():
    db.create_all()
    # Safe additive SQLite migrations: existing customer, car, and enquiry rows are retained.
    if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        migrations = {"user": {"phone": "VARCHAR(30)"}, "car": {"mileage": "VARCHAR(40) DEFAULT ''", "engine": "VARCHAR(100) DEFAULT ''", "seats": "INTEGER", "features": "TEXT DEFAULT ''"}}
        for table, columns in migrations.items():
            existing = {col["name"] for col in inspector.get_columns(table)}
            for column, definition in columns.items():
                if column not in existing:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
