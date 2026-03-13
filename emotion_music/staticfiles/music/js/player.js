/**
 * MoodTunes – Custom Music Player & UI Logic
 * Handles: audio playback, next/prev, progress bar,
 *          volume, favorites AJAX, playlist modal, mobile sidebar
 */

/* ═══════════════════════════════════════════════════════════
   STATE
═══════════════════════════════════════════════════════════ */
let songList = [];         // Array of song card elements on page
let currentIndex = -1;     // Index of currently playing song
let isSeeking = false;

const audio = document.getElementById('audioPlayer');

/* ═══════════════════════════════════════════════════════════
   INIT – collect songs from page
═══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
    // Gather all song cards on current page
    songList = Array.from(document.querySelectorAll('.song-card'));

    // Set initial volume
    const volRange = document.getElementById('volumeRange');
    if (audio && volRange) {
        audio.volume = parseInt(volRange.value) / 100;
    }

    // Bind sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');

    const toggleSidebar = () => sidebar && sidebar.classList.toggle('open');
    if (sidebarToggle) sidebarToggle.addEventListener('click', toggleSidebar);
    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 900 && sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && e.target !== mobileMenuBtn) {
                sidebar.classList.remove('open');
            }
        }
    });

    // Bind audio events
    if (audio) {
        audio.addEventListener('timeupdate', updateProgress);
        audio.addEventListener('loadedmetadata', updateDuration);
        audio.addEventListener('ended', playNext);
        audio.addEventListener('error', () => {
            console.warn('Audio error on:', audio.src);
        });
    }

    // Progress range scrub
    const progressRange = document.getElementById('progressRange');
    if (progressRange) {
        progressRange.addEventListener('mousedown', () => { isSeeking = true; });
        progressRange.addEventListener('input', (e) => {
            const pct = parseFloat(e.target.value);
            if (audio.duration) {
                audio.currentTime = (pct / 100) * audio.duration;
            }
            updateProgressUI(pct);
        });
        progressRange.addEventListener('mouseup', () => { isSeeking = false; });
        progressRange.addEventListener('touchend', () => { isSeeking = false; });
    }

    // Volume range
    const volumeRange = document.getElementById('volumeRange');
    if (volumeRange) {
        volumeRange.addEventListener('input', (e) => {
            audio.volume = parseInt(e.target.value) / 100;
            updateVolumeIcon(audio.volume);
        });
    }

    // Play/Pause button
    const playPauseBtn = document.getElementById('playPauseBtn');
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => {
            if (audio.paused) {
                audio.play().catch(console.error);
            } else {
                audio.pause();
            }
            syncPlayPauseIcon();
        });
    }

    // Prev / Next
    document.getElementById('prevBtn')?.addEventListener('click', playPrev);
    document.getElementById('nextBtn')?.addEventListener('click', playNext);

    // Mute toggle
    document.getElementById('muteBtn')?.addEventListener('click', () => {
        audio.muted = !audio.muted;
        updateVolumeIcon(audio.muted ? 0 : audio.volume);
    });

    // Modal close
    document.getElementById('modalClose')?.addEventListener('click', closePlaylistModal);
    document.getElementById('playlistModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'playlistModal') closePlaylistModal();
    });

    // Auto-update play/pause icon when audio state changes externally
    audio?.addEventListener('play', syncPlayPauseIcon);
    audio?.addEventListener('pause', syncPlayPauseIcon);

    // Mark player-fav-btn state
    markPlayerFavBtn();
});

/* ═══════════════════════════════════════════════════════════
   PLAYBACK
═══════════════════════════════════════════════════════════ */
/**
 * Play a song from a card element.
 * @param {HTMLElement} card
 */
function playSongFromCard(card) {
    if (!card) return;
    const songId = parseInt(card.dataset.songId);
    const audioSrc = card.dataset.audio;
    const title = card.dataset.title || 'Unknown Title';
    const artist = card.dataset.artist || 'Unknown Artist';
    const cover = card.dataset.cover || '';

    // Update current index
    currentIndex = songList.indexOf(card);

    // Remove playing class from all cards
    document.querySelectorAll('.song-card.is-playing').forEach(c => c.classList.remove('is-playing'));
    card.classList.add('is-playing');

    // Update audio source
    if (audio.src !== audioSrc) {
        audio.src = audioSrc || '';
    }

    // Update player UI
    updatePlayerInfo(title, artist, cover, songId);

    // Play
    if (audioSrc) {
        audio.play().catch(err => {
            console.error('Playback failed:', err);
        });
    }

    // Mark played (AJAX)
    if (songId) {
        markPlayed(songId);
    }
}

/** Called by "Play All" buttons */
function playAllSongs() {
    if (songList.length > 0) {
        playSongFromCard(songList[0]);
    }
}

function playNext() {
    if (songList.length === 0) return;
    const nextIdx = (currentIndex + 1) % songList.length;
    playSongFromCard(songList[nextIdx]);
}

function playPrev() {
    if (songList.length === 0) return;
    // If >3s in, restart current; otherwise go to prev
    if (audio.currentTime > 3) {
        audio.currentTime = 0;
        return;
    }
    const prevIdx = (currentIndex - 1 + songList.length) % songList.length;
    playSongFromCard(songList[prevIdx]);
}

/* ═══════════════════════════════════════════════════════════
   PLAYER UI UPDATES
═══════════════════════════════════════════════════════════ */
function updatePlayerInfo(title, artist, cover, songId) {
    document.getElementById('playerTitle').textContent = title;
    document.getElementById('playerArtist').textContent = artist;

    const img = document.getElementById('playerCoverImg');
    const placeholder = document.getElementById('playerCoverPlaceholder');

    if (cover) {
        img.src = cover;
        img.style.display = 'block';
        if (placeholder) placeholder.style.display = 'none';
    } else {
        img.style.display = 'none';
        if (placeholder) placeholder.style.display = 'flex';
    }

    // Update fav button state
    const favBtn = document.getElementById('playerFavBtn');
    if (favBtn) {
        favBtn.dataset.songId = songId;
        const isFav = (window.FAVORITE_IDS || []).includes(songId);
        updateFavBtnState(favBtn, isFav, true);
    }
}

function updateProgress() {
    if (isSeeking || !audio.duration) return;
    const pct = (audio.currentTime / audio.duration) * 100;
    updateProgressUI(pct);
    document.getElementById('currentTime').textContent = formatTime(audio.currentTime);
}

function updateDuration() {
    document.getElementById('totalTime').textContent = formatTime(audio.duration || 0);
}

function updateProgressUI(pct) {
    const fill = document.getElementById('progressFill');
    const range = document.getElementById('progressRange');
    if (fill) fill.style.width = pct + '%';
    if (range) range.value = pct;
}

function syncPlayPauseIcon() {
    const icon = document.getElementById('playIcon');
    if (!icon) return;
    if (audio.paused) {
        icon.classList.replace('fa-pause', 'fa-play');
    } else {
        icon.classList.replace('fa-play', 'fa-pause');
    }
}

function updateVolumeIcon(vol) {
    const icon = document.getElementById('volIcon');
    if (!icon) return;
    icon.className = 'fas ' + (vol === 0 ? 'fa-volume-xmark' : vol < 0.5 ? 'fa-volume-low' : 'fa-volume-high');
}

function formatTime(secs) {
    if (!isFinite(secs)) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}

/* ═══════════════════════════════════════════════════════════
   FAVORITES (AJAX)
═══════════════════════════════════════════════════════════ */
function toggleFavorite(btn, songId) {
    // Stop click propagating to play card
    event && event.stopPropagation();

    const csrfToken = getCookie('csrftoken');
    fetch(`/favorite/toggle/${songId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
    })
        .then(r => r.json())
        .then(data => {
            const isFav = data.is_favorite;
            updateFavBtnState(btn, isFav, false);

            // Sync player fav button if same song
            const playerFavBtn = document.getElementById('playerFavBtn');
            if (playerFavBtn && parseInt(playerFavBtn.dataset.songId) === songId) {
                updateFavBtnState(playerFavBtn, isFav, true);
            }

            // Update FAVORITE_IDS list
            if (!window.FAVORITE_IDS) window.FAVORITE_IDS = [];
            if (isFav) {
                if (!window.FAVORITE_IDS.includes(songId)) window.FAVORITE_IDS.push(songId);
            } else {
                window.FAVORITE_IDS = window.FAVORITE_IDS.filter(id => id !== songId);
            }

            showToast(isFav ? '❤️ Added to Favorites' : '💔 Removed from Favorites');
        })
        .catch(err => console.error('Favorite toggle failed:', err));
}

function updateFavBtnState(btn, isFav, isPlayerBtn) {
    if (!btn) return;
    const icon = btn.querySelector('i');
    if (icon) {
        icon.className = (isFav ? 'fas' : 'far') + ' fa-heart';
    }
    btn.classList.toggle('favorited', isFav);
}

function markPlayerFavBtn() {
    const favBtn = document.getElementById('playerFavBtn');
    if (!favBtn) return;
    favBtn.addEventListener('click', () => {
        const songId = parseInt(favBtn.dataset.songId);
        if (!songId) return;
        // Find matching card btn
        const cardFavBtn = document.querySelector(`.song-card[data-song-id="${songId}"] .fav-btn`);
        toggleFavorite(cardFavBtn || favBtn, songId);
    });
}

/* ═══════════════════════════════════════════════════════════
   MARK PLAYED (AJAX)
═══════════════════════════════════════════════════════════ */
function markPlayed(songId) {
    const csrfToken = getCookie('csrftoken');
    fetch(`/mark-played/${songId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
    }).catch(err => console.warn('Mark played failed:', err));
}

/* ═══════════════════════════════════════════════════════════
   PLAYLIST MODAL
═══════════════════════════════════════════════════════════ */
let _pendingSongId = null;

function openPlaylistModal(songId) {
    event && event.stopPropagation();
    _pendingSongId = songId;

    const playlists = window.PLAYLISTS || [];
    const optionsEl = document.getElementById('playlistOptions');
    if (!optionsEl) return;

    if (playlists.length === 0) {
        optionsEl.innerHTML = '<p style="color:var(--text-muted);font-size:.85rem">No playlists yet. Create one first!</p>';
    } else {
        optionsEl.innerHTML = playlists.map(pl =>
            `<button class="playlist-option-btn" onclick="addToPlaylist(${pl.id}, '${escapeHtml(pl.name)}')">
                <i class="fas fa-list-music" style="margin-right:.5rem;color:#34d399"></i>${escapeHtml(pl.name)}
            </button>`
        ).join('');
    }

    document.getElementById('playlistModal').classList.add('open');
}

function closePlaylistModal() {
    document.getElementById('playlistModal')?.classList.remove('open');
    _pendingSongId = null;
}

function addToPlaylist(playlistId, playlistName) {
    if (!_pendingSongId) return;
    const csrfToken = getCookie('csrftoken');
    const formData = new FormData();
    formData.append('song_id', _pendingSongId);
    formData.append('playlist_id', playlistId);

    fetch('/playlists/add/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData,
    })
        .then(r => r.json())
        .then(data => {
            closePlaylistModal();
            showToast(data.success ? `✅ Added to "${playlistName}"` : `⚠️ ${data.message}`);
        })
        .catch(err => { console.error('Playlist add failed:', err); closePlaylistModal(); });
}

/* ═══════════════════════════════════════════════════════════
   UTILITIES
═══════════════════════════════════════════════════════════ */
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        const [k, v] = c.trim().split('=');
        if (k === name) return decodeURIComponent(v);
    }
    return '';
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3200);
}
