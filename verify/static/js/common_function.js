function checkYourSimulation(name_analysis) {
    swal({
        title: '<i>Search Simulations</i>',
        type: 'info',
        showCloseButton: true,
        showCancelButton: false,
        showConfirmButton: true,
        allowOutsideClick: false,
        allowEscapeKey: true
    });
    let data = new FormData();
    data.append("csrfmiddlewaretoken", csrf_token)
    data.append("name_analysis", name_analysis)

    $.ajax({
            type: 'POST',
            url: url_check_simulations,
            data: data,
            processData: false,
            contentType: false,
            dataType: 'JSON',
            async: false,
            cache: false,
            success: function (data) {
                if (data.status === 1) {
                    $('select[name=simulation]').html('<option value="">Choose..</option>').append(data.html)
                }

                swal({
                    title: '<i>' + data.title + '</i>',
                    type: data.type,
                    html: data.mess,
                    showCloseButton: true,
                    showCancelButton: false,
                    showConfirmButton: true,
                    allowOutsideClick: false,
                    allowEscapeKey: true
                })
            }
        }
    )

}

function showPlot(id_sim, type_plot) {
    let path_plot = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim + '/' + type_plot + '.png';

    $(".printPlot").attr("src", path_plot);
    $(".divPrintPlot").removeAttr("style");
}

function swalError(msg) {
    let title = '<i>' + msg + '</i>'
    swal({
        title: title,
        type: 'error',
        showCloseButton: true,
        showCancelButton: false,
        showConfirmButton: true,
        allowOutsideClick: false,
        allowEscapeKey: true
    });
}

export {showPlot, checkYourSimulation, swalError}