async function loadGuide() {
    try {
        const [m3uRes, xmlRes] = await Promise.all([
            fetch('./channels.m3u'),
            fetch('./epg.xml')
        ]);

        const m3uText = await m3uRes.text();
        const xmlDoc = new DOMParser().parseFromString(await xmlRes.text(), "text/xml");
        const container = document.getElementById('epg-container');
        container.innerHTML = '';

        const channels = parseM3U(m3uText);
        const programmes = Array.from(xmlDoc.getElementsByTagName('programme'));

        channels.forEach(ch => {
            const chProgs = programmes.filter(p => p.getAttribute('channel') === ch.id);
            if (chProgs.length > 0) {
                const row = document.createElement('div');
                row.className = 'channel-row';
                row.innerHTML = `
                    <div class="channel-meta">
                        <img src="${ch.logo}" onerror="this.src='https://via.placeholder.com/40'">
                        ${ch.name}
                    </div>
                    <div class="program-scroll">
                        ${chProgs.map(p => `
                            <div class="program-card">
                                <div class="time">${formatTime(p.getAttribute('start'))}</div>
                                <div class="title">${p.getElementsByTagName('title')[0].textContent}</div>
                            </div>
                        `).join('')}
                    </div>`;
                container.appendChild(row);
            }
        });
    } catch (e) { console.error("Grabber Error:", e); }
}

function parseM3U(text) {
    return text.split('#EXTINF').slice(1).map(line => ({
        id: line.match(/tvg-id="([^"]+)"/)?.[1],
        logo: line.match(/tvg-logo="([^"]+)"/)?.[1],
        name: line.split(',')[1].split('\n')[0].trim()
    })).filter(c => c.id);
}

function formatTime(t) { return `${t.substring(8,10)}:${t.substring(10,12)}`; }
function filterChannels() {
    let q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('.channel-row').forEach(r => {
        r.style.display = r.innerText.toLowerCase().includes(q) ? 'flex' : 'none';
    });
}
loadGuide();
