import os
import shutil
import threading

import numpy as np
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from utilities.tools import (check_content_type, check_status_simulation,
                             create_simulation_folder,
                             existence_and_unique_analysis, get_media_link,
                             get_plot_trends_convergence_corr, get_sep,
                             run_lhs_analysis, run_prcc_analysis,
                             run_prcc_specific_ts, run_smoothness_analysis,
                             run_sobol_analysis, save_files, get_correct_col_value)


def verify_lhs_prcc(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/verify_lhs_prcc_gen.html', data)


def verify_sobol(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/verify_sobol_gen.html', data)


def verify(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/verify_gen.html', data)


def verify_smoothness(response):
    data = {
        'appname': 'verify',
        'title': 'Smoothness',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/smoothness.html', data)


def verify_time_step(response):
    data = {
        'appname': 'verify',
        'title': 'Time Step',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/time_step.html', data)


def verify_unique_exist(response):
    data = {
        'appname': 'verify',
        'title': 'Existence Unique',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/exist_unique.html', data)


def verify_documentation(response):
    data = {
        'appname': 'verify',
        'title': 'documentation',
        'media_path': settings.MEDIA_URL,
        'version': settings.VERSION,
    }

    return render(response, 'verify/documentation.html', data)


def check_simulations(request):
    if request.method == 'POST':
        return check_status_simulation(settings.BASE_DIR_VERIFY, settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                       request.POST['name_analysis'])


def delete_simulations(request):
    if request.method == 'POST':
        name_sim = request.POST['path_sim'].split('/')[-2]
        shutil.rmtree(os.path.join(settings.MEDIA_DIR_VERIFY, 'Anonymous', name_sim))

        return JsonResponse({'status': 0, 'type': 'success', 'title': 'Deleted',
                             'mess': f'{name_sim} has been deleted.'})


def read_info_simulation(request):
    return None


def time_step_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) >= 2:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):

                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1
                else:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The first column is used for the X-axis of the plot '})
                starttime = 0

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep = get_sep(request.POST['sep'])
                new_list_files = save_files(request.FILES.getlist('file'), path_sim)
                skip_rows = int(request.POST['skip_rows'])

                get_plot_trends_convergence_corr('fig', new_list_files, col, starttime, path_sim,
                                                 request.POST['name_analysis'], sep, skip_rows)

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': ''})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'You need to select more than two files'})


def uniqueness_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) >= 2:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep = get_sep(request.POST['sep'])
                skip_rows = int(request.POST['skip_rows'])
                new_list_files = save_files(request.FILES.getlist('file'), path_sim)

                result = existence_and_unique_analysis(new_list_files, sep, skip_rows)

                # delete unused folders
                shutil.rmtree(path_sim)

                if result[0] == 0:
                    return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>the files are the same</u>',
                                         'mess': ''})
                elif result[0] == 1:
                    return JsonResponse({'status': 1, 'type': 'warning', 'title': '<u>the files are NOT the same</u>',
                                         'mess': f'In your files at row:{result[1]} and at column: {result[2]} '
                                                 f'the SD is:{result[3]}'})
                else:
                    return JsonResponse({'status': 1, 'type': 'error', 'title': '<u>ERROR</u>',
                                         'mess': 'the number of lines in the files is different'})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'There was a problem during execution!'})


def smoothness_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) == 1:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):
                col = get_correct_col_value(int(request.POST['col']))
                if col == -1:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The first column is used for the X-axis of the plot '})

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep = get_sep(request.POST['sep'])
                new_list_files = save_files(request.FILES.getlist('file'), path_sim)
                skip_rows = int(request.POST['skip_rows'])

                df = pd.read_csv(new_list_files[0], skiprows=skip_rows, header=None, decimal=',',
                                 sep=sep, engine='c', na_filter=False, low_memory=False)

                k = int(request.POST['k_select'])
                arr = df.iloc[:, col].values.tolist()
                arr_time = df.iloc[:, 0].values.tolist()
                run_smoothness_analysis(arr, arr_time, k, request.POST['name_analysis'], path_sim)

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'data': ''})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'There was a problem during execution!'})


def sobol_generates_sample(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) == 1:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep = get_sep(request.POST['sep'])

                new_list_files = save_files(request.FILES.getlist('file'), path_sim)

                n_combinations = request.POST['number_combinations']

                params, param_name = run_sobol_analysis(new_list_files[0], int(n_combinations),
                                                        int(request.POST['seed']),
                                                        request.POST['name_analysis'], path_sim, sep)

                np.savetxt(os.path.join(path_sim, 'sobol_matrix.csv'), params, delimiter=',', fmt='%f',
                           header=','.join(param_name), comments='')
                path = os.path.join(path_sim, 'sobol_matrix.csv')
                path_out = path.split('/')[-6:]
                out = '/'.join(path_out)

                link = request.scheme + '://' + request.get_host() + '/' + out

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'data': link})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'No files selected!'})


def sobol_analyze(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file_range_parameter')) == 1 and \
                len(request.FILES.getlist('file_output_model')) >= 1:
            if check_content_type(request.FILES.getlist('file_range_parameter'),
                                  'text/csv,application/octet-stream') and \
                    check_content_type(request.FILES.getlist('file_output_model'), 'text/csv,application/octet-stream'):

                col = int(request.POST['col_sobol'])

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])

                sep_input_parameter_file = get_sep(request.POST['sep_input_parameter_file'])
                sep_output_model_file = get_sep(request.POST['sep_output_model_file'])

                list_files_uploaded = save_files(request.FILES.getlist('file_range_parameter'), path_sim)
                list_files_uploaded_1 = save_files(request.FILES.getlist('file_output_model'), path_sim)

                n_combinations = request.POST['number_combinations']
                ll = []
                for path in list_files_uploaded_1:
                    df = pd.read_csv(path, sep=sep_output_model_file, engine='c', na_filter=False, low_memory=False,
                                     header=None)
                    ll.append(df)

                df_merged = pd.concat(ll, axis=0, ignore_index=True)
                yy = df_merged[col - 1].squeeze().to_numpy()

                params = run_sobol_analysis(list_files_uploaded[0], int(n_combinations), int(request.POST['seed']),
                                            request.POST['name_analysis'], path_sim, sep=sep_input_parameter_file,
                                            flag=True, y=yy)

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'data': ''})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'You have choosed more than 1 files'})


def lhs_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('files_input_lhs')) == 1:
            if check_content_type(request.FILES.getlist('files_input_lhs'), 'text/csv,application/octet-stream'):

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep = get_sep(request.POST['sep'])

                list_files_uploaded = save_files(request.FILES.getlist('files_input_lhs'), path_sim)

                df_param = pd.read_csv(list_files_uploaded[0], sep=sep, engine='c', na_filter=False, low_memory=False)

                tuple_min_max_vf = list(zip(df_param['min'], df_param['max']))
                inputs_space = dict(zip(df_param['param_name'], tuple_min_max_vf))

                matrix_lhs = run_lhs_analysis(inputs_space, int(request.POST['number_combinations']),
                                              int(request.POST['seed']), int(request.POST['iterations']), path_sim,
                                              request.POST['name_analysis'])

                matrix_lhs.to_csv(os.path.join(path_sim, 'matrix_lhs.csv'), index=False)
                path = os.path.join(path_sim, 'matrix_lhs.csv')
                path_out = path.split('/')[-6:]
                out = '/'.join(path_out)

                link = request.scheme + '://' + request.get_host() + '/' + out

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'data': link})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'You have choosed more than 1 files'})


def prcc_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file_input_prcc')) > 1 and len(request.FILES.getlist('file_matrix_lhs')) == 1:
            if check_content_type(request.FILES.getlist('file_input_prcc'), 'text/csv,application/octet-stream') and \
                    check_content_type(request.FILES.getlist('file_matrix_lhs'), 'text/csv,application/octet-stream'):

                col = get_correct_col_value(int(request.POST['col']))
                if col == -1:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The first column is used for the X-axis of the plot '})

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])

                sep_lhs = get_sep(request.POST['sep_for_lhs'])
                sep_for_files = get_sep(request.POST['sep_for_files'])
                matrix_from_output = save_files(request.FILES.getlist('file_input_prcc'), path_sim)
                matrix_lhs = save_files(request.FILES.getlist('file_matrix_lhs'), path_sim)

                lhs_matrix = pd.read_csv(matrix_lhs[0], sep=sep_lhs)

                ll = []
                df = pd.read_csv(matrix_from_output[0], sep=sep_for_files, usecols=[0, col], engine='c', na_filter=False,
                                 low_memory=False, header=None)
                ll.append(df)
                for i in range(1, len(matrix_from_output)):
                    df = pd.read_csv(matrix_from_output[i], sep=sep_for_files, usecols=[col], engine='c', na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)

                matrix_output = pd.concat(ll, axis=1, ignore_index=True)
                # matrix_output = pd.read_csv(matrix_from_output[0], sep=sep)

                plot_file, time_corr_file, response = run_prcc_analysis(lhs_matrix, matrix_output, path_sim, request)

                link_plot = get_media_link(plot_file, request.scheme, request.get_host())
                link_time_corr = get_media_link(time_corr_file, request.scheme, request.get_host())

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'link_plot': link_plot, 'link_time_corr': link_time_corr})

            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse(
                {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'You have chosen less than 1 files'})


def prcc_analysis_specific_ts(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file_input')) > 1 and len(request.FILES.getlist('file_matrix_lhs')) == 1:
            if check_content_type(request.FILES.getlist('file_input'), 'text/csv,application/octet-stream') and \
                    check_content_type(request.FILES.getlist('file_matrix_lhs'), 'text/csv,application/octet-stream'):

                col = get_correct_col_value(int(request.POST['col']))
                if col == -1:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The first column is used for the X-axis of the plot '})

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                sep_for_lhs = get_sep(request.POST['sep_for_lhs'])
                sep_for_files = get_sep(request.POST['sep_for_files'])

                matrix_from_output = save_files(request.FILES.getlist('file_input'), path_sim)
                matrix_lhs = save_files(request.FILES.getlist('file_matrix_lhs'), path_sim)

                lhs_matrix = pd.read_csv(matrix_lhs[0], sep=sep_for_lhs)

                ll = []
                df = pd.read_csv(matrix_from_output[0], sep=sep_for_files, usecols=[0, col], engine='c',
                                 na_filter=False,
                                 low_memory=False, header=None)
                ll.append(df)
                for i in range(1, len(matrix_from_output)):
                    df = pd.read_csv(matrix_from_output[i], sep=sep_for_files, usecols=[col], engine='c',
                                     na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)

                matrix_output = pd.concat(ll, axis=1, ignore_index=True)

                # matrix_output = pd.read_csv(matrix_from_output[0], sep=sep)

                plot_file, status = run_prcc_specific_ts(lhs_matrix, matrix_output, path_sim, request)

                # if status is True, than the PDF is not empty
                if status:
                    link_plot = get_media_link(plot_file, request.scheme, request.get_host())

                    return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                         'mess': '', 'link_plot': link_plot})
                else:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'PDF file is empty!',
                                         'mess': 'No scatter plots was generated'})
            else:
                return JsonResponse(
                    {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse(
                {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'You have chose less than 1 files'})
