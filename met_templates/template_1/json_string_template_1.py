json_string_template = [
    """    
    "resource_type": {{
      "id": {}
    }}
    """,
    """
    "creators": [{{
      "person_or_org": {{
        "family_name": {},
        "given_name": {},
        "identifiers": [{{
          "identifier": {},
          "scheme": {}
        }}],
        "name": {},
        "type": {}
      }},
      "affiliations": [{{
        "identifiers": [{{
          "identifier": {},
          "scheme": {}
        }}],
        "name": {}
      }}]
    }}]
    """,
    """
    "title": {}
    """,
    """
    "additional_titles": [{{
      "title": {},
      "type": {},
      "lang": {}
    }}]
    """,
    """
    "publisher": {}
    """,
    """
    "publication_date": {}
    """,
    """
    "subjects": [{{
      "subject": {},
      "identifier": {},
      "scheme": {}
    }}]
    """
]