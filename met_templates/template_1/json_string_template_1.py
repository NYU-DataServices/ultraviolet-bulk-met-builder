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
      }}],
      "role": {}
    }}]
    """,
    """
    "title": {}
    """,
    """
    "additional_titles": [{{
      "title": {},
      "type": {{
	   "id": {},
	   "title": {{
	   "en": {}
	   }}
	   }},
      "lang": {{
	 "id": {}
	 }}
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
      "subject": {}
    }}]
    """,
    """
    "description": {}
    """,
    """
    "additional_descriptions": [{{
    "description": {},
	"type": {{
	    "id": {},
		"title": {{
		    "en": {}
		}}
	}},
	"lang": {{
	    "id": {}
		}}
    }}]
    """,
    """
    "rights": [{{
    "title": {{
	"en": {}
	}},
    "description": {{
	"en": {} 
	}},
    "link": {}
    }}]
    """,
    """
    "contributors": [{{
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
          }}]
        }}],
       "role": {}
    }}]
    """,
    """
    "languages": [{{
    "id": {}
	}}]
    """,
    """
    "dates": [{{
    "date": {},
    "type": {{
      "id": {},
      "title": {{
        "en": {}
      }}
    }},
    "description": {}
    }}]
    """,
    """
    "version": {}
    """,
    """
    "identifiers": [{{
    "identifier": {},
    "scheme": {}
    }}]
    """,
    """
    "related_identifiers": [{{
    "identifier": {},
    "scheme": {},
    "relation_type": {{
      "id": {},
      "title": {{
        "en": {}
      }}
    }},
    "resource_type": {{
      "id": {},
      "title": {{
        "en": {}
      }}
    }}
    }}]
    """
]