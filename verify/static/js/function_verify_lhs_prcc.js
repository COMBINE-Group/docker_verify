import {checkYourSimulation} from './common_function.js';
import {showPlot} from './common_function.js';
import {swalError} from './common_function.js';
import {download_matrix} from './common_function.js';

$(document).ready(function () {
    let name_analysis = ['LHS', 'PRCC']
    checkYourSimulation(name_analysis);

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation(name_analysis);
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
        let type_prcc = $("#type_prcc").is(':checked')
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
            data.append("type_prcc", type_prcc)
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
                        url: url_run_prcc_analysis,
                        data: data,
                        processData: false,
                        contentType: false,
                        dataType: 'JSON',
                        async: false,
                        cache: false,
                        success: function (result) {
                            swal({
                                title: '<i>' + result.mess + '</i>',
                                type: result.type,
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
        let substring = "LHS"

        let id_sim_pat = this.value;

        if (id_sim_pat.includes(substring)) {
            download_matrix(id_sim_pat, 'matrix_lhs.csv', 'LHS matrix')

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
    });

    // handles the change of the plots
    $('select[name=type_plot]').on('change', function () {

        let type_plot = $('select[name=type_plot]').val();
        let id_sim_pat = $('input[name=selectIdSimulation]').val();

        showPlot(id_sim_pat, type_plot);
    });
});