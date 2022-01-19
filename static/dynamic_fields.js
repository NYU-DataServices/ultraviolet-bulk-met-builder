function short_id() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function find_metgrouping_num(grouping_id) {
    try {
        let rem_uuid = grouping_id.split("_").pop();
        let remove_field_groupings = document.querySelectorAll('[id^="removeclass_"]');
        for (var i = 0; i < remove_field_groupings.length; ++i) {
            if (remove_field_groupings[i].id.split("_")[1] == rem_uuid) {
                var m_grouping = parseInt(remove_field_groupings[i].id.split("_").pop());
            }
        }
        if (m_grouping == null) {
            var m_grouping = 1;
        }

        console.log(m_grouping)
        return m_grouping;
    } catch (err){
        return 1;
    }
}

function met_grouping_fields(grouping_id) {
    let metgrouping = find_metgrouping_num(grouping_id);
    metgrouping ++;
    let objTo = document.getElementById(grouping_id);
    let field_grouping = objTo.innerHTML;
    let divtest = document.createElement("div");
    let rdiv = 'removeclass_' + grouping_id.replace('met_grouping_fields_wrap_', '') + '_' + metgrouping;
	divtest.setAttribute("id", rdiv);
	divtest.innerHTML = field_grouping;
	let removeButton = document.getElementById('danger_button_' + grouping_id.replace('met_grouping_fields_wrap_', ''));
    removeButton.style.visibility = "visible";
    objTo.parentNode.appendChild(divtest);
    let new_grouping_inputs = document.getElementById(rdiv).querySelectorAll('input,select')
    for(var i = 0; i < new_grouping_inputs.length; ++i){
        let input_field = new_grouping_inputs[i];
        let original_name = input_field.name;
        let new_input_name = "addedInput" + metgrouping + "-" + original_name.split("_").slice(0, -2).join("_") + "_" + short_id().slice(0,5) + "_" + original_name.split("_").at(-1);
        input_field.setAttribute("name", new_input_name);
        input_field.removeAttribute("value");
        }
}

function remove_met_grouping_fields(rid) {
   let metgrouping = find_metgrouping_num(rid);
   $('#removeclass_'+ rid + '_' + metgrouping).remove();
   metgrouping--;
   if (metgrouping == 1) {
       document.getElementById('danger_button_' + rid).style.visibility = "hidden";
   }
}