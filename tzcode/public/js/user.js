frappe.ui.form.on("User", {
    first_name(frm) {
        frm.set_value("first_name", capitalize(frm.doc.first_name));
        frm.trigger("make_username");
    },
    last_name(frm) {
        frm.set_value("last_name", capitalize(frm.doc.last_name));
        frm.trigger("make_username");
    },
    make_username(frm) {
        let new_name = '';
        if (frm.doc.first_name) {
            new_name = frm.doc.first_name;
        }
        if (frm.doc.last_name) {
            if (!!new_name)
                new_name = new_name.concat("_");

            new_name = new_name.concat(frm.doc.last_name);
        }
        frm.set_value("username", new_name);
    }
})

function capitalize(str) {
    if (typeof (str) != "string")
        throw 'Function must receive a string';

    let cleaned_str = str.trim().toLowerCase();
    if (!cleaned_str)
        return ""

    return cleaned_str[0].toUpperCase().concat(cleaned_str.slice(1))
}
