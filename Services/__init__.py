# This file makes the `utils` directory a Python module.
# You can import all utilities here if needed.

from .jotForm.get_image import get_image_from_url
from .jotForm.file_utils import process_file_uploads
from .jotForm.id_extraction import extract_form_id, extract_submission_id
from .jotForm.request_processor import process_request_data
from .database.mongodb import save_to_mongodb
from .email.email_service import send_email
from .validation.pr_card_validator import validate_pr_card
from .validation.e_transfer_validator import validate_e_transfer
from .ocr.image_to_text import image_To_Text, image_To_Text_Local_Model

__all__ = ["image_To_Text", "image_To_Text_Local_Model", "process_file_uploads", "extract_form_id", "extract_submission_id", "process_request_data", "save_to_mongodb", "send_email", "validate_pr_card", "validate_e_transfer", "get_image_from_url"]
