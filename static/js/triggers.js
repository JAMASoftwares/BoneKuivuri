client_gallery = 'Triggers'
gallerySocket = null


function updateTriggersGallery() {
    $.getJSON('/list_trigger_images', function(data) {
        const gallery = document.getElementById('gallery-trg');
        gallery.innerHTML = ''; // Clear existing images
        data.images.forEach(image => {
            const aElement = document.createElement('a');
            const imgElement = document.createElement('img');
            aElement.href = '/captures/triggers/' + image; // Point to the full-size image
            aElement.dataset.lightbox = "image-gallery"; // Use Lightbox2
            imgElement.src = '/triggers_thumbnails/' + image; // Thumbnail image
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

window.onload = updateTriggersGallery; // Update the gallery when the page loads
