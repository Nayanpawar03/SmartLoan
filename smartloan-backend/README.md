# SmartLoan Backend

A banking-style backend system that uses a **Fuzzy Inference System (FIS)** combined with a **trained Logistic Regression model** to evaluate credit scores, predict default probability, and generate AI-powered explanations for loan decisions.

---

## Tech Stack

- **Node.js + Express.js** — REST API server
- **MySQL** — relational database
- **JWT + Passport.js** — authentication (email/password + Google OAuth)
- **Python FastAPI** — ML microservice (FIS + default prediction + explainability)
- **scikit-fuzzy** — fuzzy logic engine
- **scikit-learn** — logistic regression model trained on real Kaggle data

---

## Project Structure

```
smartloan-backend/
├── src/
│   ├── config/
│   │   ├── db.js              # MySQL connection pool
│   │   └── passport.js        # Google OAuth strategy
│   ├── controllers/
│   │   ├── authController.js
│   │   ├── profileController.js
│   │   ├── assessmentController.js
│   │   ├── loanController.js
│   │   └── managerController.js
│   ├── routes/
│   │   ├── authRoutes.js
│   │   ├── profileRoutes.js
│   │   ├── assessmentRoutes.js
│   │   ├── loanRoutes.js
│   │   └── managerRoutes.js
│   ├── middleware/
│   │   └── authMiddleware.js  # JWT verify + role check
│   ├── utils/
│   │   └── loanEligibility.js # DTI + eligibility logic
│   └── server.js
├── .env
└── package.json

smartloan-fis/
├── fis_engine.py      # Fuzzy Inference System (2-stage)
├── nn_model.py        # Default probability prediction
├── explainer.py       # AI explanation generator
├── train_model.py     # Model training script
├── main.py            # FastAPI entry point
├── model.pkl          # Trained logistic regression
├── scaler.pkl         # Fitted StandardScaler
├── features.pkl       # Feature list
└── venv/
```

---

## Prerequisites

- Node.js v18+
- Python 3.11
- MySQL 8.0

---

## Setup

### 1. Clone the repo and install Node dependencies

```bash
cd smartloan-backend
npm install
```

### 2. Configure environment variables

Create a `.env` file in `smartloan-backend/`:

```env
PORT=3000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smartloan_db
JWT_SECRET=your_jwt_secret
FIS_API_URL=http://localhost:8000/predict-credit-score
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_CALLBACK_URL=http://localhost:3000/api/auth/google/callback
SESSION_SECRET=your_session_secret
```

### 3. Set up the database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE smartloan_db;
USE smartloan_db;
```

Run all `CREATE TABLE` statements for:
- `users`
- `user_financial_profiles`
- `credit_assessments`
- `loan_products`
- `loan_applications`

Add explanation column:
```sql
ALTER TABLE credit_assessments ADD COLUMN explanation TEXT;
```

Seed loan products:
```sql
INSERT INTO loan_products (name, min_credit_score, max_dti, min_income, max_loan_amount, interest_rate, tenure_months) VALUES
('Basic Personal Loan', 40, 50.00, 20000, 200000, 14.5, 36),
('Standard Personal Loan', 55, 45.00, 35000, 500000, 12.0, 48),
('Premium Personal Loan', 70, 40.00, 50000, 1000000, 10.5, 60),
('Home Loan', 75, 35.00, 60000, 5000000, 8.5, 240),
('Business Loan', 65, 40.00, 75000, 2000000, 13.0, 84);
```

### 4. Set up the Python FIS + ML service

```bash
cd smartloan-fis
venv\Scripts\activate
pip install fastapi uvicorn scikit-fuzzy scikit-learn scipy numpy pandas joblib packaging networkx
```

Train the model (requires `cs-training.csv` from Kaggle "Give Me Some Credit"):
```bash
python train_model.py
```

Start the service:
```bash
uvicorn main:app --reload --port 8000
```

### 5. Start the Node.js server

```bash
cd smartloan-backend
npm run dev
```

---

## API Reference

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register with email/password |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/google` | Google OAuth login |

### Financial Profile (requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profile` | Submit financial profile |
| PUT | `/api/profile` | Update financial profile |
| GET | `/api/profile` | Get own profile |

### Credit Assessment (requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/assessment/run` | Run FIS + ML assessment |
| GET | `/api/assessment/latest` | Get latest assessment result |

### Loans (requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/loans/recommendations` | Get eligible loan products |
| POST | `/api/loans/apply` | Apply for a loan |
| GET | `/api/loans/my-applications` | View own applications |

### Manager Dashboard (requires JWT + manager role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/manager/users` | All users with credit scores |
| GET | `/api/manager/applications` | All applications with AI explanation |
| PATCH | `/api/manager/applications/:id/status` | Approve or reject application |
| GET | `/api/manager/analytics` | Risk stats and score distribution |

---

## How the AI Pipeline Works

```
User submits financial profile
        ↓
Stage 1 FIS → behaviour_score + financial_score + experience_score
        ↓
Stage 2 FIS → fuzzy_credit_score (300–850)
        ↓
Logistic Regression → default_probability (0–1)
        ↓
Explainer → human-readable explanation
        ↓
Stored in DB + returned to client
```

### FIS Scoring

**Stage 1** computes 3 intermediate scores:
- `behaviour_score` — payment history + credit utilization
- `financial_score` — DTI + income + EMI
- `experience_score` — credit history length + inquiries

**Stage 2** combines them into a final `credit_score` (300–850)

| Score Range | Band | Risk Level |
|-------------|------|------------|
| 800 – 850 | Excellent | Very Low |
| 700 – 799 | Good | Low |
| 600 – 699 | Fair | Medium |
| 500 – 599 | Poor | High |
| 300 – 499 | Very Poor | Very High |

### Default Prediction

Logistic Regression trained on 150,000 records from the Kaggle "Give Me Some Credit" dataset. Key learned feature weights:

| Feature | Influence |
|---------|-----------|
| fuzzy_credit_score | ↓ risk |
| credit_utilization | ↑ risk (strongest) |
| monthly_income | ↓ risk |
| debt_to_income_ratio | ↑ risk |
| num_inquiries | ↑ risk |

### AI Explanation Example

> "This applicant presents moderate default risk supported by low credit utilization, a healthy debt-to-income ratio, a moderate income level, few recent credit inquiries, and a good credit score (696). (Default probability: 43%)"

---

## Authentication

All protected routes require:
```
Authorization: Bearer <jwt_token>
```

Manager routes additionally require the user's `role` to be `manager`.
