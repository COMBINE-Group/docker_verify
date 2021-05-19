import {checkYourSimulation, delete_simulation} from './common_function.js';
import {showPlot} from './common_function.js';
import {swalError} from './common_function.js';

$(document).ready(function () {
    let name_analysis = 'smoothness'
    checkYourSimulation(name_analysis);

    $("#reload_simulation").click(function () {
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');
        checkYourSimulation(name_analysis);
    });

    $("#delete_simulation").click(function () {
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
                let id_sim = $('input[name=selectIdSimulation]').val()
                delete_simulation(id_sim);
                checkYourSimulation(name_analysis);
            }
        })
    });

    $("#submit_smoothness_analysis").click(function () {
        //hide div to show the plots
        $('.divPlot').attr('style', 'visibility: hidden;');
        $('.divPrintPlot').attr('style', 'visibility: hidden;');

        let column_select = $("#column_select_smoothness_analysis").val()
        let k_select = $("#k_value_smoothness_analysis").val()
        let filesInputSmoothnessAnalysis = $("#files_input_smoothness_analysis")
        let char_sep = $('select[name=sep_smoothness]').val();
        let skip_rows = $("#skip_rows").val();

        if (!column_select.trim() || !$.isNumeric(column_select)) {
            swalError("The \"Column value\" field are empty, or it is not a numeric value")
        } else {
            if (!k_select.trim() || !$.isNumeric(k_select)) {
                swalError("The \"Window Size value\" field are empty, or it is not a numeric value")
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
                    data.append('name_analysis', name_analysis)
                    data.append('skip_rows', skip_rows)
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

    // handles the change of the simulations
    $('select[name=simulation]').on('change', function () {

        let id_sim_pat = this.value;

        if (id_sim_pat !== '') {
            //set id simulation
            $('input[name=selectIdSimulation]').val(id_sim_pat);

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

