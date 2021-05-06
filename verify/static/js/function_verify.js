import {checkYourSimulation} from './common_function.js';
import {showPlot} from './common_function.js';
import {swalError} from './common_function.js';

$(document).ready(function () {
    let name_analysis = ['uniquness', 'smoothness', 'timestep']
    checkYourSimulation(name_analysis);

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation(name_analysis);
    });

    $("#submit_uniquness_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        let filesInputUniqueAnalysis = $("#files_input_unique_analysis")
        let char_sep = $('select[name=sep_unique_analysis]').val();

        if (filesInputUniqueAnalysis[0].files.length === 0) {
            swalError("No files selected")

        } else {
            let data = new FormData();
            $.each(filesInputUniqueAnalysis[0].files, function (i, file) {
                data.append("file", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append('name_analysis', name_analysis[0])
            data.append('sep', char_sep)

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
                                    checkYourSimulation(name_analysis)
                                }
                            })
                        }
                    });
                }
            })
        }
    });

    $("#submit_smoothness_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let column_select = $("#column_select_smoothness_analysis").val()
        let k_select = $("#k_value_smoothness_analysis").val()
        let filesInputSmoothnessAnalysis = $("#files_input_smoothness_analysis")
        let char_sep = $('select[name=sep_smoothness]').val();

        if (!column_select.trim() || !$.isNumeric(column_select)) {
            swalError("The \"K value\" fields are empty, or it is not numeric")
        } else {
            if (!k_select.trim() || !$.isNumeric(k_select)) {
                swalError("The \"K value\" fields are empty, or it is not numeric")
            } else {
                if (filesInputSmoothnessAnalysis[0].files.length === 0) {
                    swalError("No files selected")
                } else {
                    let data = new FormData();
                    $.each(filesInputSmoothnessAnalysis[0].files, function (i, file) {
                        data.append("file", file);
                    });
                    data.append("csrfmiddlewaretoken", csrf_token)
                    data.append("column_select", column_select)
                    data.append("k_select", k_select)
                    data.append('name_analysis', name_analysis[1])
                    data.append('sep', char_sep)

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
                                            checkYourSimulation(name_analysis)
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
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let column_select = $("#column_select_timestep").val()
        let filesInputTimestep = $("#files_input_timestep")
        let char_sep = $('select[name=sep_time_step]').val();

        if (!column_select.trim() || !$.isNumeric(column_select)) {
            swalError("The 'Column to analyze' field is empty or it is not numeric!")
        } else {
            if (filesInputTimestep[0].files.length === 0) {
                swalError("No files selected")

            } else {
                let data = new FormData();
                data.append("column_select", column_select)
                $.each(filesInputTimestep[0].files, function (i, file) {
                    data.append("file", file);
                });
                data.append("csrfmiddlewaretoken", csrf_token)
                data.append('name_analysis', name_analysis[2])
                data.append('sep', char_sep)

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
                                        checkYourSimulation(name_analysis)
                                    }
                                })
                            }
                        });
                    }
                })
            }
        }
    });

    // handles the change of the simulations
    $('select[name=simulation]').on('change', function () {

        let id_sim_pat = this.value;

        if (id_sim_pat !== '') {
            //set id simulation
            $('input[name=selectIdSimulation]').val(id_sim_pat);

            let pat_smoothness_plot = media_path + 'outputs/' + appname + '/' + user_username + '/' + id_sim_pat + '/' + 'Smoothness_Analysis.png'

            let http = new XMLHttpRequest();
            http.open('HEAD', pat_smoothness_plot, false);
            http.send();
            if (http.status === 200) {

                $("#type_plot option").each(function () {
                    $(this).removeAttr("selected");
                    $(this).hide();
                    console.log($(this).val())
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

            $(".printPlot").attr("src", '');

            $(".divPlot").removeAttr("style");

            showPlot(id_sim_pat, type_plot)
        }
    });

    // handles the change of the plots
    $('select[name=type_plot]').on('change', function () {

        let type_plot = $('select[name=type_plot]').val();
        let id_sim_pat = $('input[name=selectIdSimulation]').val();

        showPlot(id_sim_pat, type_plot);
    });
});

