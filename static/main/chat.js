function renderMessages(data) {
    document.querySelector('ul#message-list').innerHTML = ''
    for (const message of data) {
        document.querySelector('ul#message-list').innerHTML += `<li>${message.message} ${message.author_id}</li>`
    }
}

function wsRenderMessages(data) {
    console.log(data)
    data = JSON.parse(data.data)
    console.log(data)
    for (let message of data) {
        message = JSON.parse(message)
        document.querySelector('ul#message-list').innerHTML += `<li>${message.message} ${message.author_id}</li>`
    }
}


function renderMessage(message) {
    document.querySelector('ul#message-list').innerHTML += `<li>${message.message} ${message.author_id}</li>`
}

function getMessages(chat_id) {
    const access_token = localStorage.getItem('access_token')
    $.ajax({
        method: 'get',
        url: `/api/chat/${chat_id}`,
        dataType: 'json',
        contentType: 'application/json',
        headers: {'Authorization': `Bearer ${access_token}`},
        error: function (data) {
            window.location.href = '/register'
        },
        success: renderMessages,
    })
}

function pollMessages(chat_id) {
    setInterval(getMessages, 1000, chat_id)
}

function wsMessages(chat_id) {
    const access_token = localStorage.getItem('access_token')
    let ws = new WebSocket(`ws://0.0.0.0:8000/api/ws/chat/${chat_id}/${access_token}`)
    ws.onmessage = wsRenderMessages
}

$("form#chat-connect-form").on('submit', function (e) {
    e.preventDefault()
    localStorage.setItem('chat_id', this.chat_id.value)
    const access_token = localStorage.getItem('access_token')
    if (access_token == null) {
        window.location.href = '/register'
    } else {
        wsMessages(this.chat_id.value)
    }
})

$("form#chat-send").on("submit", function (e) {
    e.preventDefault()
    const access_token = localStorage.getItem('access_token')
    if (access_token == null) {
        window.location.href = '/register'
    } else {
        const chat_id = localStorage.getItem('chat_id')
        const message = this.message.value
        document.querySelector('input#message').value = ''
        $.ajax({
            method: 'post',
            url: `/api/chat/${chat_id}`,
            dataType: 'json',
            contentType: 'application/json',
            headers: {'Authorization': `Bearer ${access_token}`},
            data: JSON.stringify({message: message}),
            success: renderMessage
        })
    }
})