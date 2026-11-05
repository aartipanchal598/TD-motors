# TD Motors — Premium Website

Flask website for TD Motors, Kharadi, Pune. This updated build keeps the existing SQLite database and adds new features through safe, additive startup migrations. Existing users, enquiries, cars, reviews and income rows are not intentionally deleted or reset.

## Included in this update
- Premium responsive automotive UI with motion/reveal effects and improved mobile navigation.
- Customer and administrator sign-in through the same login screen; role-based redirects and protected admin routes.
- Customer registration with mobile number, customer account page and registered-phone update.
- Forgot-password OTP flow using Twilio Verify SMS (requires credentials; see below).
- Showroom filters for brand, model, fuel, transmission, body type, minimum/maximum price and sorting.
- Car photo upload from the admin inventory page (JPG, PNG, WEBP) plus image URL support and a visual fallback.
- Car comparison for up to three vehicles using stored vehicle specifications.
- EMI calculator.
- Customer rewards wallet, referral codes, points history, redemption requests and admin point-crediting page.
- Customer experience/video showcase placeholder ready for customer-approved video files and Instagram links.
- Existing enquiry, review moderation, income tracking and CSV export functions retained.

## Important database note
Keep your current `tdmotors.db` file. Do not run a database reset or delete it. On first startup this build checks for the newly required columns and adds only missing columns to the existing `user` and `car` tables. New reward tables are created if absent. Back up `tdmotors.db` before upgrading, as you should before any software update.

## Run locally on Windows
1. Extract the project and open the inner `TD_Motors_Premium_Website` folder in VS Code.
2. Keep your existing `.env` file and `tdmotors.db` backup safe. If `.env` is not present, copy `.env.example` to `.env`.
3. Activate your existing virtual environment (if already active, skip this):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
4. Install/update dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Ensure `.env` contains a strong `SECRET_KEY`. Do not share this file publicly.
6. Run:
   ```powershell
   flask --app app run
   ```
7. Open `http://127.0.0.1:5000`.

## Admin and customer GUI
- Both admins and customers use `/login`.
- New customers register at `/register`.
- Existing admin accounts remain admin accounts and are redirected to `/admin` after login.
- Customers are redirected to `/account` and can access `/loyalty`.
- Admin manages cars at `/admin/cars`, inquiries at `/admin/inquiries`, reviews at `/admin/reviews`, income at `/admin/income`, and rewards at `/admin/rewards`.

## SMS OTP setup (required for live password recovery)
The forgot-password screen uses Twilio Verify SMS. Create/configure a Verify service with Twilio, then add these values to your private `.env` file:

```ini
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
```

Restart Flask after changing `.env`. Registered mobile numbers are normalized to E.164 for Indian numbers (10-digit numbers receive the +91 prefix). Twilio account/service charges, destination permissions and SMS delivery conditions apply. Until configured, the website clearly reports that SMS OTP is not enabled; it does not pretend to send a code.

## Car images and stock
The supplied database currently contains **zero car inventory records**, so the showroom cannot show actual TD Motors vehicles until the admin adds them. Add each real car from Admin → Car inventory, enter its price/specifications, and upload a client-approved JPG/PNG/WEBP photo or provide an image URL. Do not treat sample stock photos as actual available inventory. A generic automotive fallback appears if a listing's image URL fails.

## Customer videos / Instagram
The homepage now includes a customer experience/video showcase area. Add customer-approved original videos under `static/videos/` and replace the placeholder cards with the relevant video paths. Public Instagram Reels can be linked/embedded where Instagram permits; private, deleted or embed-disabled posts may not display. Obtain customer consent and media usage rights before publishing handover videos.

## Reward programme operation
Customers receive a referral code at registration. Admin should credit points only after verifying an eligible sale, service or referral in Admin → Customer rewards. Customers can request redemption from their rewards wallet; TD Motors must confirm package eligibility and fulfil the request. The software does not automatically verify payments or service completion.

## Deployment checklist
- Use HTTPS, a strong secret key and secure environment variables.
- Use managed PostgreSQL and Redis for a public multi-worker deployment; back up and migrate the database deliberately.
- Configure and test Twilio Verify, email delivery, monitoring and backups.
- Replace/augment stock imagery with client-owned media, test every form and mobile layout, and perform a security review before launch.
- CSV exports remain available for Excel; use Print → Save as PDF for a quick PDF copy.

## TD Motors contact details
Phone: +91 95772 30707  
Email: info.technodriven@gmail.com  
Website: https://technodriven.in  
Instagram: https://www.instagram.com/td_motors_multibrand/
