from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Load your CSV
df = pd.read_csv("stock_data.csv")

@app.route('/stock', methods=['GET'])
def get_stock():
    # Return the entire CSV as JSON
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
