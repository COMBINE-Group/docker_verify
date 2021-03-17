from django.conf import settings
from django.shortcuts import render
from utilities.tools import check_status_simulation, check_content_type, create_simulation_folder, \
    get_plot_trends_convergence_corr, save_and_convert_files, existence_and_unique_analysis, run_smoothness_analysis, \
    run_sobol_analysis, run_lhs_analysis, run_prcc_analysis
from django.http import JsonResponse
import shutil
import os
import threading
import pandas as pd
import numpy as np


def verify_lhs_prcc(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_lhs_prcc_gen.html', data)


def verify_sobol(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_sobol_gen.html', data)


def verify(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_gen.html', data)


def check_simulations(request):
    if request.method == 'POST':
        return check_status_simulation(settings.BASE_DIR_VERIFY, settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                       request.POST['name_analysis'])


def read_info_simulation(request):
    return None


def time_step_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) >= 2:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):
                starttime = 0

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                try:
                    new_list_files = save_and_convert_files(request.FILES.getlist('file'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1

                get_plot_trends_convergence_corr('fig', new_list_files, col, starttime, path_sim,
                                                 request.POST['name_analysis'])

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
                try:
                    new_list_files = save_and_convert_files(request.FILES.getlist('file'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})
                result = existence_and_unique_analysis(new_list_files)

                # delete unused folders
                shutil.rmtree(path_sim)

                if result[0] == 0:
                    return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>the files are the same</u>',
                                         'mess': ''})
                elif result[0] == 1:
                    return JsonResponse({'status': 1, 'type': 'warning', 'title': '<u>the files are NOT the same</u>',
                                         'mess': 'Min(SD): %s' % result[1]})
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

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                try:
                    new_list_files = save_and_convert_files(request.FILES.getlist('file'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                df = pd.read_csv(new_list_files[0], comment='#', engine='c', na_filter=False, low_memory=False)
                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1

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
                try:
                    new_list_files = save_and_convert_files(request.FILES.getlist('file'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                n_combinations = request.POST['number_combinations']

                params, param_name = run_sobol_analysis(new_list_files[0], int(n_combinations),
                                                        int(request.POST['seed']), request.POST['name_analysis'])

                np.savetxt('out.csv', params, delimiter=',', fmt='%f', header=','.join(param_name), comments='')
                path = os.path.join(os.getcwd(), 'sobol_matrix.csv')
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
        if len(request.FILES.getlist('files_parameter_input')) == 1 and \
                len(request.FILES.getlist('files_output_model')) == 1:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                try:
                    list_files_uploaded = save_and_convert_files(request.FILES.getlist('files_parameter_input'),
                                                                 path_sim)
                    list_files_uploaded_1 = save_and_convert_files(request.FILES.getlist('files_output_model'),
                                                                   path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                n_combinations = request.POST['number_combinations']
                df = pd.read_csv(os.path.join(os.getcwd(), list_files_uploaded_1[0]), header=None, engine='c',
                                 na_filter=False, low_memory=False)

                yy = df.squeeze().to_numpy()

                params = run_sobol_analysis(list_files_uploaded[0], int(n_combinations), int(request.POST['seed']),
                                            request.POST['name_analysis'], flag=True, y=yy)

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

                try:
                    list_files_uploaded = save_and_convert_files(request.FILES.getlist('files_input_lhs'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                df_param = pd.read_csv(list_files_uploaded[0], engine='c', na_filter=False, low_memory=False)

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
        if len(request.FILES.getlist('file_input_prcc')) == 1 and len(request.FILES.getlist('file_matrix_lhs')) == 1:
            if check_content_type(request.FILES.getlist('file_input_prcc'), 'text/csv,application/octet-stream') and \
                    check_content_type(request.FILES.getlist('file_matrix_lhs'), 'text/csv,application/octet-stream'):

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])
                try:
                    matrix_from_output = save_and_convert_files(request.FILES.getlist('file_input_prcc'), path_sim)
                    matrix_lhs = save_and_convert_files(request.FILES.getlist('file_matrix_lhs'), path_sim)
                except Exception as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': e.args[0]})

                lhs_matrix = pd.read_csv(matrix_lhs[0])
                matrix_output = pd.read_csv(matrix_from_output[0])

                return run_prcc_analysis(lhs_matrix, matrix_output, path_sim, request.POST['name_analysis'], request)

            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse(
                {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'You have choosed more than 1 files'})
