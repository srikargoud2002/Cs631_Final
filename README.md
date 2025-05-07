# 🛒 E-Commerce Platform (MySQL + Streamlit)

A sample e-commerce platform with MySQL backend, Streamlit frontend, and Faker-generated user data.

---


### 1. Clone the Repository
```bash
git clone https://github.com/ srikargoud2002/Cs631_Final
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
Create a file named `.env` in the root directory and add the following:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=srikar_final
```

### 5. Set Up the Database Tables
```bash
python initial_table.py
```

### 6. Insert Sample Product Data
```bash
python sample_data.py
```

### 7. Generate Fake Customer and Transaction Data
```bash
python generate_fake_data.py
```

### 8. Run the Streamlit App
```bash
streamlit run app.py
```

---

## 📁 Project Structure
```
.
├── app.py
├── initial_table.py
├── generate_fake_data.py
├── sample_data.py
├── requirements.txt
├── .env
└── README.md
```

---

## ✅ Features

- Customer registration and login
- Credit card and shipping address management
- Product browsing with laptop/printer/computer details
- Shopping basket and checkout
- Transaction processing with totals
- Sales analytics via Streamlit

---

## 🛠 Requirements

- Python 3.8+
- MySQL Server
- Streamlit
