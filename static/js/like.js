function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


async function changeLike(event) {
    const pk = event.target.dataset.pk
    const process = event.target.dataset.isLiked == 'false' ? 'like' : 'unlike'
    const url = `/tweets/${pk}/${process}/`
    const data = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    }
    const response = await fetch(url, data)
    const jsonResponse = await response.json()

    if (process == 'like') {
        event.target.dataset.isLiked = 'true'
        event.target.innerHTML = '❤︎'
    } else {
        event.target.dataset.isLiked = 'false'
        event.target.innerHTML = '♡'
    }
    document.getElementById(pk).innerHTML = jsonResponse.liked_by_count
}
