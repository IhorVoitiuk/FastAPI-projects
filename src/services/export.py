import csv
import json
from typing import List

from src.schemas import ContactResponse


def export_contacts_to_csv(contacts: List[ContactResponse]):
    """
    The export_contacts_to_csv function takes a list of ContactResponse objects and returns a CSV string.
    
    :param contacts: List[ContactResponse]: Specify the type of data that will be passed into the function
    :return: A string containing the csv data
    :doc-author: Ihor Voitiuk
    """
    csv_data = []
    for contact in contacts:
        csv_data.append([contact.first_name, contact.last_name, contact.email, contact.phone_number])

    csv_string = ""
    if csv_data:
        csv_string = "\n".join([",".join(row) for row in csv_data])

    return csv_string


def export_contacts_to_json(contacts: List[ContactResponse]):
    """
    The export_contacts_to_json function takes a list of ContactResponse objects and converts them to JSON.
    
    :param contacts: List[ContactResponse]: Specify the type of data that will be passed into the function
    :return: A string of json data
    :doc-author: Ihor Voitiuk
    """
    json_data = []
    for contact in contacts:
        json_data.append({
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone_number": contact.phone_number
        })

    json_string = json.dumps(json_data)

    return json_string
