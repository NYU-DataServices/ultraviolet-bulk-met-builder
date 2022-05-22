#
# Classes representing the basic component parts of the metadata schema as fields
# and build html forms
#


import shortuuid
import re


class SingleField():
    """Used for key-value pairs with a single string as value and represented as text input in html form"""

    def __init__(self, fieldNumber, labelName, jsonName, default_value, main_label_size=False):
        self.fieldNumber = fieldNumber
        self.labelName = labelName
        self.jsonName = jsonName
        self.default_value = default_value
        self.main_label_size = main_label_size

    def html(self, parent_append_id=False):
        if not parent_append_id:
            parent_append_id = shortuuid.uuid()[0:5]
        elct = shortuuid.uuid()[0:5]
        if self.default_value != "":
            pl_hlder = 'value="' + self.default_value + '"'
        else:
            pl_hlder = ""
        if self.main_label_size != False:
            insert_label = '<h{}>{}</h{}>'.format(self.main_label_size, self.labelName, self.main_label_size)
        else:
            insert_label = self.labelName

        return '<label for="text" class="col-md-2 col-form-label">{}</label>' \
               '<div class="col-md-4"><div class="input-group">' \
               '<input type="text" class="form-control" id="{}" name="singleField_{}_{}_{}_{}" {}>' \
               '</div></div>'.format(insert_label, elct, self.fieldNumber, self.jsonName, elct, parent_append_id, pl_hlder)


class EnumField():
    """Used for key-value pairs with a single string as value and represented as dropdown input in html form"""

    def __init__(self, fieldNumber, labelName, jsonName, default_list_values, default_value="", main_label_size=False):
        self.fieldNumber = fieldNumber
        self.labelName = labelName
        self.jsonName = jsonName
        self.default_list_values = default_list_values
        self.default_value = default_value
        self.main_label_size = main_label_size

    def html(self, parent_append_id=False):
        if not parent_append_id:
            parent_append_id = shortuuid.uuid()[0:5]
        elct = shortuuid.uuid()[0:5]
        if self.main_label_size != False:
            insert_label = '<h{}>{}</h{}>'.format(self.main_label_size, self.labelName, self.main_label_size)
        else:
            insert_label = self.labelName

        label_html = '<label for="select" class="col-md-2 col-form-label">{}</label>' \
                     '<div class="col-md-4"><select id="{}" name="enumField_{}_{}_{}_{}" ' \
                     'class="custom-select">'.format(insert_label, elct, self.fieldNumber, self.jsonName, elct, parent_append_id) + \
                    "".join(['<option value="{}">{}</option>'.format(defval.lower(), defval)
                             for defval in self.default_list_values]) + \
                     '</select></div>'

        if self.default_value != "":
            selected_value_reg = re.compile('value=\"{}\"'.format(self.default_value))
            return re.sub(selected_value_reg, 'value="{}" selected'.format(self.default_value), label_html)
        else:
            return label_html


class MultiVals():
    """Used for complex key-value pairs with a list/array as a value, and requires subvalues consisting of complex or simple fields, or both"""

    def __init__(self, labelName, jsonName, values_list, main_label_size=False, accordion=False, allow_add_row=False):
        self.labelName = labelName
        self.jsonName = jsonName
        self.value_list = values_list
        elct = shortuuid.uuid()[0:5]
        if not main_label_size:
            insert_label = '<div class="col-md-2">{}</div>'.format(labelName)
        else:
            if not accordion:
                insert_label = '<div class="col-md-2"><h{}>{}</h{}></div>'.format(main_label_size, labelName, main_label_size)

            else:
                insert_label = '<div class="accordion md-accordion" id="accordion_{}" role="tablist" aria-multiselectable="true">' \
                               '<div class="card border-0 col-md-8"><div class="card-header" role="tab" id="heading_{}">' \
                               '<a class="collapsed" data-toggle="collapse" data-parent="#accordion_{}" ' \
                               'href="#collapse_{}" aria-expanded="false" aria-controls="collapse_{}">'.format(elct, elct, elct, elct, elct) + \
                               '<h{} class="mb-0">{} <i class="fas fa-angle-down rotate-icon"></i>' \
                               '</h{}></a></div>'.format(main_label_size, labelName, main_label_size)

        if not allow_add_row and accordion:
            build_html = insert_label + '<div id="collapse_{}" class="collapse" role="tabpanel" ' \
                                        'aria-labelledby="heading_{}" data-parent="#accordion_{}">' \
                                        '<div class="card-body">'.format(elct, elct, elct) + \
                         "".join([value.html(elct) for value in values_list]) + '</div></div></div></div>'

        elif not allow_add_row and not accordion:
            build_html = insert_label + "".join([value for value in values_list])

        elif allow_add_row and not accordion:
            build_html = '{}<div class="col-md-4">'.format(insert_label) + \
                         '<div class="input-group-btn"><button id="success_button_{}" ' \
                         'class="btn btn-success" type="button" onclick="met_grouping_fields({});">' \
                         '<span>Add another</span></button></div><div class="input-group-btn">' \
                         '<button style="visibility:hidden;" id="danger_button_{}" ' \
                         'class="btn btn-danger" type="button" onclick=remove_met_grouping_fields(\'{}\');>' \
                         '<span>Remove</span></button></div>'.format(elct, "'met_grouping_fields_wrap_" + elct + "'", elct, elct) + \
                         '<div id="{}">'.format("met_grouping_fields_wrap_" + elct, elct) + \
                         "".join([value.html(elct) for value in values_list]) + '<hr/></div></div>'
        else:
            build_html = insert_label + \
                         '<div id="collapse_{}" class="collapse" role="tabpanel" aria-labelledby="heading_{}" data-parent="#accordion_{}">' \
                         '<div class="card-body">'.format(elct, elct, elct) + \
                         '<div class="input-group-btn"><button id="success_button_{}" class="btn btn-success" type="button" onclick="met_grouping_fields({});">' \
                         '<span>Add another</span></button></div><div class="input-group-btn">' \
                         '<button style="visibility:hidden;" id="danger_button_{}" ' \
                         'class="btn btn-danger" type="button" onclick=remove_met_grouping_fields(\'{}\');>' \
                         '<span>Remove</span></button></div>'.format(elct, "'met_grouping_fields_wrap_" + elct + "'", elct, elct) + \
                         '<div id="{}">'.format("met_grouping_fields_wrap_" + elct, elct) + \
                         "".join([value.html(elct) for value in values_list]) + '<hr/></div></div></div></div></div>'

        self.html = build_html


class MultiDictMixer():
    """Used to construct complex multivalue key-value arrays/dictionaries that populate MultiVals objects"""

    def __init__(self, list_field_dict):
        self.list_field_dict = list_field_dict

    def html(self, parent_pass_id=False):
        if parent_pass_id != False:
            elct = parent_pass_id
        else:
            elct = shortuuid.uuid()[0:5]
        return "".join([list_field.html(elct) for list_field in self.list_field_dict])


class MultiSingleField():
    """Used to construct a single key-value whose children consist of multiple Single, Enum, or Identifier Fields"""

    def __init__(self, labelName, jsonName, listSingleVals, main_label_size=False, accordion=False, allow_add_row=False):
        self.labelName = labelName
        self.jsonName = jsonName
        self.listSingleVals = listSingleVals
        self.num_fields = len(listSingleVals)
        self.main_label_size = main_label_size
        self.accordion = accordion
        self.allow_add_row = allow_add_row

    def html(self, parent_pass_id=False):
        if parent_pass_id != False:
            elct = parent_pass_id
        else:
            elct = shortuuid.uuid()[0:5]
        if not self.main_label_size:
            insert_label = '<div class="col-md-2">{}</div>'.format(self.labelName)
        else:
            if not self.accordion:
                insert_label = '<div class="col-md-2"><h{}>{}</h{}></div>'.format(self.main_label_size, self.labelName,
                                                                                  self.main_label_size)

            else:
                insert_label = '<div class="accordion md-accordion" id="accordion_{}" role="tablist" aria-multiselectable="true">' \
                               '<div class="card border-0 col-md-8"><div class="card-header" role="tab" id="heading_{}">' \
                               '<a class="collapsed" data-toggle="collapse" data-parent="#accordion_{}" ' \
                               'href="#collapse_{}" aria-expanded="false" aria-controls="collapse_{}">'.format(elct, elct, elct, elct, elct) + \
                               '<h{} class="mb-0">{} <i class="fas fa-angle-down rotate-icon"></i>' \
                               '</h{}></a></div>'.format(self.main_label_size, self.labelName, self.main_label_size)

        if not self.allow_add_row and self.accordion:
            build_html = insert_label + \
                         '<div id="collapse_{}" class="collapse" role="tabpanel" aria-labelledby="heading_{}" data-parent="#accordion_{}">' \
                         '<div class="card-body">'.format(elct, elct, elct) + \
                         "".join([fieldval.html(elct) for fieldval in self.listSingleVals]) + '</div></div></div></div>'

        elif not self.allow_add_row and not self.accordion:
            build_html = insert_label + "".join([fieldval.html(elct) for fieldval in self.listSingleVals])

        elif self.allow_add_row and not self.accordion:
            build_html = '{}<div class="col-md-4">'.format(insert_label) + \
                         '<div class="input-group-btn"><button id="success_button_{}" ' \
                         'class="btn btn-success" type="button" onclick="met_grouping_fields({});">' \
                         '<span>Add another</span></button></div>' \
                         '<div class="input-group-btn"><button style="visibility:hidden;" ' \
                         'id="danger_button_{}" class="btn btn-danger" type="button" onclick=remove_met_grouping_fields(\'{}\');>' \
                         '<span>Remove</span></button></div>'.format(elct, "'met_grouping_fields_wrap_" + elct + "'", elct, elct) + \
                         '<div id ="{}">'.format("met_grouping_fields_wrap_" + elct, elct) + \
                         "".join([fieldval.html(elct) for fieldval in self.listSingleVals]) + '<hr/></div></div>'

        else:
            build_html = insert_label + \
                         '<div id="collapse_{}" class="collapse" role="tabpanel" aria-labelledby="heading_{}" ' \
                         'data-parent="#accordion_{}"><div class="card-body">'.format(elct, elct, elct) + \
                         '<div class="input-group-btn"><button id="success_button_{}" ' \
                         'class="btn btn-success" type="button" onclick="met_grouping_fields({});">' \
                         '<span>Add another</span></button></div><div class="input-group-btn">' \
                         '<button style="visibility:hidden;" id="danger_button_{}" ' \
                         'class="btn btn-danger" type="button" onclick=remove_met_grouping_fields(\'{}\');>' \
                         '<span>Remove</span></button></div>'.format(elct, "'met_grouping_fields_wrap_" + elct + "'", elct, elct) + \
                         '<div id ="{}">'.format("met_grouping_fields_wrap_" + elct, elct) + \
                        "".join([fieldval.html(elct) for fieldval in self.listSingleVals]) + '<hr/></div></div></div></div></div>'

        return build_html



class IdentifierField():
    """Used to generate the full identifer field set (label, identifier value, identifier type)"""

    def __init__(self, fieldNumber, enum_options, main_label_size=False, default_vals_list=False):
        self.fieldNumber = fieldNumber
        self.placeholder = "e.g. orcid.org/0000-0001-0000-0000"
        self.schema_options = enum_options
        self.jsonName = "identifiers"
        self.main_label_size = main_label_size
        self.default_vals_list = default_vals_list

    def html(self, parent_append_id=False):
        if not parent_append_id:
            parent_append_id = shortuuid.uuid()[0:5]
        elct = shortuuid.uuid()[0:5]
        if self.placeholder != "":
            pl_hlder = 'placeholder="' + self.placeholder + '"'
        else:
            pl_hlder = ""
        if self.main_label_size != False:
            insert_label = '<h{}>{}</h{}>'.format(self.main_label_size, "Identifier", self.main_label_size)
        else:
            insert_label = "Identifier"
        label_html = '<label for="select" class="col-md-2 col-form-label">{}</label>' \
                     '<div class="col-md-4"><input type="text" class="form-control" ' \
                     'id="{}" name="identifierField_{}_identifier_{}_{}" {}>'.format(insert_label, elct, self.fieldNumber, elct, parent_append_id, pl_hlder) + \
                     '</div>' + '<label for="select" class="col-md-2 col-form-label">Select schema</label>' \
                     '<div class="col-md-4"><select id="select_{}" name="identifierSelectField_{}_scheme_{}_{}" ' \
                      'class="custom-select">'.format(elct, self.fieldNumber, elct, parent_append_id) + \
                     "".join(['<option value="{}">{}</option>'.format(defval.lower(), defval) for defval in self.schema_options]) + '</select></div>'
        if self.default_vals_list in [False, ""]:
            return label_html
        else:
            label_html = label_html.replace('placeholder="' + self.placeholder + '"', 'value="{}"'.format(self.default_vals_list[0]))
            selected_value_reg = re.compile('option\svalue=\"{}\"'.format(self.default_vals_list[1]))
            return re.sub(selected_value_reg, 'option value="{}" selected'.format(self.default_vals_list[1]), label_html)