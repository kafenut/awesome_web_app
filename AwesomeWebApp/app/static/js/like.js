$('.like_link').find('a').click(function (event) {   //a like link
    event.preventDefault();
    var link = $(this).parent();
    var id = link.data('id');
    var type = link.data('type');
    var like;
    if (link.data('like') === 'like') //To confirm is it a like or a cancel of like
        like = true;
    else
        like = false;
    var raw_data = {
        title: 'like_blog',
        id: id,
        type: type,
        like: like
    }
    var data = JSON.stringify(raw_data);
    $.ajax({
        url: '/like_blog',
        method: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: data
    }).done(function (data) {
        if (data.success === true) {
            var span = link.find('span');
            if (like === true) {
                link.data('like', 'unlike');
                link.find('a').css('color', 'red');
                link.find('svg').attr('data-prefix', 'fas')
                span.text(String(Number(span.text()) + 1));
            }
            else {
                link.data('like', 'like');
                link.find('a').css('color', '');
                link.find('svg').attr('data-prefix', 'far')
                span.text(String(Number(span.text()) - 1));
            }
        }
        else {
            $('#alert').html(data.text);
        }
    }).fail(function (xhr, status) {
        $('#alert').html('fail: ' + xhr.status + ',reason: ');
    });
});