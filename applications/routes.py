from flask import current_app as app
from applications import db
from flask import render_template,flash,redirect,url_for
from applications.forms import UserInputForm
from applications.models import IncomeExpenses
from sqlalchemy import extract
import json
from datetime import datetime
def register_routes(app):
    @app.route("/")
    def index():
        entries=IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
        return render_template("index.html",title="expensses",entries=entries)

    @app.route("/add",methods=['GET','POST'])
    def add_expense():
        form=UserInputForm()
        if form.validate_on_submit():
            entry=IncomeExpenses(type=form.type.data,amount=form.amount.data,category=form.category.data)
            db.session.add(entry)
            db.session.commit()
            flash("succesfully entry",'success')
            return redirect(url_for('index'))
        return render_template("add.html",title="add",form=form)
    @app.route('/delete-post/<int:entry_id>')
    def delete(entry_id):
        entry=IncomeExpenses.query.get_or_404(int(entry_id))
        db.session.delete(entry)
        db.session.commit()
        flash("Deletion was succesful",'success')
        return redirect(url_for('index'))
    @app.route('/Dashboard')
    def dashboard():
        try:
            # Fetch data for Income vs Expenses pie chart
            income_vs_expenses = db.session.query(
                db.func.sum(IncomeExpenses.amount), IncomeExpenses.type
            ).group_by(IncomeExpenses.type).order_by(IncomeExpenses.type).all()
            income_vs_expense_data = [float(row[0] or 0) for row in income_vs_expenses]

            # Category comparison
            category_comparison = db.session.query(
                db.func.sum(IncomeExpenses.amount), IncomeExpenses.category
            ).group_by(IncomeExpenses.category).order_by(IncomeExpenses.category).all()
            category_labels = [row[1] for row in category_comparison]
            category_amounts = [float(row[0] or 0) for row in category_comparison]

            # Over time expenditure
            dates = db.session.query(
                db.func.sum(IncomeExpenses.amount), IncomeExpenses.date
            ).group_by(IncomeExpenses.date).order_by(IncomeExpenses.date).all()
            over_time_expenditure = [float(row[0] or 0) for row in dates]
            dates_label = [row[1].strftime("%m-%d-%y") if row[1] else "N/A" for row in dates]

            # Monthly income
            try:
                monthly_income = db.session.query(
                    db.func.strftime('%Y-%m', IncomeExpenses.date),
                    db.func.sum(IncomeExpenses.amount)
                ).filter(db.func.lower(IncomeExpenses.type) == 'income') \
                .group_by(db.func.strftime('%Y-%m', IncomeExpenses.date)).all()
            except Exception as e:
                print("Error in monthly_income:", e)
                monthly_income = []

            # Monthly expense
            try:
                monthly_expense = db.session.query(
                    db.func.strftime('%Y-%m', IncomeExpenses.date),
                    db.func.sum(IncomeExpenses.amount)
                ).filter(db.func.lower(IncomeExpenses.type) == 'expense') \
                .group_by(db.func.strftime('%Y-%m', IncomeExpenses.date)).all()
            except Exception as e:
                print("Error in monthly_expense:", e)
                monthly_expense = []

            # Build month -> amount maps
            income_dict = {month: float(amount or 0) for month, amount in monthly_income}
            expense_dict = {month: float(amount or 0) for month, amount in monthly_expense}
            months = sorted(set(income_dict.keys()) | set(expense_dict.keys()))
            income_data = [income_dict.get(month, 0) for month in months]
            expense_data = [expense_dict.get(month, 0) for month in months]

            # Final debug print
            print("months:", months)
            print("income_data:", income_data)
            print("expense_data:", expense_data)

            return render_template("dashboard.html",
                                income_vs_expenses=income_vs_expense_data,
                                category_labels=category_labels,
                                category_amounts=category_amounts,
                                months=months,
                                income_data=income_data,
                                expense_data=expense_data,
                                over_time_expenditure=over_time_expenditure,
                                dates_label=dates_label)

        except Exception as final_error:
            print("CRITICAL ERROR:", final_error)
            return "Something went wrong. Check console for details."