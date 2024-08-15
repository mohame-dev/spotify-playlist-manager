document.addEventListener('DOMContentLoaded', function () {
    const exportLink = document.querySelector('.export');
    const playlistContainer = document.querySelector('.container-export');
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');

    const fileName = document.getElementById('file-name');
    const numberSongs = document.getElementById('number-songs');
    const displayName = document.getElementById('welcome');

    fetch('/username')
        .then(response => response.json())
        .then(data => {
            const username = data.username || 'Guest';
            displayName.textContent = `Welcome ${username}!`;
        })
        .catch(error => {
            console.error('Error fetching username:', error);
            displayName.textContent = 'Welcome Guest!';
        });

    exportLink.addEventListener('click', function (event) {
        event.preventDefault();
        playlistContainer.classList.toggle('show');
        if (playlistContainer.classList.contains('show')) {
            loadPlaylists();
        }
    });

    playlistContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('playlist-button')) {
            const playlistId = event.target.getAttribute('data-playlist-id');
            downloadPlaylistTracks(playlistId);
        }
    });

    fileInput.addEventListener('change', function () {
        const file = fileInput.files[0];
        if (file) {
            fileName.textContent = `Selected file: ${file.name}`;

            const reader = new FileReader();

            reader.onload = function (event) {
                const text = event.target.result;
                const lines = text.trim().split('\n');
                const numberOfSongs = lines.length;
                numberSongs.textContent = `Number of songs found: ${numberOfSongs}`;
            };

            reader.readAsText(file);
        } else {
            fileName.textContent = '';
            numberSongs.textContent = '';
        }
    });

    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const file = fileInput.files[0];
        if (file) {
            document.body.style.cursor = 'wait';

            uploadPlaylistTracks(file);
        } else {
            alert('Please select a file to upload.');
        }
    });



    function loadPlaylists() {
        fetch('/playlists')
            .then(response => response.json())
            .then(playlists => {
                playlistContainer.innerHTML = '';
                if (playlists.length > 0) {
                    playlists.forEach(playlist => {
                        const playlistElement = document.createElement('div');
                        playlistElement.classList.add('playlist-item');
                        playlistElement.innerHTML = `
                            <img src="${playlist.image_url}" alt="${playlist.name}" class="playlist-image">
                            <button class="playlist-button" data-playlist-id="${playlist.playlist_uri.split(':')[2]}">${playlist.name}</button>
                        `;
                        playlistContainer.appendChild(playlistElement);
                    });
                } else {
                    playlistContainer.innerHTML = '<p>No playlists found.</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching playlists:', error);
                playlistContainer.innerHTML = '<p>Error loading playlists.</p>';
            });
    }

    function downloadPlaylistTracks(playlistId) {
        document.body.style.cursor = 'wait';

        fetch(`/export-playlist/${playlistId}`)
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    throw new Error('Failed to download tracks.');
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${playlistId}.txt`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error downloading playlist tracks:', error);
            })
            .finally(() => {
                document.body.style.cursor = 'default';
            });
    }


    function uploadPlaylistTracks(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/import-playlist', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Upload error:', data.error);
                    alert('Failed to upload tracks: ' + data.error);
                } else {
                    console.log('Upload success:', data.success);
                    alert('Tracks uploaded successfully!');
                }
            })
            .catch(error => {
                console.error('Error uploading playlist tracks:', error);
                alert('An error occurred during upload.');
            })
            .finally(() => {
                document.body.style.cursor = 'default';

                fileInput.value = '';
                fileName.textContent = '';
                numberSongs.textContent = '';
            });
    }
});
