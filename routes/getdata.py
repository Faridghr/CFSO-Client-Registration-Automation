from pymongo import MongoClient
import os
import json
from flask import Flask, request, jsonify

def getdata_route(collection):
    try:
        # Extract rawRequest if it exists
        raw_request = request.form.get('rawRequest')
        if raw_request:
            data = json.loads(raw_request)
        else:
            data = request.get_json(force=True)

        result = collection.insert_one(data)
        return {
            'success': True,
            'message': 'Data saved to MongoDB',
            'document_id': str(result.inserted_id)
        }, 201 

    except Exception as e:
        return jsonify({'error': str(e)}), 400