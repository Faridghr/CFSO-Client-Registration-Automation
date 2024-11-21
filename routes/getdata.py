import json
from flask import request, jsonify
from services.database.mongodb import save_to_mongodb


def getdata_route(collection):
    try:
        # Extract rawRequest if it exists
        raw_request = request.form.get('rawRequest')
        if raw_request:
            data = json.loads(raw_request)
        else:
            data = request.get_json(force=True)

        # Save to MongoDB
        save_result = save_to_mongodb(collection, data)
        return jsonify(save_result), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400