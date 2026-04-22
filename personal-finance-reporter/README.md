# 📊 Personal Finance Reporter

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2ECC71?style=flat)
![Tests](https://img.shields.io/badge/Tests-pytest-E74C3C?style=flat&logo=pytest&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

A command-line tool that reads personal finance data from a CSV file and generates a **professional multi-page PDF report** with charts, tables and key statistics — in seconds.

---

## ✨ Features

- **Automatic PDF generation** — cover page, stat cards, charts and tables
- **3 embedded charts** — income vs expenses bar chart, category pie chart, monthly balance
- **Monthly breakdown table** with savings rate per month
- **Category ranking** to identify your biggest spending areas
- **Clean CLI** — works with any CSV following the required format
- **Robust validation** — helpful error messages for malformed input
- **Full test suite** with pytest

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/personal-finance-reporter.git
cd personal-finance-reporter

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run with the sample data
python main.py
```

The report will be saved to `reports/finance_report.pdf`. Open it and see your finances summarised.

---

## 📂 Project Structure

```
personal-finance-reporter/
├── main.py                  # CLI entry point
├── src/
│   ├── parser.py            # CSV loading and validation
│   ├── analytics.py         # Financial computations
│   ├── charts.py            # Matplotlib chart generation
│   └── report.py            # ReportLab PDF assembly
├── tests/
│   └── test_finance.py      # pytest test suite
├── data/
│   └── expenses_sample.csv  # Sample dataset
├── reports/                 # Generated PDFs (git-ignored)
├── requirements.txt
├── .gitignore
├── LICENSE
└── CHANGELOG.md
```

---

## 📋 CSV Format

Your input file must contain the following columns:

| Column        | Type    | Example          | Notes                          |
|---------------|---------|------------------|--------------------------------|
| `date`        | date    | `2024-01-15`     | ISO 8601 format (YYYY-MM-DD)   |
| `category`    | string  | `Food`           | Any label you choose           |
| `description` | string  | `Supermarket`    | Free text                      |
| `amount`      | float   | `45.30`          | Positive number                |
| `type`        | string  | `expense`        | Must be `income` or `expense`  |

**Example:**
```csv
date,category,description,amount,type
2024-01-15,Income,Salary,1800.00,income
2024-01-18,Food,Supermarket REWE,45.30,expense
2024-01-20,Transport,Monthly U-Bahn ticket,86.00,expense
```

---

## 🖥️ CLI Usage

```bash
# Use default sample data
python main.py

# Specify a custom input file
python main.py --input path/to/my_expenses.csv

# Specify a custom output path
python main.py --input data/2024.csv --output reports/2024_report.pdf

# Show help
python main.py --help
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All 18 tests cover the parser, analytics engine and edge cases (missing files, invalid columns, wrong data types).

---

## 💡 Motivation

> *Dieses Projekt entstand aus dem Wunsch, meine monatlichen Ausgaben automatisch auszuwerten — ohne manuelle Arbeit in Tabellenkalkulationen. Als angehender Entwickler wollte ich ein Tool bauen, das echten Nutzen hat und gleichzeitig sauberen, testbaren Python-Code demonstriert.*

This project was born from the desire to automatically analyse my monthly expenses — without manual spreadsheet work. As an aspiring developer, I wanted to build a tool with real practical value while demonstrating clean, testable Python code.

---

## 🛠️ Tech Stack

| Library      | Purpose                        |
|--------------|--------------------------------|
| `pandas`     | Data loading and analytics     |
| `matplotlib` | Chart generation               |
| `reportlab`  | PDF assembly                   |
| `pytest`     | Testing                        |

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

*Built as part of a Python portfolio for IT Ausbildung applications in Germany/Austria.*
