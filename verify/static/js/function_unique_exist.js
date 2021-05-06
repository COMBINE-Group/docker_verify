import {checkYourSimulation} from './common_function.js';
import {swalError} from './common_function.js';

$(document).ready(function () {
    let name_analysis = 'uniquness'
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
            data.append('name_analysis', name_analysis)
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
});
