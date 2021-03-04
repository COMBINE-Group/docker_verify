$(document).ready(function () {
    checkYourSimulation();

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation();
    });


    $("#submit_sobol_analysis").click(function () {
        //nascondo i div per i plot
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        let number_skip_row = $("input[name=number_skip_row_lhs]").val()
        let char_sep = $('select[name=char_sep_lhs]').val();
        let number_combinations = $("#number_combinations_lhs").val()
        let seed = $("#seed").val()

        if ($("#files_input_lhs")[0].files.length === 0) {
            swal({
                title: '<i>No files selected</i>',
                type: 'error',
                showCloseButton: true,
                showCancelButton: false,
                showConfirmButton: true,
                allowOutsideClick: false,
                allowEscapeKey: true
            });
        } else {
            let data = new FormData();
            $.each($("#files_input_lhs")[0].files, function (i, file) {
                data.append("file", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("number_skip_row", number_skip_row)
            data.append("char_sep", char_sep)
            data.append("number_combinations", number_combinations)
            data.append("seed", seed)

            swal({
                title: 'Running',
                html: 'please don\'t refresh the page!',
                allowEscapeKey: false,
                allowOutsideClick: false,
                showCloseButton: false,
                showConfirmButton: true,
                timer: 0,
                onOpen: () => {
                    swal.showLoading();

                    $.ajax({
                        type: 'POST',
                        url: url_run_sobol_analysis,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {

                            swal({
                                title: '<i>' + result.title + '</i>',
                                type: result.type,
                                html: '<a target="_blank" href="' + result.data + ' ">Download</a>',
                                showCloseButton: true,
                                showCancelButton: false,
                                showConfirmButton: true,
                                allowOutsideClick: false,
                                allowEscapeKey: true
                            }).then(result => {
                                if (result.value) {
                                    checkYourSimulation()
                                }
                            })
                        }
                    });
                }
            })
        }
    });


    $("#submit_sobol_analyze").click(function () {
        //nascondo i div per i plot
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        let number_skip_row = $("input[name=number_skip_row_analyze]").val()
        let char_sep = $('select[name=char_sep_analyze]').val();
        let seed = $("#seed_analyze").val()
        let number_combinations = $("#number_combinations_sobol").val()

        if ($("#files_parameter_input")[0].files.length === 0 || $("#files_output_model")[0].files.length === 0) {
            swal({
                title: '<i>No files selected</i>',
                type: 'error',
                showCloseButton: true,
                showCancelButton: false,
                showConfirmButton: true,
                allowOutsideClick: false,
                allowEscapeKey: true
            });
        } else {
            let data = new FormData();
            $.each($("#files_parameter_input")[0].files, function (i, file) {
                data.append("files_parameter_input", file);
            });

            $.each($("#files_output_model")[0].files, function (i, file) {
                data.append("files_output_model", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("number_skip_row", number_skip_row)
            data.append("char_sep", char_sep)
            data.append("seed", seed)
            data.append("number_combinations", number_combinations)

            swal({
                title: 'Running',
                allowEscapeKey: false,
                allowOutsideClick: false,
                showCloseButton: false,
                showConfirmButton: true,
                timer: 0,
                onOpen: () => {
                    swal.showLoading();

                    $.ajax({
                        type: 'POST',
                        url: url_run_sobol_analyze,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {
                            swal({
                                title: '<i>' + result.data + '</i>',
                                type: result.type,
                                html: result.msg,
                                showCloseButton: true,
                                showCancelButton: false,
                                showConfirmButton: true,
                                allowOutsideClick: false,
                                allowEscapeKey: true
                            }).then(result => {
                                if (result.value) {
                                    checkYourSimulation()
                                }
                            })
                        }
                    });
                }
            })
        }
    });

    // Gestisce l'azione del cambio della simulazione
    $('select[name=simulation]').on('change', function () {
        let tagSelect = $('select[name=type_plot] option:eq(0)');
        tagSelect.prop("selected", true);

        let id_sim_pat = this.value;
        let type_plot = tagSelect.val();

        if (id_sim_pat !== '') {
            //setto id della simulazione per recuperare i relativi grafici
            $('input[name=selectIdSimulation]').val(id_sim_pat);

            /*$.post(url_read_info, {
                'id_simulation': id_sim_pat,
                'csrfmiddlewaretoken': csrf_token
            }, function (data) {
                $('.infosim').html('').append(data.html);
            }, 'json');

            $.post(url_check_patient_dead, {
                'id_simulation': id_sim_pat,
                'csrfmiddlewaretoken': csrf_token
            }, function (data) {
                if (data.status === 1) {
                    swal({
                        title: '<i>MTB bacteria load excedeed: virtual patient was likely to be considered dead.</i>',
                        type: 'info',
                        showCloseButton: true,
                        showCancelButton: false,
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: true
                    })
                }
            }, 'json');*/

            //resetto il link dell'img
            $(".printPlot").attr("src", '');

            //mostro div per i plot
            $(".divPlot").removeAttr("style");

            showPlot(id_sim_pat, type_plot)
        }
    });

    //gestisce l'azione del cambio dei plot
    $('select[name=type_plot]').on('change', function () {

        let type_plot = $('select[name=type_plot]').val();
        let id_sim_pat = $('input[name=selectIdSimulation]').val();

        showPlot(id_sim_pat, type_plot);
    });
});

function checkYourSimulation() {
    swal({
        title: '<i>Search Simulations</i>',
        type: 'info',
        showCloseButton: true,
        showCancelButton: false,
        showConfirmButton: true,
        allowOutsideClick: false,
        allowEscapeKey: true
    });

    $.post(url_check_simulations, {
        'csrfmiddlewaretoken': csrf_token,
        'name_analysis': '_sobol_analysis'
    }, function (data) {

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

    }, "json");
}

function showPlot(id_sim, type_plot) {
    let path_plot = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim + '/' + type_plot + '.png';
    $(".printPlot").attr("src", path_plot);
    $(".divPrintPlot").removeAttr("style");
}

