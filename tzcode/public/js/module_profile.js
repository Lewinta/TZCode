frappe.ui.form.on("Module Profile", {
    refresh (frm) {
        if (has_common(frappe.user_roles, ["Administrator", "System Manager", "External Vendor"])) {
			if (!frm.module_editor && frm.doc.__onload && frm.doc.__onload.all_modules) {
				let module_area = $('<div style="min-height: 300px">')
					.appendTo(frm.fields_dict.module_html.wrapper);

				frm.module_editor = new frappe.ModuleEditor(frm, module_area);
			}
		}

		if (frm.module_editor) {
			frm.module_editor.refresh();
		}
	
        $('input[data-module="Core"]').prop('disabled', true);
        $('input[data-module="Desk"]').prop('disabled', true);

        frm.trigger("add_custom_buttons");
    },
    validate (frm) {
        frm.trigger("get_modules");
    },
    add_custom_buttons (frm) {
        if(frm.is_new())
            return;
        frm.add_custom_button(__("Check All"), () => {
            $('.block-module-check').prop('checked', true);
        });
        frm.add_custom_button(__("Uncheck All"), () => {
            $('.block-module-check').prop('checked', false);
            $('input[data-module="Core"]').prop('checked', true);
            $('input[data-module="Desk"]').prop('checked', true);
        });
    },
    get_modules (frm) {
        frappe.run_serially([
            () => frm.clear_table("module_details"),
            () => add_selected_modules(frm),
            () => frm.refresh_field("module_details"),
        ]);
    }
})

function add_selected_modules(frm){
    $('.block-module-check:checked').each(function() {
        let module = $(this).attr('data-module');
        frm.add_child("module_details", {module});
    })
}