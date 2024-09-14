from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/get-commentary', methods=['GET'])
def get_data():
    data = {"message": "Received Commentary"}
    return jsonify(data)

@app.route('/video', methods=['POST'])
def post_data():
    video_data = request.json
    response = {"message": "Received Video", "data": video_data}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

