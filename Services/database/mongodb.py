def save_to_mongodb(collection, data):
    """
    Saves data to MongoDB.

    :param collection: MongoDB collection instance.
    :param data: Data dictionary to store.
    :return: MongoDB insertion result.
    """
    result = collection.insert_one(data)
    return {
        'success': True,
        'message': 'Data saved to MongoDB',
        'document_id': str(result.inserted_id)
    }
