from django.conf import settings
from django.shortcuts import render
from utilities.tools import check_status_simulation, check_content_type, create_simulation_folder, \
    get_plot_trends_convergence_corr, save_and_convert_files, existence_and_unique_analysis, run_smoothness_analysis, \
    run_sobol_analysis
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
        return check_status_simulation(settings.BASE_DIR_VERIFY, settings.MEDIA_DIR_VERIFY, request.user.username,
                                       request.POST['name_analysis'])


def read_info_simulation(request):
    return None


def time_step_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) >= 2:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):
                starttime = 0

                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])
                new_list_files = save_and_convert_files(request.FILES.getlist('file'), os.getcwd())

                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1

                thread = threading.Thread(
                    target=get_plot_trends_convergence_corr('fig', new_list_files, col, starttime))
                thread.start()

                os.chdir(settings.BASE_DIR_VERIFY)

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

                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])
                new_list_files = save_and_convert_files(request.FILES.getlist('file'), os.getcwd())
                result = existence_and_unique_analysis(new_list_files)

                # delete unused folders
                folder_analysis_to_delete = os.getcwd()
                os.chdir(settings.BASE_DIR_VERIFY)
                shutil.rmtree(folder_analysis_to_delete)

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

                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])
                new_list_files, sep = save_and_convert_files(request.FILES.getlist('file'), os.getcwd())

                df = pd.read_csv(new_list_files[0], comment='#', sep=sep, header=None, engine='c', na_filter=False,
                                 low_memory=False)
                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1

                k = int(request.POST['k_select'])
                arr = df.iloc[:, col].values.tolist()
                arr_time = df.iloc[:, 0].values.tolist()
                thread = threading.Thread(target=run_smoothness_analysis(arr, arr_time, k))
                thread.start()

                os.chdir(settings.BASE_DIR_VERIFY)
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

                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])
                new_list_files, sep = save_and_convert_files(request.FILES.getlist('file'), os.getcwd())

                n_combinations = request.POST['number_combinations']

                params = run_sobol_analysis(new_list_files[0], int(n_combinations), int(request.POST['seed']))

                np.savetxt('out.txt', params)
                path = os.path.join(os.getcwd(), 'out.txt')
                path_out = path.split('/')[-6:]
                out = '/'.join(path_out)

                link = request.scheme + '://' + request.get_host() + '/' + out
                os.chdir(settings.BASE_DIR_VERIFY)

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

                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])

                list_files_uploaded, sep = save_and_convert_files(request.FILES.getlist('files_parameter_input'),
                                                                  os.getcwd())
                list_files_uploaded_1, sep = save_and_convert_files(request.FILES.getlist('files_output_model'),
                                                                    os.getcwd())

                n_combinations = request.POST['number_combinations']
                df = pd.read_csv(os.path.join(os.getcwd(), list_files_uploaded_1[0]), header=None, engine='c',
                                 na_filter=False, low_memory=False)

                # DA ESTRARRE DA new_list_files_1[0]
                yy = df.squeeze().to_numpy()

                params = run_sobol_analysis(list_files_uploaded[0], int(n_combinations), int(request.POST['seed']),
                                            flag=True, y=yy)

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': '', 'data': ''})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'You have choosed more than 1 files'})
