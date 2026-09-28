# TD Motors Premium Website

A premium multi-brand automotive website starter for TD Motors, Kharadi, Pune.

## Stack
- HTML5
- CSS3
- Vanilla JavaScript
- Node.js + Express
- Nodemailer for server-side email
- JSON file storage for the optional inquiry-data bonus

## Run locally

1. Install Node.js (LTS) from https://nodejs.org/
2. Open this folder in VS Code.
3. Open VS Code Terminal.
4. Run:
   npm install
5. Copy `.env.example` to `.env`.
6. Put the verified TD Motors business email and Gmail/App Password values in `.env`.
7. Run:
   npm start
8. Open:
   http://localhost:3000

## WhatsApp
Open `public/app.js` and replace:
`const DEMO_WHATSAPP = "91XXXXXXXXXX";`
with the verified TD Motors WhatsApp number, including country code and no `+`, spaces or dashes.

## Before client delivery
Replace all demo/placeholder:
- phone number
- WhatsApp number
- business email
- exact address
- business hours
- customer reviews
- car inventory
- real prices
- real vehicle photos
- real showroom/detailing/workshop photos
- verified social links

Do not put Gmail passwords, API keys or other secrets inside `public/`.

## Email integration
The backend uses Nodemailer and reads credentials from `.env`. Never commit `.env` to GitHub.

For Gmail, use a Google App Password rather than your normal Gmail password. Your Google account should have 2-Step Verification enabled.

## GitHub
Create a repository, then:
git init
git add .
git commit -m "Initial TD Motors premium website"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main

## Important deployment note
For a production deployment, use a real database instead of the demo JSON file and use a transactional email provider or a properly configured business mailbox.