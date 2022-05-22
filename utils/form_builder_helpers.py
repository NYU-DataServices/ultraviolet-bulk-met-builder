#
# Helper functions to handle step-by-step move from JSON to Database Record to HTML Form to JSON Hash (and back)
#

import json
from bs4 import BeautifulSoup
from utils.met_field_models import *


""" Helpers for parsing submitted form fields from user, pulling together field groupings based on <input> ids, etc. """

def form_inputs_parser(request_form_dict):
    """
    Parses form response into a nested dictionary that groups togther multival parents with
    children based on input names in user form in consistent field order. Also returns list of
    fields to enable further parsing based on field order position. Handles cases where
    additional fields vals have been added by user (e.g. a second or third creator)
    :param request_form_dict: dict
    :return: (dict, list)
    """
    initial_grouped_fields_dict = {}
    field_key_order = []
    for field_name, value in request_form_dict.items():
        grouping_key_parts = field_name.split("_")
        grouping_key, field_number, field_type = grouping_key_parts[-1], grouping_key_parts[1], grouping_key_parts[0]
        if grouping_key not in field_key_order:
            field_key_order.append(grouping_key)
        try:
            initial_grouped_fields_dict[grouping_key].append([field_number, field_type, value])
        except:
            initial_grouped_fields_dict[grouping_key] = [[field_number, field_type, value]]

    final_grouped_fields_dict = {}
    for field_grouping in initial_grouped_fields_dict:
        if len(initial_grouped_fields_dict[field_grouping]) == 1:
            final_grouped_fields_dict[field_grouping] = initial_grouped_fields_dict[field_grouping][0]
        else:
            final_grouped_fields_dict[field_grouping] = {"1": []}
            for val_pair in initial_grouped_fields_dict[field_grouping]:
                if val_pair[1][0:3] != "add":
                    final_grouped_fields_dict[field_grouping]["1"].append(val_pair)
                else:
                    try:
                        final_grouped_fields_dict[field_grouping][val_pair[1].split("-")[0][-1]].append(val_pair)
                    except:
                        final_grouped_fields_dict[field_grouping][val_pair[1].split("-")[0][-1]] = [val_pair]
    return final_grouped_fields_dict, field_key_order


def template_to_json_builder(json_template, request_form_dict):
    """
    Builds a JSON record (a string) out of the input field vals submitted by user using the template provided
    in met_templates/template_#/ directory
    :param json_template: str
    :param request_form_dict: dict
    :return: str
    """
    final_grouped_fields_dict, field_key_order = form_inputs_parser(request_form_dict)
    count = 0
    met_json_complete = {}
    while count < len(json_template):
        if isinstance(final_grouped_fields_dict[field_key_order[count]], dict):
            if len(final_grouped_fields_dict[field_key_order[count]]) == 1:
                met_json_complete.update(json.loads("{" + json_template[count].format(*['"' + i[2] + \
                                                    '"' for i in final_grouped_fields_dict[field_key_order[count]]["1"]]) + "}"))
            else:
                multival_parent_key = str(re.search(r'\"[_a-z]{1,}\"', json_template[count])[0].replace('"', ''))
                multival_dict = {multival_parent_key:[]}
                for grouping_key in final_grouped_fields_dict[field_key_order[count]]:
                    single_append_rec = json_template[count].split(': [', 1)[1].rstrip()[0:-1]
                    multival_dict[multival_parent_key].append(json.loads(single_append_rec.format(*['"' + i[2] + '"' for i \
                                                                in final_grouped_fields_dict[field_key_order[count]][grouping_key]])))
                met_json_complete.update(multival_dict)
        else:
            met_json_complete.update(json.loads("{" + json_template[count].format('"' + \
                                              final_grouped_fields_dict[field_key_order[count]][2] + '"') + "}"))
        count+=1

    return json.dumps(met_json_complete)


def field_vals_to_db_rows(field_vals_dict, record_id, template_id):
    """
    Transforms nested dictionary representation of form-submitted values into row-wise representation that can be inserted in DB
    :param field_vals_dict: dict
    :param record_id: str
    :param template_id: str
    :return: list
    """
    rows_list = []
    field_grouping_num = 1
    for key, val_group in field_vals_dict.items():
        if isinstance(val_group, list):
            rows_list.append([record_id, val_group[0], int(template_id), field_grouping_num, 0, val_group[1], val_group[2]])
            field_grouping_num+=1
        else:
            for k, sub_val_group in val_group.items():
                for sub_val in sub_val_group:
                    added_field = 1 if sub_val[1][0:3] == "add" else 0
                    try:
                        sub_val_field_type = sub_val[1].split('-')[1]
                    except:
                        sub_val_field_type = sub_val[1]
                    rows_list.append([record_id, sub_val[0], int(template_id), field_grouping_num, added_field, sub_val_field_type, sub_val[2]])
            field_grouping_num+=1
    return rows_list


""" HTML form helper functions for building record editing forms. Sort and organize query responses from DB for html form creation """

def arrange_children(template_fields):
    """
    Sorting function to arrange record vvalues obtained from database into arranged dictionary
    that can be built into an HTML form
    :param template_fields: dict
    :return: dict
    """
    for field_num in sorted(set(list(template_fields.keys()))):
        if len(template_fields[field_num]) > 1:
            pointer = len(template_fields[field_num]) - 1
            while pointer > 0:
                if template_fields[field_num][pointer]["parent_field"] != 0:
                    for field in template_fields[field_num]:
                        if field["field_num"] == template_fields[field_num][pointer]["parent_field"]:
                            field["children"].insert(0, template_fields[field_num][pointer])
                else:
                    pass
                pointer-=1
    return {i:template_fields[i][0] for i in template_fields}


def multi_single_field_helper(field_depth, default_value=""):
    """
    Helper function to identify constituent parts of dictionary representation of a single record and instantiate
    them as SingleField, EnumField, and IdentifierField classes
    :param field_depth: dict
    :param default_value: str
    :return:
    """
    head_val = False if field_depth["header_val"] == "NONE" else field_depth["header_val"]

    if field_depth["field_class_type"] == "SingleField":
        return SingleField(field_depth["field_num"],
                           field_depth["label_name"],
                           field_depth["json_name"],
                           default_value,
                           main_label_size=head_val)
    elif field_depth["field_class_type"] == "EnumField":
        return EnumField(field_depth["field_num"],
                         field_depth["label_name"],
                         field_depth["json_name"],
                         [i for i in field_depth["enum_options"].split(',')],
                         default_value,
                         main_label_size=head_val)
    elif field_depth["field_class_type"] == "IdentifierField":
        return IdentifierField(field_depth["field_num"], default_vals_list=default_value)



def parse_field_info_db(template_fields):
    """
    For use of new record creation only. This function parses the full set of fields as dict records from queries to db
    and turns them into HTML via the field classes
    :param template_fields: dict
    :return: str
    """

    template_fields = arrange_children(template_fields)

    met_form_template = []
    for field_num in sorted(set(list(template_fields.keys()))):
        # Must be a SingleField or EnumField if there are no child fields
        if len(template_fields[field_num]["children"]) == 0:
            met_form_template.append(multi_single_field_helper(template_fields[field_num]).html())

        elif template_fields[field_num]["field_class_type"] == "MultiVals":
            list_multivals = []
            if template_fields[field_num]["children"][0]["field_class_type"] == "MultiDictMixer":
                multidictmixer = []
                for subfield_depth1 in template_fields[field_num]["children"][0]["children"]:
                    if subfield_depth1["field_class_type"] == "MultiSingleField":
                        sub_multi_single_fields = []
                        for subfield_depth2 in subfield_depth1["children"]:
                            if subfield_depth2["field_class_type"] != "MultiSingleField":
                                    sub_multi_single_fields.append(multi_single_field_helper(subfield_depth2))
                            else:
                                sub_multi_single_fields.append(MultiSingleField(subfield_depth2["label_name"],
                                                                                subfield_depth2["json_name"],
                                                                                [multi_single_field_helper(i) for i \
                                                                                 in subfield_depth2["children"]]))

                        multidictmixer.append(MultiSingleField(subfield_depth1["label_name"],
                                                               subfield_depth1["json_name"],
                                                               sub_multi_single_fields,
                                                               subfield_depth1["header_val"]))

                    else:
                        multidictmixer.append(multi_single_field_helper(subfield_depth1))
                list_multivals.append(MultiDictMixer(multidictmixer))

            accord_val = True if template_fields[field_num]["accordion"] == "True" else False
            row_val = True if template_fields[field_num]["add_row"] == "True" else False

            met_form_template.append(MultiVals(template_fields[field_num]["label_name"],
                                               template_fields[field_num]["json_name"],
                                               list_multivals,
                                               template_fields[field_num]["header_val"],
                                               accordion=accord_val,
                                               allow_add_row=row_val).html)

        elif template_fields[field_num]["field_class_type"] == "MultiSingleField":
            list_multivals = []
            for subfield in template_fields[field_num]["children"]:
                list_multivals.append(multi_single_field_helper(subfield))

            accord_val = True if template_fields[field_num]["accordion"] == "True" else False
            row_val = True if template_fields[field_num]["add_row"] == "True" else False

            met_form_template.append(MultiSingleField(template_fields[field_num]["label_name"],
                                                      template_fields[field_num]["json_name"],
                                                      list_multivals,
                                                      template_fields[field_num]["header_val"],
                                                      accordion=accord_val,
                                                      allow_add_row=row_val).html())

    return "".join([i for i in met_form_template])


def arrange_template_fields(template_fields):
    """
    Function to build the modal popup for creating add'l records, take template info from DB,
     and arrange it into a parseable list of field labels
    :param template_fields: dict
    :return: list
    """
    field_label_list = []
    fieldcount = 0
    for field_group in template_fields.items():
        for field in field_group[1]:
            if field['field_class_type'] in ['EnumField', 'SingleField']:
                if field['parent_field'] == 0:
                    field_label_list.append((0, field['label_name'], "N/A"))
                    field_label_list.append((1, field['label_name'], field['field_num'], fieldcount))
                    fieldcount+=1
                else:
                    field_label_list.append((1, field['label_name'], field['field_num'], fieldcount))
                    fieldcount += 1
            elif field['field_class_type'] == 'IdentifierField':
                field_label_list.append((1, 'Identifier', field['field_num'], fieldcount))
                fieldcount += 1
                field_label_list.append((1, 'Select schema', field['field_num'], fieldcount))
                fieldcount += 1
            elif field['parent_field'] == 0:
                field_label_list.append((0, field['label_name'], ))
    return field_label_list


def template_html_field_analyzer(field_num, template_fields, list_default_values, vcounter):
    """
    A sub-function used by parse_previous_field_info_db() function. This function steps through the dictionary
    representation of the template and instantiates fields (using Field Class models) with passed default values
    The vcounter param is the index location corresponding to each basic field stored in the DB in the same order as it
    is presented on the form
    :param field_num: int
    :param template_fields: dict
    :param list_default_values: list
    :param vcounter: int
    :return: (list, int)
    """
    met_form_template = []
    # Must be a SingleField or EnumField if no children present
    if len(template_fields[field_num]["children"]) == 0:
        met_form_template.append(
            multi_single_field_helper(template_fields[field_num], list_default_values[vcounter][6]).html())
        vcounter += 1
    elif template_fields[field_num]["field_class_type"] == "MultiVals":
        list_multivals = []
        if template_fields[field_num]["children"][0]["field_class_type"] == "MultiDictMixer":
            multidictmixer = []
            for subfield_depth1 in template_fields[field_num]["children"][0]["children"]:
                if subfield_depth1["field_class_type"] == "MultiSingleField":
                    sub_multi_single_fields = []
                    for subfield_depth2 in subfield_depth1["children"]:
                        if subfield_depth2["field_class_type"] != "MultiSingleField":
                            if subfield_depth2["field_class_type"] == "IdentifierField":
                                sub_multi_single_fields.append(
                                    multi_single_field_helper(subfield_depth2,
                                                            [list_default_values[vcounter][6],
                                                            list_default_values[vcounter + 1][6]])
                                    )
                                vcounter += 2
                            else:
                                sub_multi_single_fields.append(
                                    multi_single_field_helper(subfield_depth2, list_default_values[vcounter][6])
                                    )
                                vcounter += 1
                        else:
                            built_fields_list = []
                            for i in subfield_depth2["children"]:
                                if i["field_class_type"] == "IdentifierField":
                                    built_fields_list.append(multi_single_field_helper(i, [list_default_values[vcounter][6],
                                                                                           list_default_values[vcounter + 1][6]]))
                                    vcounter += 2
                                else:
                                    built_fields_list.append(multi_single_field_helper(i, list_default_values[vcounter][6]))
                                    vcounter += 1
                            sub_multi_single_fields.append(
                                MultiSingleField(subfield_depth2["label_name"], subfield_depth2["json_name"],
                                                 built_fields_list))

                    multidictmixer.append(
                        MultiSingleField(subfield_depth1["label_name"],
                                         subfield_depth1["json_name"],
                                         sub_multi_single_fields,
                                         subfield_depth1["header_val"]))

                else:
                    if subfield_depth1["field_class_type"] == "IdentiferField":
                        multidictmixer.append(
                            multi_single_field_helper(subfield_depth1,
                                                    [list_default_values[vcounter][6],
                                                    list_default_values[vcounter + 1][6]])
                            )
                        vcounter += 2
                    else:
                        multidictmixer.append(multi_single_field_helper(subfield_depth1,
                                                                        list_default_values[vcounter][6]))
                        vcounter += 1

            list_multivals.append(MultiDictMixer(multidictmixer))

        accord_val = True if template_fields[field_num]["accordion"] == "True" else False
        row_val = True if template_fields[field_num]["add_row"] == "True" else False

        met_form_template.append(
            MultiVals(template_fields[field_num]["label_name"], template_fields[field_num]["json_name"], list_multivals,
                      template_fields[field_num]["header_val"], accordion=accord_val, allow_add_row=row_val).html)

    elif template_fields[field_num]["field_class_type"] == "MultiSingleField":
        list_multivals = []
        for subfield in template_fields[field_num]["children"]:
            if subfield["field_class_type"] == "IdentifierField":
                list_multivals.append(multi_single_field_helper(subfield, [list_default_values[vcounter][6],
                                                                           list_default_values[vcounter + 1][6]]))
                vcounter += 2
            else:
                list_multivals.append(multi_single_field_helper(subfield, list_default_values[vcounter][6]))
                vcounter += 1

        accord_val = True if template_fields[field_num]["accordion"] == "True" else False
        row_val = True if template_fields[field_num]["add_row"] == "True" else False

        met_form_template.append(MultiSingleField(template_fields[field_num]["label_name"], template_fields[field_num]["json_name"],
                             list_multivals, template_fields[field_num]["header_val"], accordion=accord_val,
                             allow_add_row=row_val).html())

    return met_form_template, vcounter


def parse_previous_field_info_db(template_fields, list_default_values):
    """
    For use of creating form from previous record. This function parses template (represented in dictionary form),
     populates them using the list of field values, and turns them into HTML form with default values set (e.g. field
     input values filled in).
    :param template_fields: dict
    :param list_default_values: list
    :return: str
    """
    template_fields = arrange_children(template_fields)
    accordion_default_values = {}
    for d_val in [i for i in list_default_values if i[4] == 1]:
        try:
            accordion_default_values[d_val[3]].append(d_val)
        except:
            accordion_default_values[d_val[3]] = [d_val]
    list_default_values = [i for i in list_default_values if i[4] != 1]

    vcounter = 0
    met_form_template = []
    for field_group_num in sorted(set(list(template_fields.keys()))):
        met_addendum_list, vcounter = template_html_field_analyzer(field_group_num,
                                                                   template_fields,
                                                                   list_default_values,
                                                                   vcounter)
        met_form_template+=met_addendum_list

        if field_group_num in accordion_default_values:
            # Check to see if we have multiple added field groupings:
            num_fields_per_grouping = len([i for i in list_default_values if i[3] == field_group_num])
            chunked_list = [accordion_default_values[field_group_num][i:i + num_fields_per_grouping] \
                            for i in range(0, len(accordion_default_values[field_group_num]), num_fields_per_grouping)]
            r_count = 2
            for vals_grouping in chunked_list:
                accordion_html_list, local_counter = template_html_field_analyzer(field_group_num, template_fields, vals_grouping, 0)

                accordion_f_block = BeautifulSoup(accordion_html_list[0], "lxml")
                original_f_block = BeautifulSoup(met_form_template[-1], "lxml")

                accordion_added_field_html = accordion_f_block.contents[0].find_all("div", {'id': re.compile(r'met_grouping_fields_wrap')})[0]
                original_added_field_html = original_f_block.contents[0].find_all("div", {'id': re.compile(r'met_grouping_fields_wrap')})[0]

                swap_out_uuid = accordion_added_field_html["id"].split("_")[-1]
                short_uuid = original_added_field_html["id"].split("_")[-1]

                modified_id = "removeclass_" + short_uuid + "_" + str(r_count)
                accordion_added_field_html["id"] = modified_id
                addinputstring = "addedInput" + str(r_count) + "-"
                new_accordion_html = str(accordion_added_field_html).replace(
                    "identifierField", addinputstring + "identifierField").replace(
                    "identifierSelectField", addinputstring + "identifierSelectField").replace(
                    "singleField", addinputstring + "singleField").replace(
                    "enumField", addinputstring + "enumField")
                new_accordion_html = met_form_template[-1][:-24] + new_accordion_html + "</div></div></div></div>"
                new_accordion_html = new_accordion_html.replace("visibility:hidden", "visibility: visible").replace(swap_out_uuid, short_uuid)

                met_form_template[-1] = new_accordion_html
                r_count+=1

    return met_form_template




""" Future work: parsing JSON schema for template and record creation """

def parse_invenio_json(inv_json, start_key):
    """
    TO DO: Take InvenioRDM JSON and parse it for template record in DB
    :param inv_json:
    :param start_key:
    :return:
    """
    list_fields = []

    def extract(inv_json, list_fields, start_key):
        if isinstance(inv_json, dict):
            for k, v in inv_json.items():
                if isinstance(v, (dict, list)):
                    extract(v, list_fields, start_key)
                else:
                    list_fields.append(v)
        elif isinstance(inv_json, list):
            for item in inv_json:
                extract(item, list_fields, start_key)
        return list_fields

    return extract(inv_json, list_fields, start_key)
