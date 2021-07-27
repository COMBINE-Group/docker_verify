function checkYourSimulation(name_analysis) {
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

function download_matrix(id_sim_pat, name_file, msg) {
    let html = ''
    for (let i=0; i<name_file.length; i++){
        let path_file = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim_pat + '/'+name_file[i];
        html += '<a target="_blank" href="' + path_file + ' ">'+msg[i]+'</a><br/>'
    }

    swal({
        title: '<i>Download</i>',
        type: 'success',
        html: html,
        showCloseButton: true,
        showCancelButton: false,
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: true
    })
}

function delete_simulation(id_sim){
    let path_sim = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim + '/'
    let data = new FormData();
    data.append("csrfmiddlewaretoken", csrf_token)
    data.append("path_sim", path_sim)

    $.ajax({
            type: 'POST',
            url: url_delete_simulations,
            data: data,
            processData: false,
            contentType: false,
            dataType: 'JSON',
            async: false,
            cache: false,
            success: function (data) {
                swal({
                    title: data.title,
                    type: data.type,
                    html: data.mess,
                    timer: 2500,
                    showCloseButton: true,
                    showCancelButton: false,
                    showConfirmButton: false,
                    allowOutsideClick: false,
                    allowEscapeKey: true
                 })
            }
        }
    )
}

function prompt_delete_simulation(id_sim, name_analysis){
    if (id_sim !== "Choose..") {
        swal({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.value) {
            $('.divPlot').attr('style', 'visibility: hidden;');
            $('.divPrintPlot').attr('style', 'visibility: hidden;');
            delete_simulation(id_sim);
            checkYourSimulation(name_analysis);
        }
    })
}
}

export {showPlot, checkYourSimulation, swalError, download_matrix, prompt_delete_simulation}