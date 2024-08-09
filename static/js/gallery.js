
document.addEventListener("DOMContentLoaded", function() {
    const images = document.getElementsByClassName('zoomable-image');
    for (const img of images) {
        img.addEventListener("click", function() {
            if (!document.fullscreenElement) {
                if (img.requestFullscreen) {
                img.requestFullscreen();
                } else if (img.mozRequestFullScreen) { /* Firefox */
                img.mozRequestFullScreen();
                } else if (img.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
                img.webkitRequestFullscreen();
                } else if (img.msRequestFullscreen) { /* IE/Edge */
                img.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.mozCancelFullScreen) { /* Firefox */
                    document.mozCancelFullScreen();
                } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) { /* IE/Edge */
                    document.msExitFullscreen();
                }
            }
        });
    }
});

function changeImage(imageSrc) {
    const mainImage = document.getElementById("mainImage");
    // Start the fade-out
    mainImage.style.opacity = 0;
    
    // Wait for the fade-out to finish
    setTimeout(() => {
      // Change the image source
      mainImage.src = imageSrc;
      // Start the fade-in
      mainImage.style.opacity = 1;
    }, 500); // This timeout duration should match the CSS opacity transition duration
}

var thumbs = document.getElementsByClassName("thumb")
for (const thumb of thumbs) {
    thumb.addEventListener("click", function() {
        console.log("Thumb clicked", this.src)
        changeImage(this.src);
    });
}
