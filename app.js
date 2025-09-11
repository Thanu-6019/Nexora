const eventsContainer = document.getElementById('eventsContainer');
const eventSearch = document.getElementById('eventSearch');
const suggestionsList = document.getElementById('suggestions');
const scrollTopBtn = document.getElementById('scrollTopBtn');
const eventModal = document.getElementById('eventModal');
const modalTitle = document.getElementById('modalTitle');
const modalDesc = document.getElementById('modalDesc');
const closeModal = document.getElementById('closeModal');
const viewAllBtn = document.getElementById('viewAllBtn');

// Render events
function renderEvents(filter = '') {
    eventsContainer.innerHTML = '';
    const filtered = eventsData.filter(event => event.title.toLowerCase().includes(filter.toLowerCase()));
    filtered.forEach(event => {
        const div = document.createElement('div');
        div.classList.add('event-item');
        div.innerHTML = `
            <div class="flex items-center space-x-4">
                <div class="event-avatar ${event.status === 'Live' ? 'bg-primary' : 'bg-secondary'}">${event.title[0]}</div>
                <div>
                    <h4 class="font-semibold">${event.title}</h4>
                    <p class="text-gray-600 text-sm">${event.date} • ${event.participants} participants</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <span class="status-badge ${event.status === 'Live' ? 'status-live' : 'status-upcoming'}">${event.status}</span>
            </div>
        `;
        div.addEventListener('click', () => openModal(event));
        eventsContainer.appendChild(div);
    });
}

// Search with suggestions
eventSearch.addEventListener('input', (e) => {
    const value = e.target.value;
    renderEvents(value);

    if (value.trim() === '') {
        suggestionsList.classList.add('hidden');
        suggestionsList.innerHTML = '';
        return;
    }

    const filtered = eventsData.filter(ev => ev.title.toLowerCase().includes(value.toLowerCase()));
    suggestionsList.innerHTML = filtered.map(ev => `<li>${ev.title}</li>`).join('');
    suggestionsList.classList.remove('hidden');

    document.querySelectorAll('#suggestions li').forEach(li => {
        li.addEventListener('click', () => {
            eventSearch.value = li.innerText;
            renderEvents(li.innerText);
            suggestionsList.classList.add('hidden');
        });
    });
});

// Modal
function openModal(event) {
    modalTitle.innerText = event.title;
    modalDesc.innerText = event.description;
    eventModal.classList.add('active');
}

closeModal.addEventListener('click', () => eventModal.classList.remove('active'));

// Scroll to top
window.addEventListener('scroll', () => {
    scrollTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
});

scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// View All Events button
viewAllBtn.addEventListener('click', () => renderEvents(''));

// Initial render
renderEvents();

