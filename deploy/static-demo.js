(() => {
    const badge = document.createElement('div');
    badge.className = 'static-demo-badge';
    badge.textContent = 'Design preview';
    document.body.appendChild(badge);

    const notice = document.createElement('div');
    notice.className = 'static-demo-notice';
    notice.setAttribute('role', 'status');
    notice.textContent = 'This GitHub Pages build is a visual preview. Accounts, submissions, password reset, and live scores are available only on the full Django deployment.';
    document.body.appendChild(notice);

    let timeout;
    const showNotice = () => {
        window.clearTimeout(timeout);
        notice.classList.add('is-visible');
        timeout = window.setTimeout(() => notice.classList.remove('is-visible'), 5200);
    };

    document.addEventListener('submit', event => {
        event.preventDefault();
        showNotice();
    });

    document.querySelectorAll('a[data-static-only="true"]').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            showNotice();
        });
    });
})();

