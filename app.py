from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================================================
# Utility functions
# ==================================================
def categorize(minutes, low, medium):
    if minutes < low:
        return "Low", "green"
    elif minutes <= medium:
        return "Moderate", "orange"
    return "High", "red"

def compute_weekly_commute(df, wfo_days):
    df["weekly_commute_min"] = df["travel_time_min"] * wfo_days
    return df

def commute_burden_concentration(df):
    Low_cat = len(df[df['category']=='Low'])/len(df)*100
    mod_cat = len(df[df['category']=='Moderate'])/len(df)*100
    high_cat = len(df[df['category']=='High'])/len(df)*100
    return round(Low_cat,1), round(mod_cat,1), round(high_cat,1)

def office_location_fit_score(df, acceptable_commute_min):
    total_employees = len(df)
    if total_employees == 0:
        return 0, "N/A"
    fit_count = (df['travel_time_min'] <= acceptable_commute_min).sum()
    fit_pct = round((fit_count / total_employees) * 100,1)
    if fit_pct < 50:
        benchmark = "Poor"
    elif fit_pct < 70:
        benchmark = "Fair"
    else:
        benchmark = "Good"
    return fit_pct, benchmark

# ==================================================
# Routes
# ==================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error":"No file uploaded"}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    df = pd.read_excel(filepath)
    if not {"employee_id","latitude","longitude"}.issubset(df.columns):
        return jsonify({"error":"Excel must have employee_id, latitude, longitude"}), 400
    # Add dummy travel_time_min for demo
    df["travel_time_min"] = (df["latitude"] + df["longitude"]) % 60 + 20
    df[["category","color"]] = df["travel_time_min"].apply(lambda x: pd.Series(categorize(x, 30, 45)))
    return df.to_dict(orient="records")

@app.route("/run_scenario", methods=["POST"])
def run_scenario():
    data = request.get_json()
    employees = pd.DataFrame(data["employees"])
    wfo_days = int(data.get("wfo_days", 3))
    low = int(data.get("low", 30))
    medium = int(data.get("medium", 45))
    employees["weekly_commute_min"] = employees["travel_time_min"] * wfo_days
    employees[["category","color"]] = employees["travel_time_min"].apply(lambda x: pd.Series(categorize(x, low, medium)))
    Low_cat, mod_cat, high_cat = commute_burden_concentration(employees)
    fit_pct, fit_label = office_location_fit_score(employees, medium)
    return jsonify({
        "employees": employees.to_dict(orient="records"),
        "Low_cat": Low_cat,
        "mod_cat": mod_cat,
        "high_cat": high_cat,
        "office_fit_pct": fit_pct,
        "office_fit_label": fit_label
    })

if __name__ == "__main__":
    app.run(debug=True)