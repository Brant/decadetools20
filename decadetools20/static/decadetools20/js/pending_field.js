document.addEventListener('DOMContentLoaded', function () {
    const targets = {};
    document.querySelectorAll('[data-poll-target]').forEach(el => {
        targets[el.dataset.pollTarget] = el;
    });

    if (Object.keys(targets).length === 0) return;

    const match = window.location.pathname.match(/\/(\d+)\/change\/$/);
    const objId = match ? match[1] : null;

    // ✅ Exit early if we're creating a new object (no object ID)
    if (!objId) {
        console.info('No object ID found — skipping polling for new object.');
        return;
    }

    const baseUrl = window.location.pathname.split('/').slice(0, -3).join('/');
    const pollUrl = `${baseUrl}/poll-field/${objId}/`;

    const resolvedFields = new Set();
    let tries = 0;
    const maxTries = 10;

    const interval = setInterval(() => {
        tries += 1;

        fetch(pollUrl, {
            credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(res => res.json())
            .then(data => {
                let allResolved = true;

                for (const field in data) {
                    const info = data[field];
                    if (resolvedFields.has(field)) continue;

                    if (info.ready) {
                        const el = targets[field];
                        if (el) el.innerHTML = info.html;
                        resolvedFields.add(field);
                    } else {
                        allResolved = false;
                    }
                }

                if (allResolved || tries >= maxTries) {
                    clearInterval(interval);

                    if (!allResolved) {
                        console.warn(`Polling stopped after ${maxTries} attempts.`);

                        for (const field in targets) {
                            if (!resolvedFields.has(field)) {
                                const el = targets[field];
                                if (el) {
                                    el.innerHTML = `<div class="poll-failed">⚠️ Unable to load data…</div>`;
                                }
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Polling error:', error);
                clearInterval(interval);
            });
    }, 4000);
});
