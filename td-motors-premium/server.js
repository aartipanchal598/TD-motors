const express = require("express");
const cors = require("cors");
const path = require("path");
const fs = require("fs");
const nodemailer = require("nodemailer");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 3000;
const dataDir = path.join(__dirname, "data");
const dataFile = path.join(dataDir, "inquiries.json");

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "public")));

if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir);
if (!fs.existsSync(dataFile)) fs.writeFileSync(dataFile, "[]");

function saveInquiry(inquiry) {
  const existing = JSON.parse(fs.readFileSync(dataFile, "utf8"));
  existing.push(inquiry);
  fs.writeFileSync(dataFile, JSON.stringify(existing, null, 2));
}

function createTransporter() {
  if (!process.env.GMAIL_USER || !process.env.GMAIL_APP_PASSWORD) return null;
  return nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.GMAIL_USER,
      pass: process.env.GMAIL_APP_PASSWORD
    }
  });
}

app.post("/api/inquiries", async (req, res) => {
  const {
    fullName, mobile, email, brand, carModel,
    serviceRequired, preferredDateTime, message
  } = req.body;

  if (!fullName || !mobile || !email || !serviceRequired) {
    return res.status(400).json({
      success: false,
      message: "Please complete all required fields."
    });
  }

  const inquiry = {
    id: Date.now().toString(),
    fullName,
    mobile,
    email,
    brand: brand || "",
    carModel: carModel || "",
    serviceRequired,
    preferredDateTime: preferredDateTime || "",
    message: message || "",
    inquiryDate: new Date().toISOString(),
    status: "New"
  };

  try {
    saveInquiry(inquiry);

    const transporter = createTransporter();
    if (transporter && process.env.BUSINESS_EMAIL) {
      await transporter.sendMail({
        from: `"TD Motors Website" <${process.env.GMAIL_USER}>`,
        to: process.env.BUSINESS_EMAIL,
        replyTo: email,
        subject: `New Customer Inquiry — ${serviceRequired}`,
        text:
`New Customer Inquiry

Name: ${fullName}
Mobile: ${mobile}
Email: ${email}
Interested Brand: ${brand || "Not specified"}
Car Model: ${carModel || "Not specified"}
Requirement: ${serviceRequired}
Preferred Date/Time: ${preferredDateTime || "Not specified"}
Message: ${message || "No additional message"}

Inquiry ID: ${inquiry.id}`
      });
    }

    res.json({
      success: true,
      message: "Your inquiry has been received."
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({
      success: false,
      message: "We could not submit your inquiry right now. Please try WhatsApp instead."
    });
  }
});

app.get("*splat", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`TD Motors website running at http://localhost:${PORT}`);
});