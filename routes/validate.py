from flask import request, jsonify
from services.jotForm.request_processor import process_request_data
from services.validation.pr_card_validator import validate_pr_card
from services.validation.e_transfer_validator import validate_e_transfer
from services.email.email_service import send_email
from services.database.mongodb import save_to_mongodb

import json


def validate_route(mail, collection):
    try:
        # Extract query parameters
        pr_amount = request.args.get('pr_amount')
        normal_amount = request.args.get('normal_amount')

        # Parse request body
        raw_request = request.form.get('rawRequest')
        if raw_request:
            data = json.loads(raw_request)
        else:
            data = request.get_json(force=True)

        # Process request data
        res = process_request_data(data, pr_amount, normal_amount)

        # Validate PR card
        pr_validation_result = validate_pr_card(
            res.get('PR_Status'),
            res.get('PR_Card_Number'),
            res.get('Full_Name'),
            res.get('PR_File_Upload_URLs'),
        )
        res.update(pr_validation_result)

        # Validate e-transfer
        e_transfer_validation_result = validate_e_transfer(
            res.get('Payer_Full_Name'),
            res.get('Amount_of_Payment'),
            res.get('E_Transfer_File_Upload_URLs'),
        )
        res.update(e_transfer_validation_result)

        # Send email
        send_email(res.get('PR_Status'), mail, res)

        # Save to MongoDB
        save_result = save_to_mongodb(collection, res)
        return jsonify(save_result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
