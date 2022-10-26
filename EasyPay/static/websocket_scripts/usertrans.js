var wsStart = 'ws://';
var host = window.location.host;
var self_username = $('#self_username').html();
var other_one_username = $('#other_one_username').html();


window.onload = function () {
    callConvApi();
};

var chats_socket_url = wsStart + host + "/chats/" + self_username.replace(/\s/g, '') + "/" + other_one_username.replace(/\s/g, '');

const chatsSocket = new WebSocket(chats_socket_url)




//chatsSocket.close();

var input = document.getElementById("massage-btn");
input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        let temp = { 'message': input.value, 'payment': -1 };
        input.value = "";
        NotificationSend(temp);
    }
});

var payment_btn = document.getElementById('payment-btn');
payment_btn.addEventListener("click", function (e) {
    let message = document.getElementById('payment-message').value;
    let payment = document.getElementById('amount').value;
    if (payment === '') {
        payment = -1;
    }
    data = { 'message': message, 'payment': payment };
    
    NotificationSend(data);
});
// $('#close-payment-modal').click();
function NotificationSend(data) {
    chatsSocket.send(JSON.stringify({
        'message': data['message'],
        'payment': data['payment'],
        'username': other_one_username,
    }));
}

chatsSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    conversations_append(data);
};

function callConvApi() {
    // let csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    let path = window.location.origin + "/api/conversations/";
    $.ajax({
        type: 'GET',
        url: path,
        dataType: 'json',
        data: {
            'user1': self_username,
            'user2': other_one_username,
        },
        success: function (response) {
            conversations_append(response);
        },

        error: function (response) {
            console.log(response);
        }
    });
}

function conversations_append(response) {
    response.forEach(item => {
        if (item['transaction'] != "") {
            if (item['receiver'] === self_username) {
                $('#conversations-container').append(`
                <div data-aos="zoom-in-down" data-aos-duration="1500" id=""
                class="main-contend-payment text-center EasyP shadow-lg">
                <div class="mt-2">Payment to You</div>
                <div class="mt-3"><i class="fa-solid fa-indian-rupee-sign"></i>`+ item['transaction'] + `</div>
                <div class="mt-4"><i style="color: #3EC70B;" class="fa-solid fa-circle-check"></i> Paid: `+ item['date_time'] + `
                </div>
            </div><br>
                `);
            }
            else {
                $('#conversations-container').append(`
                <div data-aos="zoom-in-up" data-aos-duration="1500" id=""
                class="main-contend-payment-two text-center EasyP shadow-lg p-2">
                <div class="mt-2">Payment to `+ item['receiver'] + `</div>
                <div class="mt-3"><i class="fa-solid fa-indian-rupee-sign"></i>`+ item['transaction'] + `</div>
                <div class="mt-4"><i style="color: #3EC70B;" class="fa-solid fa-circle-check"></i> Paid: `+ item['date_time'] + `
                </div>
            </div>
               `);
            }
        }
        else {
            if (item['receiver'] === self_username) {
                $('#conversations-container').append(
                    `
                    <div data-aos="zoom-in-down" data-aos-duration="1500" id=""
            class="main-contend-one p-3 shadow-lg text-center d-flex justify-content-center align-items-center">
            `+ item['message'] + `
        </div><br>
                    `
                );
            }

            else {
                $('#conversations-container').append(`
                <div data-aos="zoom-in-up" data-aos-duration="1500" id=""
                class="main-contend-two p-3 shadow-lg text-center d-flex justify-content-center align-items-center">
                `+ item['message'] + `
            </div><br>
                `);

            }
        }
        $(window).scrollTop($('#last').offset().top);
    });

}