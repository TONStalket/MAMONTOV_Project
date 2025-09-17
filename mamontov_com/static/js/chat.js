const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
let fetchInterval = null;

function renderMessages(messages) {
    chatMessages.innerHTML = '';
    const fragment = document.createDocumentFragment();

    messages.forEach((message) => {
        const wrapper = document.createElement('article');
        wrapper.className = 'message';

        const author = document.createElement('span');
        author.className = 'message-author';
        author.textContent = message.author;

        const body = document.createElement('p');
        body.textContent = message.content;

        const time = document.createElement('span');
        time.className = 'message-time';
        const date = new Date(message.created_at);
        time.textContent = date.toLocaleString();

        wrapper.appendChild(author);
        wrapper.appendChild(body);
        wrapper.appendChild(time);
        fragment.appendChild(wrapper);
    });

    chatMessages.appendChild(fragment);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function loadMessages() {
    try {
        const response = await fetch('/api/messages');
        if (!response.ok) {
            throw new Error('Не удалось загрузить сообщения');
        }
        const messages = await response.json();
        renderMessages(messages);
    } catch (error) {
        console.error(error);
        showInlineNotification('Ошибка получения сообщений. Попробуйте позже.', 'warning');
    }
}

async function sendMessage(content) {
    const response = await fetch('/api/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
    });

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const errorMessage = data.error || 'Не удалось отправить сообщение.';
        throw new Error(errorMessage);
    }

    return response.json();
}

function showInlineNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `flash flash-${type}`;
    container.textContent = message;
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 4000);
}

chatForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const content = messageInput.value.trim();
    if (!content) {
        showInlineNotification('Введите текст сообщения.', 'warning');
        return;
    }

    chatForm.classList.add('is-loading');

    try {
        await sendMessage(content);
        messageInput.value = '';
        await loadMessages();
    } catch (error) {
        console.error(error);
        showInlineNotification(error.message, 'danger');
    } finally {
        chatForm.classList.remove('is-loading');
    }
});

function init() {
    loadMessages();
    fetchInterval = setInterval(loadMessages, 4000);
}

if (chatForm && messageInput && chatMessages) {
    init();
}
