$(document).ready(function () {
    checkYourSimulation();

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation();
    });

    $("#submit_uniquness_analysis").click(function () {
        //nascondo i div per i plot
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        if ($("#files_input_unique_analysis")[0].files.length === 0) {
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
            $.each($("#files_input_unique_analysis")[0].files, function (i, file) {
                data.append("file", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append('name_analysis', '_uniquness_analysis')

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
                        url: url_run_uniqueness_analysis,
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
                                html: result.mess,
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

    $("#submit_smoothness_analysis").click(function () {
        //nascondo i div per i plot
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        let column_select = $("#column_select_smoothness_analysis").val()
        let k_select = $("#k_value_smoothness_analysis").val()

        if (!column_select.trim() || !$.isNumeric(column_select)) {
            swal({
                title: '<i>The "Column to analyze" fields are empty, or it is not numeric</i>',
                type: 'error',
                showCloseButton: true,
                showCancelButton: false,
                showConfirmButton: true,
                allowOutsideClick: false,
                allowEscapeKey: true
            });
        } else {
            if (!k_select.trim() || !$.isNumeric(k_select)) {
                swal({
                    title: '<i>The "K value" fields are empty, or it is not numeric</i>',
                    type: 'error',
                    showCloseButton: true,
                    showCancelButton: false,
                    showConfirmButton: true,
                    allowOutsideClick: false,
                    allowEscapeKey: true
                });
            } else {
                if ($("#files_input_smoothness_analysis")[0].files.length === 0) {
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
                    $.each($("#files_input_smoothness_analysis")[0].files, function (i, file) {
                        data.append("file", file);
                    });
                    data.append("csrfmiddlewaretoken", csrf_token)
                    data.append("column_select", column_select)
                    data.append("k_select", k_select)
                    data.append('name_analysis', '_smoothness_analysis')

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
                                url: url_run_smoothness_analysis,
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
                                        html: result.mess,
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
            }
        }
    });


    $("#submit_timestep_analysis").click(function () {
        //nascondo i div per i plot
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        let column_select = $("#column_select_timestep").val()

        if (!column_select.trim() || !$.isNumeric(column_select)) {
            swal({
                title: '<i>The "Column to analyze" field is empty or it not numeric!</i>',
                type: 'error',
                showCloseButton: true,
                showCancelButton: false,
                showConfirmButton: true,
                allowOutsideClick: false,
                allowEscapeKey: true
            });
        } else {
            if ($("#files_input_timestep")[0].files.length === 0) {
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
                data.append("column_select", column_select)
                $.each($("#files_input_timestep")[0].files, function (i, file) {
                    data.append("file", file);
                });
                data.append("csrfmiddlewaretoken", csrf_token)
                data.append('name_analysis', '_timestep_analysis')

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
                            url: url_run_time_step_analysis,
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
                                    html: result.mess,
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
        }
    });

    // Gestisce l'azione del cambio della simulazione
    $('select[name=simulation]').on('change', function () {

        let id_sim_pat = this.value;

        if (id_sim_pat !== '') {
            //setto id della simulazione per recuperare i relativi grafici
            $('input[name=selectIdSimulation]').val(id_sim_pat);

            let pat_smoothness_plot = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim_pat + '/' + 'Smoothness_Analysis.png'
            console.log(pat_smoothness_plot)
            let http = new XMLHttpRequest();
            http.open('HEAD', pat_smoothness_plot, false);
            http.send();
            if (http.status === 200) {

                $("#type_plot option").each(function () {
                    $(this).removeAttr("selected");
                    $(this).hide();
                    if ($(this).val() === "Smoothness_Analysis") {
                        $(this).show();
                        $(this).attr("selected", "selected");
                    }
                });
            } else {
                $("#type_plot option").each(function () {
                    $(this).removeAttr("selected");
                    $(this).hide();
                    if ($(this).val() !== "Smoothness_Analysis") {
                        $(this).show();
                        if ($(this).val() === "fig_trends") {
                            $(this).attr("selected", "selected");
                        }
                    }
                });
            }

            let tagSelect = $('select[name=type_plot]').find(":selected");
            tagSelect.prop("selected", true);
            let type_plot = tagSelect.val();
            console.log(type_plot)
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

    $.post(url_check_simulations, {'csrfmiddlewaretoken': csrf_token, 'name_analysis': ''}, function (data) {

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
