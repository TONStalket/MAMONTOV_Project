const postsList = document.getElementById('postsList');
const postForm = document.getElementById('postForm');
const postTitleInput = document.getElementById('postTitle');
const postContentInput = document.getElementById('postContent');

function showInlineNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `flash flash-${type}`;
    container.textContent = message;
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 4000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) {
        return '';
    }

    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function renderPosts(posts) {
    if (!postsList) {
        return;
    }

    postsList.innerHTML = '';
    const fragment = document.createDocumentFragment();

    if (!posts.length) {
        const empty = document.createElement('p');
        empty.className = 'empty-state';
        empty.textContent = 'Пока нет публикаций. Станьте первым, кто расскажет о чём-то важном.';
        fragment.appendChild(empty);
    } else {
        posts.forEach((post) => {
            const article = document.createElement('article');
            article.className = 'post';
            article.dataset.postId = post.id;

            const header = document.createElement('header');
            header.className = 'post-header';

            const title = document.createElement('h2');
            title.className = 'post-title';
            title.textContent = post.title;

            const meta = document.createElement('div');
            meta.className = 'post-meta';

            const author = document.createElement('span');
            author.className = 'post-author';
            author.textContent = post.author;

            const time = document.createElement('time');
            time.className = 'post-time';
            time.dateTime = post.created_at;
            time.textContent = formatDate(post.created_at);

            meta.appendChild(author);
            meta.appendChild(time);

            header.appendChild(title);
            header.appendChild(meta);

            const content = document.createElement('p');
            content.className = 'post-content';
            content.textContent = post.content;

            article.appendChild(header);
            article.appendChild(content);
            fragment.appendChild(article);
        });
    }

    postsList.appendChild(fragment);
}

async function fetchPosts() {
    const response = await fetch('/api/posts');
    if (!response.ok) {
        throw new Error('Не удалось получить публикации.');
    }

    return response.json();
}

async function createPost(title, content) {
    const response = await fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, content }),
    });

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const message = data.error || 'Не удалось опубликовать сообщение.';
        throw new Error(message);
    }

    return response.json();
}

async function loadPostsWithHandling() {
    try {
        const posts = await fetchPosts();
        renderPosts(posts);
    } catch (error) {
        console.error(error);
        showInlineNotification(error.message, 'warning');
    }
}

function setFormLoading(isLoading) {
    if (!postForm) {
        return;
    }

    postForm.classList.toggle('is-loading', isLoading);
    const controls = postForm.querySelectorAll('input, textarea, button');
    controls.forEach((control) => {
        control.disabled = isLoading;
    });
}

postForm?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const title = postTitleInput.value.trim();
    const content = postContentInput.value.trim();

    if (!title || !content) {
        showInlineNotification('Заполните заголовок и текст публикации.', 'warning');
        return;
    }

    setFormLoading(true);

    try {
        await createPost(title, content);
        postTitleInput.value = '';
        postContentInput.value = '';
        await loadPostsWithHandling();
        showInlineNotification('Публикация добавлена!', 'success');
    } catch (error) {
        console.error(error);
        showInlineNotification(error.message, 'danger');
    } finally {
        setFormLoading(false);
    }
});

function initCommunityPage() {
    loadPostsWithHandling();
    setInterval(loadPostsWithHandling, 10000);
}

if (postsList) {
    initCommunityPage();
}
