import {checkYourSimulation, prompt_delete_simulation} from './common_function.js';
import {showPlot} from './common_function.js';
import {swalError} from './common_function.js';
import {download_matrix} from './common_function.js';

$(document).ready(function () {
    let name_analysis = ['LHS', 'PRCC_overTime', 'PRCC_specific_TS']
    checkYourSimulation(name_analysis);

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation(name_analysis);
    });

    $("#delete_simulation").click(function () {
        let id_sim = $('#id_simulations option:selected').text();
        prompt_delete_simulation(id_sim, name_analysis);
    });

    $("#submit_lhs_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let number_combinations = $("#number_samples_lhs").val()
        let seed_lhs = $("#seed_lhs").val()
        let filesInputLHS = $("#files_input_lhs")
        let iterations = $("#iterations").val()
        let char_sep = $('select[name=sep_lhs]').val();

        if (filesInputLHS[0].files.length === 0) {
            swalError("No files selected")
        } else {
            let data = new FormData();
            $.each(filesInputLHS[0].files, function (i, file) {
                data.append("files_input_lhs", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("number_combinations", number_combinations)
            data.append("seed", seed_lhs)
            data.append("iterations", iterations)
            data.append("name_analysis", name_analysis[0])
            data.append("sep", char_sep)

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
                        url: url_run_lhs_analysis,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {
                            let html = ''
                            if (result.status === 1) {
                                html = '<a target="_blank" href="' + result.data + ' ">Download</a>'
                            }

                            swal({
                                title: '<i>' + result.title + '</i>',
                                type: result.type,
                                html: html,
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


    $("#submit_prcc_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let fileInputPrcc = $("#file_input_prcc")
        let fileMatrixLhs = $("#file_matrix_lhs")
        let step_time_points = $("#step_times_points").val()
        let threshold_pvalue = $("#threshold_pvalue").val()
        let char_sep = $('select[name=sep_prcc]').val();

        if (fileInputPrcc[0].files.length === 0 && fileMatrixLhs[0].files.length === 0) {
            swalError("No files selected")
        } else {
            let data = new FormData();
            $.each(fileInputPrcc[0].files, function (i, file) {
                data.append("file_input_prcc", file);
            });

            $.each(fileMatrixLhs[0].files, function (i, file) {
                data.append("file_matrix_lhs", file);
            });

            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("name_analysis", name_analysis[1])
            data.append("step_time_points", step_time_points)
            data.append("sep", char_sep)
            data.append("threshold_pvalue", threshold_pvalue)

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
                        url: url_run_prcc_analysis,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {
                            let html = ''
                            if (result.status === 1) {
                                html = '<a target="_blank" href="' + result.link_plot + ' ">Download PDF plot</a><br/>'
                                html += '<a target="_blank" href="' + result.link_time_corr + ' ">Download Time Correlation file</a>'
                            }

                            swal({
                                title: '<i>' + result.mess + '</i>',
                                type: result.type,
                                html: html,
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

    $("#submit_prcc_analysis_specific_ts").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let timeStep = $("#time_step").val()
        let threshold_pvalue = $("#threshold_pvalue_specific_ts").val()
        let char_sep = $('select[name=sep_prcc_specific_ts]').val();
        let fileInput = $("#file_input_specific_ts")
        let fileMatrixLhs = $("#file_matrix_lhs_specific_ts")

        if (fileInput[0].files.length === 0 && fileMatrixLhs[0].files.length === 0) {
            swalError("No files selected")
        } else {
            let data = new FormData();
            $.each(fileInput[0].files, function (i, file) {
                data.append("file_input", file);
            });

            $.each(fileMatrixLhs[0].files, function (i, file) {
                data.append("file_matrix_lhs", file);
            });

            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("name_analysis", name_analysis[2])
            data.append("timeStep", timeStep)
            data.append("pvalue", threshold_pvalue)
            data.append("sep", char_sep)

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
                        url: url_run_prcc_analysis_specific_ts,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {
                            let html = ''
                            if (result.status === 1) {
                                html = '<a target="_blank" href="' + result.link_plot + ' ">Download PDF plot</a><br/>'
                            }
                            else{
                                html = result.mess
                            }

                            swal({
                                title: '<i>' + result.title + '</i>',
                                type: result.type,
                                html: html,
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

    // handles the change of the simulations
    $('select[name=simulation]').on('change', function () {
        let tagSelect = $('select[name=type_plot] option:eq(0)');
        tagSelect.prop("selected", true);

        let id_sim_pat = this.value;

        if (id_sim_pat.includes(name_analysis[0])) {
            download_matrix(id_sim_pat, ['matrix_lhs.csv'], ['LHS matrix'])

        } else {
            if (id_sim_pat.includes(name_analysis[1])) {
                download_matrix(id_sim_pat, ['plot_prcc_overtime.pdf', 'time_corr.json'], ['Download PDF plot', 'Download Time Correlation file'])
            } else {
                let type_plot = tagSelect.val();

                if (id_sim_pat !== '') {
                    //set id simulation
                    $('input[name=selectIdSimulation]').val(id_sim_pat);

                    $(".printPlot").attr("src", '');

                    $(".divPlot").removeAttr("style");

                    showPlot(id_sim_pat, type_plot)
                }
            }
        }
    });

    // handles the change of the plots
    $('select[name=type_plot]').on('change', function () {

        let type_plot = $('select[name=type_plot]').val();
        let id_sim_pat = $('input[name=selectIdSimulation]').val();

        showPlot(id_sim_pat, type_plot);
    });
});