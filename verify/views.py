import os
import shutil
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
                             run_sobol_analysis, save_files, get_correct_col_value, is_columns_object)


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

                # here we check if separator and column are correct.
                df_tmp = pd.read_csv(new_list_files[0], sep=sep, skiprows=skip_rows)

                if len(df_tmp.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character is not correct '})
                elif col >= len(df_tmp.columns):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'The column {col} does not exist in your file'})

                if is_columns_object(new_list_files, sep, skip_rows):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator'})

                get_plot_trends_convergence_corr('results', new_list_files, col, starttime, path_sim,
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
                if is_columns_object(new_list_files, sep, skip_rows):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator'})

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
                elif result[0] == -1:
                    return JsonResponse({'status': 1, 'type': 'error', 'title': '<u>ERROR</u>',
                                         'mess': 'the number of lines in the files is different'})
                else:
                    return JsonResponse({'status': 1, 'type': 'error', 'title': '<u>ERROR</u>',
                                         'mess': 'the separator character is not correct'})
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
                col = get_correct_col_value(int(request.POST['column_select']))
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

                if len(df.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character is not correct'})
                elif col >= len(df.columns):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The column does not exist in your file'})

                if is_columns_object(new_list_files, sep, skip_rows):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator'})

                k = int(request.POST['k_select'])
                arr = df.iloc[:, col].values.tolist()
                arr_time = df.iloc[:, 0].values.tolist()
                run_smoothness_analysis(arr, arr_time, k, request.POST['name_analysis'], path_sim, str(col))

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

                seed = int(request.POST['seed'])
                n_combinations = int(request.POST['number_combinations'])
                sep = get_sep(request.POST['sep'])

                if not ((seed & (seed - 1) == 0) and (seed != 0 and seed - 1 != 0)):
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The seed must be an exponent of 2 '})

                if not ((n_combinations & (n_combinations - 1) == 0) and (n_combinations != 0 and n_combinations - 1 != 0)):
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The number of combination must be an exponent of 2 '})

                if n_combinations > seed:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The number of combination must be lower of seed '})

                path_sim = create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous',
                                                    request.POST['name_analysis'])

                new_list_files = save_files(request.FILES.getlist('file'), path_sim)

                df_params = pd.read_csv(new_list_files[0], sep=sep, engine='c', na_filter=False, low_memory=False)

                if len(df_params.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character is not correct'})
                elif len(df_params.columns) != 4:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'the number of expected columns is 4: param_name, '
                                                 'first_value, second_value, distribution'})

                if is_columns_object(new_list_files, sep):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator'})

                params, param_name = run_sobol_analysis(df_params, seed, request.POST['name_analysis'],
                                                        path_sim, n_comb=n_combinations)

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
                                     'mess': 'The file is not CSV'})
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

                ll = []
                for path in list_files_uploaded_1:
                    df = pd.read_csv(path, sep=sep_output_model_file, engine='c', na_filter=False, low_memory=False,
                                     header=None)
                    if len(df.columns) == 1:
                        shutil.rmtree(path_sim)
                        return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                             'mess': 'The separator character of the output model files are not correct'})
                    else:
                        ll.append(df)

                df_merged = pd.concat(ll, axis=0, ignore_index=True)
                if col > len(df_merged.columns):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The column does not exist in your file'})
                yy = df_merged[col - 1].squeeze().to_numpy()

                df_params = pd.read_csv(list_files_uploaded[0], sep=sep_input_parameter_file, engine='c',
                                        na_filter=False, low_memory=False)

                if len(df_params.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the parameter file is not correct'})
                elif len(df_params.columns) != 4:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'the number of expected columns is 4: param_name, '
                                                 'first_value, second_value, distribution'})

                if is_columns_object(list_files_uploaded_1, sep_output_model_file):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal '
                                                 f'separator in the output model files'})

                if is_columns_object(list_files_uploaded, sep_input_parameter_file):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator '
                                                 f'in the parameter file'})

                run_sobol_analysis(df_params, int(request.POST['seed']), request.POST['name_analysis'],
                                   path_sim, y=yy)

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
                if len(df_param.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the parameter file is not correct'})
                elif len(df_param.columns) != 3:
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'the number of expected columns is 3: param_name, min, max'})

                if is_columns_object(list_files_uploaded, sep):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator '
                                                 f'in the parameter file'})

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
                if len(lhs_matrix.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the LHS matrix is not correct'})

                ll = []
                try:
                    df = pd.read_csv(matrix_from_output[0], sep=sep_for_files, usecols=[0, col], engine='c', na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)
                except ValueError as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the outputs model file is not correct, '
                                                 'or you have selected a column that doesn\'t exist'})

                for i in range(1, len(matrix_from_output)):
                    df = pd.read_csv(matrix_from_output[i], sep=sep_for_files, usecols=[col], engine='c', na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)

                if is_columns_object(matrix_from_output, sep_for_files):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator '
                                                 f'in the outputs model file'})

                header = ["time"] + [str(i) for i in range(0, len(ll))]
                matrix_output = pd.concat(ll, axis=1, ignore_index=True)
                matrix_output.columns = header
                # matrix_output = pd.read_csv(matrix_from_output[0], sep=sep)
                response = run_prcc_analysis(lhs_matrix, matrix_output, path_sim, request)

                return response

            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'You have selected files that are not CSV'})
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
                if len(lhs_matrix.columns) == 1:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the LHS matrix is not correct'})

                ll = []
                try:
                    df = pd.read_csv(matrix_from_output[0], sep=sep_for_files, usecols=[0, col], engine='c',
                                     na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)
                except ValueError as e:
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': 'The separator character of the outputs model file is not correct, '
                                                 'or you have selected a column that doesn\'t exist'})

                for i in range(1, len(matrix_from_output)):
                    df = pd.read_csv(matrix_from_output[i], sep=sep_for_files, usecols=[col], engine='c',
                                     na_filter=False,
                                     low_memory=False, header=None)
                    ll.append(df)

                if is_columns_object(matrix_from_output, sep_for_files):
                    shutil.rmtree(path_sim)
                    return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                         'mess': f'There are some columns with comma as decimal separator '
                                                 f'in the outputs model file'})

                header = ["time"] + [str(i) for i in range(0, len(ll))]
                matrix_output = pd.concat(ll, axis=1, ignore_index=True)
                matrix_output.columns = header

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
