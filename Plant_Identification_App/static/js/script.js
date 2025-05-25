new Vue({
    el: '#app',
    data: {
        previewImage: null,
        plantInfo: null,
        videoStream: null // for stopping the camera later if needed
    },
    methods: {
        previewFile(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            reader.onloadend = () => {
                this.previewImage = reader.result;
            };
            if (file) {
                reader.readAsDataURL(file);
            }
        },

        uploadImage() {
            const formData = new FormData();
            const fileInput = document.querySelector('input[type="file"]');
            const file = fileInput.files[0];

            if (!file) {
                alert('Please select an image first!');
                return;
            }

            formData.append('image', file);

            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                this.plantInfo = data;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        },

        startCamera() {
            const video = document.createElement('video');
            video.autoplay = true;
            video.style.width = '100%';
            video.style.maxHeight = '300px';
            document.querySelector('.plant-card').appendChild(video);

            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    video.srcObject = stream;
                    this.videoStream = stream;
                })
                .catch((err) => {
                    console.error("Error accessing camera: ", err);
                });
        }
    }
});