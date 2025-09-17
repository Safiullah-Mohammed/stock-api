from flask import Flask, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Load CSV
df = pd.read_csv("stock_data.csv")

@app.route('/stock', methods=['GET'])
def get_stock():
    owner = request.args.get('owner', '').strip().lower()
    product = request.args.get('product', '').strip().lower()

    filtered_df = df.copy()

    if owner:
        filtered_df = filtered_df[
            filtered_df['OWNER'].str.lower().str.contains(owner, na=False)
        ]

    if product:
        filtered_df = filtered_df[
            filtered_df['PRODUCT_CODE'].str.lower().str.contains(product, na=False) |
            filtered_df['MASTER_CODE'].str.lower().str.contains(product, na=False)
        ]

    return jsonify(filtered_df.to_dict(orient='records'))

if __name__ == '__main__':
    # Get the port from the environment (Render sets this)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
