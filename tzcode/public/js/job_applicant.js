frappe.ui.form.on("Job Applicant", {
    refresh(frm) {
        frm.trigger("add_preview_to_attachments");
    },
    
    add_preview_to_attachments(frm) {
        const eyeIcon = `
                <a href="#" style="margin-right: 4px;">
                    <svg class="icon icon-md preview-icon" aria-hidden="true" style="margin:0">
                        <use xlink:href="#icon-view"></use> 
                    </svg>
                </a>
        `;
    
        $('.attachment-row').each(function() {
            const $ellipsis = $(this).find('.data-pill '); // Target the first ellipsis within each row
        
            // Prepend the eyeIcon to the first ellipsis
            $ellipsis.prepend(eyeIcon);
        
            // Optional: Add a click event handler to the icon
            $ellipsis.find('.preview-icon').on('click', function(e) {
                e.preventDefault(); // Prevent event bubbling
                // Handle the preview action here
                // Let's find the element with the property target="_blank"
                const $anchor = $(this).closest('.attachment-row').find('a[target="_blank"]');
                // Let's print the href value
                const url = $anchor.attr('href');
                show_preview(frm, url);
            });
        });
    },
});

function get_file_extension(url) {
    const filename = url.split('/').pop(); // Get the filename from the URL
    const extension = filename.split('.').pop(); // Extract the extension
    return extension;
}

function show_preview(frm, url) {
    
    let $preview = "";
    let file_extension = get_file_extension(url);

    if (frappe.utils.is_image_file(url)) {
        $preview = $(`<div class="img_preview">
            <img
                class="img-responsive"
                src="${frappe.utils.escape_html(url)}"
                onerror="${frm.toggle_display("preview", false)}"
            />
        </div>`);
    } else if (frappe.utils.is_video_file(url)) {
        $preview = $(`<div class="img_preview">
            <video width="480" height="320" controls>
                <source src="${frappe.utils.escape_html(url)}">
                ${__("Your browser does not support the video element.")}
            </video>
        </div>`);
    } else if (file_extension === "pdf") {
        $preview = $(`<div class="img_preview">
            <object style="background:#323639;" width="100%">
                <embed
                    style="background:#323639;"
                    width="100%"
                    height="1190"
                    src="${frappe.utils.escape_html(url)}" type="application/pdf"
                >
            </object>
        </div>`);
    } else if (file_extension === "mp3") {
        $preview = $(`<div class="img_preview">
            <audio width="480" height="60" controls>
                <source src="${frappe.utils.escape_html(url)}" type="audio/mpeg">
                ${__("Your browser does not support the audio element.")}
            </audio >
        </div>`);
    }

    console.log($preview);
    if ($preview) {
        // First let's hide the sidebar and append a our preview to the main section
        frm.sidebar.sidebar.hide()
        // Let's replace .layout-side-section from col-lg-2 to col-lg-5 to make the preview bigger
        $('.layout-side-section').removeClass('col-lg-2').addClass('col-lg-5')
        // Now let's prepend the preview to the sidebar's parent
        frm.sidebar.sidebar.parent().prepend('<div id="preview-container" class="animate__fadeInLeft animate__slow"></div>');
        // Let's add a close button to the preview
        $('#preview-container').prepend(`
            <a id="close-preview" href="#" style="float: right;">
                <svg class="icon  icon-md" style="" aria-hidden="true">
                    <use class="" href="#icon-solid-error"></use>
                </svg>
                Close
            </a>
        `);
        // Let's add a click event to the close button
        $('#close-preview').click(function(){
            // Let's remove the preview
            $('#preview-container').remove();
            // Let's show the sidebar
            frm.sidebar.sidebar.show()
            // Let's replace .layout-side-section from col-lg-5 to col-lg-2 to make the sidebar smaller
            $('.layout-side-section').removeClass('col-lg-5').addClass('col-lg-2')
        });
        // Now let's append the preview to the container
        $('#preview-container').append($preview);
    }
}
