function logout() {
    $.ajax({
        url: "/passport/logout",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            // 刷新当前界面
            location.reload()
        }
    })
}