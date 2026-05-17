import json
import os
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)
DATA_FILE = Path("records.json")


def load_records():
    """从文件读取账目；如果文件不存在，就返回空列表。"""
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_records(records):
    """把账目保存到文件。"""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def calculate_summary(records):
    income = sum(record["amount"] for record in records if record["type"] == "收入")
    expense = sum(record["amount"] for record in records if record["type"] == "支出")

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
    }


@app.route("/")
def index():
    records = load_records()
    summary = calculate_summary(records)
    return render_template("index.html", records=records, summary=summary)


@app.route("/add", methods=["POST"])
def add_record():
    record_type = request.form.get("type")
    amount_text = request.form.get("amount", "")
    note = request.form.get("note", "").strip()

    if record_type not in ["收入", "支出"]:
        return redirect(url_for("index"))

    try:
        amount = float(amount_text)
    except ValueError:
        return redirect(url_for("index"))

    if amount <= 0:
        return redirect(url_for("index"))

    records = load_records()
    records.append(
        {
            "type": record_type,
            "amount": amount,
            "note": note or "无备注",
        }
    )
    save_records(records)

    return redirect(url_for("index"))


@app.route("/delete/<int:index>", methods=["POST"])
def delete_record(index):
    records = load_records()

    if 0 <= index < len(records):
        records.pop(index)
        save_records(records)

    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
