import {checkYourSimulation, download_matrix} from './common_function.js';
import {showPlot} from './common_function.js';
import {swalError} from './common_function.js';

$(document).ready(function () {
    let name_analysis = ['sobol_generates_samples', 'sobol_analyze']
    checkYourSimulation(name_analysis);

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation(name_analysis);
    });

    $("#submit_sobol_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let number_combinations = $("#number_combinations_sobol").val()
        let seed = $("#seed_analysis").val()
        let filesInputSobol = $("#files_input_sobol")

        if (filesInputSobol[0].files.length === 0) {
            swalError("No files selected")
        } else {
            let data = new FormData();
            $.each(filesInputSobol[0].files, function (i, file) {
                data.append("file", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("number_combinations", number_combinations)
            data.append("seed", seed)
            data.append("name_analysis", name_analysis[0])

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
                                    checkYourSimulation(name_analysis)
                                }
                            })
                        }
                    });
                }
            })
        }
    });


    $("#submit_sobol_analyze").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let seed = $("#seed_analyze").val()
        let number_combinations = $("#number_combinations_sobol").val()
        let filesParameterInput = $("#files_parameter_input")
        let filesOutputModel = $("#files_output_model")

        if (filesParameterInput[0].files.length === 0 || [0].files.length === 0) {
            swalError("No files selected")
        } else {
            let data = new FormData();
            $.each(filesParameterInput[0].files, function (i, file) {
                data.append("files_parameter_input", file);
            });

            $.each(filesOutputModel[0].files, function (i, file) {
                data.append("files_output_model", file);
            });
            data.append("csrfmiddlewaretoken", csrf_token)
            data.append("seed", seed)
            data.append("number_combinations", number_combinations)
            data.append("name_analysis", name_analysis[1])

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
        let substring = name_analysis[0]

        let id_sim_pat = this.value;
        if (id_sim_pat.includes(substring)) {
            download_matrix(id_sim_pat, 'sobol_matrix.csv', 'Sobol matrix')

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

