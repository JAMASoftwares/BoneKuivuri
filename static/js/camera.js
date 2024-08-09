client_video = 'Camera [IP]'
videoSocket = null


$(document).ready(function(){
    $('#capture_button').click(function(){
        // Change the cursor to a spinner (wait cursor)
        $('body').css('cursor', 'wait');
        $('.button').css('cursor', 'wait');

        $.ajax({
            url: '/capture-image',
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                var timestamp = new Date().getTime();
                $('#org-img').attr('src', data.org_path + '?t=' + timestamp);
            },
            error: function(xhr, status, error) {
                console.error("Error capturing images: " + error);
            },
            complete: function() {
                // Reset the cursor back to default
                $('body').css('cursor', 'default');
                $('.button').css('cursor', 'pointer');
            }
        });
    });
    $('#save_button').click(function(){
        // Change the cursor to a spinner (wait cursor)
        $('body').css('cursor', 'wait');
        $('.button').css('cursor', 'wait');

        $.ajax({
            url: '/save-image',
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                var timestamp = new Date().getTime();
                $('#org-img').attr('src', data.org_path + '?t=' + timestamp);
                updateGallery(); // Refresh the gallery after saving
            },
            error: function(xhr, status, error) {
                console.error("Error while saving image: " + error);
            },
            complete: function() {
                // Reset the cursor back to default
                $('body').css('cursor', 'default');
                $('.button').css('cursor', 'pointer');
            }
        });
    });
});


function updateGallery() {
    $.getJSON('/list_images', function(data) {
        const gallery = document.getElementById('gallery');
        gallery.innerHTML = ''; // Clear existing images
        data.images.forEach(image => {
            const aElement = document.createElement('a');
            const imgElement = document.createElement('img');
            aElement.href = '/captures/' + image; // Point to the full-size image
            aElement.dataset.lightbox = "image-gallery"; // Use Lightbox2
            imgElement.src = '/thumbnails/' + image; // Thumbnail image
            //imgElement.classList.add('thumb'); // Optional: For additional styling
            aElement.appendChild(imgElement);
            gallery.appendChild(aElement);
        });
    });
}

lightbox.option({
    'resizeDuration': 200,
    'wrapAround': true,
    // Add more options as needed
})

window.onload = updateGallery; // Update the gallery when the page loads
