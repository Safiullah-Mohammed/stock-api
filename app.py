from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Load your CSV directly
try:
    df = pd.read_csv("stock_data.csv")

    # Normalize headers (strip + uppercase)
    df.columns = [c.strip().upper() for c in df.columns]

    # Ensure correct types
    for col in ["OWNER", "PRODUCT_CODE", "MASTER_CODE"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    for col in ["STOCK", "FREE_STOCK"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    load_error = None
except Exception as e:
    df = None
    load_error = str(e)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"ok": True, "message": "Use /stock or /health"}), 200

@app.route("/health", methods=["GET"])
def health():
    if load_error:
        return jsonify({"ok": False, "error": load_error}), 500
    return jsonify({
        "ok": True,
        "rows": 0 if df is None else len(df),
        "columns": [] if df is None else list(df.columns)
    }), 200

@app.route("/stock", methods=["GET"])
def get_stock():
    if load_error:
        return jsonify({"error": "CSV load error", "details": load_error}), 500
    if df is None:
        return jsonify({"error": "CSV not loaded"}), 500

    # Query parameters
    owner = (request.args.get("owner") or "").strip().lower()
    product = (request.args.get("product") or "").strip().lower()

    # Optional pagination
    try:
        limit = int(request.args.get("limit", "0"))
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        return jsonify({"error": "limit/offset must be integers"}), 400

    filtered = df

    if "OWNER" in df.columns and owner:
        filtered = filtered[filtered["OWNER"].str.lower().str.contains(owner, na=False)]

    if product and "PRODUCT_CODE" in df.columns and "MASTER_CODE" in df.columns:
        m1 = filtered["PRODUCT_CODE"].str.lower().str.contains(product, na=False)
        m2 = filtered["MASTER_CODE"].str.lower().str.contains(product, na=False)
        filtered = filtered[m1 | m2]

    total = len(filtered)
    if offset > 0:
        filtered = filtered.iloc[offset:]
    if limit > 0:
        filtered = filtered.iloc[:limit]

    return jsonify({
        "ok": True,
        "total": total,
        "returned": len(filtered),
        "offset": offset,
        "limit": limit,
        "rows": filtered.to_dict(orient="records")
    }), 200

# Local dev only
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
