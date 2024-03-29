import json
import os
import shutil
from pathlib import Path
from time import localtime, strftime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
from natsort import natsorted
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from matplotlib.backends.backend_pdf import PdfPages
from SALib.analyze import sobol
from SALib.sample import saltelli
from scipy.stats import rankdata, stats
from sklearn.linear_model import LinearRegression
from skopt.sampler import Lhs
from skopt.space import Space


def get_sep(sep: str):
    if sep == 'tab' or sep == 'space':
        val = '\s+'
    elif sep == 'semicol':
        val = ';'
    else:
        val = ','
    return val


def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def copy_files(path, name_files):
    for name in name_files:
        shutil.copy2(os.path.join(path, name), name)


def create_simulation_folder(path, username, name_analysis):
    # [START] it check if simulation folder of user exists
    dir_simulation_user = os.path.join(path, username)

    if not os.path.isdir(dir_simulation_user):
        os.makedirs(dir_simulation_user)
    # [END]

    simulation_id = name_analysis + strftime("%Y-%m-%d_%H:%M:%S", localtime())
    path_simulation_id = os.path.join(dir_simulation_user, simulation_id)

    if not os.path.isdir(path_simulation_id):
        os.makedirs(path_simulation_id)
    else:
        return JsonResponse(
            {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'There was a problem during execution!'})

    return path_simulation_id


def check_status_simulation(base_dir, path, username, name_analysis):
    dir_simulation_user = os.path.join(path, username)

    if not os.path.isdir(dir_simulation_user):
        return JsonResponse({'status': 0, 'type': 'warning', 'title': 'Done!', 'mess': 'No simulation found!'})
    else:
        html_s = ''
        html_f = ''

        for filename in Path(dir_simulation_user).rglob('*.process'):
            for name in name_analysis.split(','):
                started_string = 'STARTED_' + name + '.process'
                finished_string = 'FINISHED_' + name + '.process'
                if filename.parts[-1] == started_string:
                    html_s += '<option value="">' + filename.parts[-2] + '</option>'
                elif filename.parts[-1] == finished_string:
                    html_f += '<option value="' + filename.parts[-2] + '">' + filename.parts[-2] + '</option>'

        html_s = '<optgroup label="Started">' + html_s + '</optgroup>'
        html_f = '<optgroup label="Finished">' + html_f + '</optgroup>'

        html = html_s + html_f

        return JsonResponse({'status': 1, 'type': 'success', 'title': 'Your Simulations!',
                             'mess': 'Loading completed successfully',
                             'path': os.path.join(path, 'outputs'),
                             'html': html})


def check_content_type(list_of_file, typ):
    flag = True
    typ = typ.split(',')
    for elem in list_of_file:
        if flag and elem.content_type not in typ:
            flag = False
    return flag


def check_number_rows_csv(csv_files):
    with open(csv_files[0], 'r') as ff:
        row_count = sum(1 for row in ff)

    for f in csv_files[1:]:
        with open(f, 'r') as ff:
            if row_count != sum(1 for row in ff):
                return False
    return True


def parse_files(filename_output, files, col, path_sim, sep, skip_rows, start=0, end=0, starttime=0, endtime=float('inf')):
    alist = []
    mean_value = []

    for f in files:
        # lista = read_data(f)
        lista = pd.read_csv(f, sep=sep, skiprows=skip_rows).to_numpy()
        time_step = (lista[2, 0] - lista[1, 0])
        if start != 0 or end != 0:
            listab = np.append(lista[:, 0:1], np.vstack(np.sum(lista[:, start:end + 1], axis=1)), axis=1)
            alist.append(get_col_max(time_step, listab, 1, starttime, endtime))
        else:
            alist.append(get_col_max(time_step, lista, col, starttime, endtime))
        mean_value.append(np.mean(lista[:, col]))

    rt = np.array(alist)
    mean_value = np.array(mean_value)
    rt = np.insert(rt, len(rt[0]), mean_value, axis=1)
    rt = rt[rt[:, 1].argsort()]

    plot_trends(filename_output, files, start, end, col, path_sim, sep, skip_rows)
    return rt


def read_data(filename):
    arr = []
    mylist = []
    with open(filename, 'r') as fp:
        arr = fp.readlines()
        for i in range(len(arr)):
            if '#' not in arr[i]:
                mylist.append([int(num_string) for num_string in arr[i].strip('\n').split()])
    return np.array(mylist)


def get_col_max(ts, anarray, col, starttime=0, endtime=float('inf')):
    mmin = max(0, starttime)
    mmax = min(anarray[-1, 0], endtime)
    tmp = anarray[(anarray[:, 0] >= mmin) * (anarray[:, 0] <= mmax)]

    if len(tmp) != 0:
        mymax = np.amax(tmp[:, col])  # get Peak Value

        final_value = anarray[-1:, col][0]
        idx_timestep = np.where(anarray[:, col] == mymax)[0][-1]  # get last index of timestep relative to mymax

        # this step can be done istead  to artificially force to get the last max occurrence if a max holds
        return [ts, np.size(anarray, 0), anarray[idx_timestep, 0], mymax, final_value]
    else:
        raise Exception('I can\'t get the correct Peak Value, Have you set the correct value of START_TIME_AG?')


def get_plot_trends_convergence_corr(filename_output, files, column, starttime, path_sim, name_analysis, sep, skip_rows):
    os.mknod(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))

    res_list = parse_files(filename_output, files, column, path_sim, sep, skip_rows, starttime=starttime)

    # plots pv values and time-to peak values
    # depends from the results of parse_files
    plot_peak_value(res_list, filename_output, path_sim, starttime=starttime)
    convergence_pv_tpv_fv(res_list, filename_output, path_sim, starttime=starttime)

    # calculates correlations and RMSE. Indipendent from the previous functions
    calculate_corr(filename_output, files, column, path_sim, sep, skip_rows)

    os.remove(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))
    os.mknod(os.path.join(path_sim, f'FINISHED_{name_analysis}.process'))


def plot_trends(filename_output, files, start, end, col, path_sim, sep, skip_rows):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for f in files:
        # lista = read_data(f)
        lista = pd.read_csv(f, sep=sep, skiprows=skip_rows).to_numpy()
        time_step = (lista[2, 0] - lista[1, 0])
        if start != 0 or end != 0:
            listab = np.append(lista[:, 0:1], np.vstack(np.sum(lista[:, start:end + 1], axis=1)), axis=1)
            ax.plot(listab[:, 0] / (3600 * 24), listab[:, 1], label=str(time_step))
        else:
            ax.plot(lista[:, 0] / (3600 * 24), lista[:, col], label=str(time_step))

    col = int(col) + 1
    ax.set(title=f"values of the column {col}", xlabel=f"time (days)", ylabel="entities")
    ax.legend()
    fig.savefig(os.path.join(path_sim, f'{filename_output}_trends.png'), format='png')


def convergence_calc(q_i, q_ii, mean_value):
    a = 0
    if q_ii != 0:
        a = abs(((q_ii - q_i) / q_ii) * 100)
    else:
        if mean_value != 0:
            a = abs(((q_ii - q_i) / mean_value) * 100)
    return a


# calculate the convergence of the Peak Value and Time-To-Peak value
def convergence_pv_tpv_fv(llist, dlabel, path_sim, starttime=0):
    my_funcs = np.frompyfunc(convergence_calc, 3, 1)
    idx = llist.argmax(axis=0)[1]  # get index of the row of the larger time step
    mean_value = llist[idx:, -1]  # get the mean value of the time series of the larger time step

    q_i_timetopv = llist[idx][2]  # get the timetoPV of the larger time step
    array_timeto_pv = llist[:, 2]
    f_array_timeto_pv = my_funcs(array_timeto_pv, [q_i_timetopv], mean_value)

    q_i_pv = llist[idx][3]  # get the PV of the larger time step
    array_pv = llist[:, 3]
    f_array_pv = my_funcs(array_pv, [q_i_pv], mean_value)

    q_i_fv = llist[idx][4]  # get the FV of the larger time step
    array_fv = llist[:, 4]
    f_array_fv = my_funcs(array_fv, [q_i_fv], mean_value)

    plot_convergence_pv_tpv(llist, f_array_timeto_pv, f_array_pv, f_array_fv, path_sim, starttime)


def calculate_corr(filename_output, files, col, path_sim, sep, skip_rows, start=0, end=0, starttime=0, endtime=float('inf')):
    time_step = 0
    alist = []
    listab = []
    xrange = np.array([])

    for f in files:
        # lista = read_data(f)
        lista = pd.read_csv(f, sep=sep, skiprows=skip_rows).to_numpy()
        time_step = (lista[2, 0] - lista[1, 0])
        if start != 0 or end != 0:
            listab = np.append(lista[:, 0:1], np.vstack(np.sum(lista[:, start:end + 1], axis=1)), axis=1)
            alist.append(get_col_max(time_step, listab, 1, starttime, endtime))
        else:
            alist.append(get_col_max(time_step, lista, col, starttime, endtime))
    rt = np.array(alist)
    rt2 = rt[rt[:, 0].argsort()]
    max_step = rt2[0, 0:2]
    xrange = np.arange(0, max_step[0] * max_step[1], max_step[0])
    i = 0
    flag = 0
    interp_list = np.array(np.vstack(xrange))
    for f in files:
        # lista = read_data(f)
        lista = pd.read_csv(f, sep=sep, skiprows=skip_rows).to_numpy()
        if max_step[1] == np.size(lista, 0):
            flag = i
        i += 1
        if start != 0 or end != 0:
            listab = np.append(lista[:, 0:1], np.vstack(np.sum(lista[:, start:end + 1], axis=1)), axis=1)
            interp_list = np.append(interp_list, np.vstack(np.interp(xrange, listab[:, 0], listab[:, 1])), axis=1)
        else:
            np.interp(xrange, lista[:, 0], lista[:, col])
            interp_list = np.append(interp_list, np.vstack(np.interp(xrange, lista[:, 0], lista[:, col])), axis=1)

    r = []
    rmse = []
    flag += 1
    for i in range(1, np.size(interp_list, 1)):
        r.append(np.corrcoef(interp_list[:, flag].T, interp_list[:, i].T)[0, 1])
        rmse.append(RMSE(interp_list[:, flag].T, interp_list[:, i].T))

    plot_rmse_pearsoncoeff(filename_output, rt, r, rmse, path_sim)


def RMSE(predictions, targets):
    return np.sqrt(((predictions - targets).astype('double') ** 2).mean())


def save_files(files: list, path: str):
    fs = FileSystemStorage()

    list_files_uploaded = []
    for f in files:
        fs.save(os.path.join(path, f.name), f)
        list_files_uploaded.append(os.path.join(path, f.name))

    return natsorted(list_files_uploaded)


def existence_and_unique_analysis(csv_files, sep: str, skip_rows: int):
    if not check_number_rows_csv(csv_files):
        return [-1]  # the number of lines in the files is different
    else:
        df_tmp = pd.read_csv(csv_files[0], sep=sep, skiprows=skip_rows, header=None, engine='c', na_filter=False, low_memory=False)
        n_col = len(df_tmp.axes[1])
        if n_col == 1:
            return [-2]  # the separator character is not correct
        sd_list = []
        mean_list = []
        list_of_dataframes = []
        for filename in csv_files:
            list_of_dataframes.append(
                pd.read_csv(filename, sep=sep, skiprows=skip_rows, header=None, engine='c', na_filter=False, low_memory=False))

        merged_df = pd.concat(list_of_dataframes, axis=1, sort=False, ignore_index=True)
        merged_df = merged_df.apply(pd.to_numeric, errors='coerce')

        for i in range(0, n_col):
            list_indices = [*range(i, merged_df.shape[1], n_col)]
            sd_list.append(merged_df.iloc[:, list_indices].std(axis=1))
            mean_list.append(merged_df.iloc[:, list_indices].mean(axis=1))

        '''
        sd_list1 = []
        mean_list1 = []
        for ii in range(len(merged_df)):
            for jj in np.arange(0, n_col):
                tmp = []
                for xx in range(0, len(list_of_dataframes)):
                    tmp.append(merged_df.iloc[ii, jj + (n_col * xx)])
                sd_list1.append(np.array(tmp).std())
                mean_list1.append(np.array(tmp).mean())
        '''

        tmp_max = []

        for array in sd_list:
            tmp_max.append(array.max())

        if max(tmp_max) == 0:  # the files are the same
            return [0]
        else:  # the files are NOT the same
            index, col, val = get_row_col(sd_list)
            # index+1 because the dataframe starts at row 0
            return [1, index+1, col, val]


def run_smoothness_analysis(ll, arr_t, k_elem, name_analysis: str, path_sim: str, col: str):
    os.mknod(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))

    new_array = rolling_window(np.array(ll), (k_elem * 2) + 1)
    array_result = np.zeros(len(ll))
    new_array = new_array.astype(np.float64)

    i = k_elem

    for l_list in new_array:
        diff_array = np.diff(l_list)
        mean = np.abs(np.mean(diff_array))
        if mean != 0:
            # ddof is Delta Degrees of Freedom, 1 means the the standard deviation is calculate on sample
            value = np.std(diff_array / mean, ddof=1)
            array_result[i] = value
        else:
            array_result[i] = 0
        i += 1
    plot_smoothness_analysis(arr_t, array_result, path_sim, col)
    os.remove(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))
    os.mknod(os.path.join(path_sim, f'FINISHED_{name_analysis}.process'))


def plot_smoothness_analysis(axis_x, arr_result, path_sim, col):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    col = int(col) + 1
    ax.set(title='Smoothness Analysis', xlabel="time (seconds)", ylabel=f'values of the column {col}')
    ax.plot(axis_x, np.array(arr_result))
    fig.savefig(os.path.join(path_sim, 'Smoothness_Analysis.png'), format='png')


def plot_convergence_pv_tpv(llist, f_array_timeto_pv, f_array_pv, f_array_fv, path_sim, starttime):
    fig = plt.figure()

    ax = fig.add_subplot(311)
    ax.set(title='Time-to-PV - Convergence')

    ax.plot(llist[:, 1], f_array_timeto_pv, 'bo-.', color='red', label='Time to Peak Value')
    ax.relim()
    # update ax.viewLim using the new dataLim
    ax.autoscale_view()
    ax.legend()

    bx = fig.add_subplot(312)
    bx.set(title='PV - Convergence')

    bx.plot(llist[:, 1], f_array_pv, 'ro-.', color='blue',  label=' Peak Value')
    bx.relim()
    # update ax.viewLim using the new dataLim
    bx.autoscale_view()
    bx.legend()

    cx = fig.add_subplot(313)
    cx.set(title='FV - Convergence')

    cx.plot(llist[:, 1], f_array_fv, 'ro-.', color='green', label=' Final Value')
    cx.relim()
    # update ax.viewLim using the new dataLim
    cx.autoscale_view()
    cx.legend()

    fig.text(0.5, 0.004, '# iterations', ha='center')
    fig.text(0.95, 0.5, 'Convergence estimation (%)', va='center', rotation='vertical')

    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.7)
    fig.savefig(os.path.join(path_sim, '%s.png' % 'behavior_and_variation_PV'), format='png')


def plot_peak_value(dlist, dlabel, path_sim, starttime=0, endtime=float('inf')):
    fig = plt.figure()

    ax = fig.add_subplot(211)
    ax.set(title=str(dlabel) + ' - Peak Value', xlabel="# iterations", ylabel="Peak Value")
    ax.plot(dlist[:, 1], dlist[:, 3], 'ro-.', label=' Peak Value')
    ax.relim()
    # update ax.viewLim using the new dataLim
    ax.autoscale_view()
    ax.legend()

    bx = fig.add_subplot(212)
    bx.set(title=str(dlabel) + ' - Time to PV', xlabel="# iterations", ylabel="Time to PV (secs)")
    bx.plot(dlist[:, 1], dlist[:, 2] + starttime, 'bo-.', label=' Time to Peak Value')
    bx.relim()
    # update ax.viewLim using the new dataLim
    bx.autoscale_view()
    bx.legend()

    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.7)
    # plt.show()
    fig.savefig(os.path.join(path_sim, '%s_peak_value_time_to_pv.png' % dlabel), format='png')


def plot_rmse_pearsoncoeff(filename_output, rt, r, rmse, path_sim):
    fig = plt.figure()
    ax = fig.add_subplot(211)
    bx = fig.add_subplot(212)
    ax.set(title='Pearson Correlation coefficent', xlabel="# of iterations", ylabel="PCC")
    bx.set(title='RMSE', xlabel="# of iterations", ylabel="RMSE")

    toplot = np.array([rt[:, 1], r]).T
    toplot = toplot[toplot[:, 0].argsort()]
    ax.plot(toplot[:-1, 0], toplot[:-1, 1], 'or-.', label='Pearson Corr Coeff')
    ax.relim()
    # update ax.viewLim using the new dataLim
    ax.autoscale_view()
    ax.legend()

    toplot = np.array([rt[:, 1], rmse]).T
    toplot = toplot[toplot[:, 0].argsort()]
    bx.plot(toplot[:-1, 0], toplot[:-1, 1], 'og-.', label='RMSE')
    bx.relim()
    # update ax.viewLim using the new dataLim
    bx.autoscale_view()
    bx.legend()
    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.7)
    # plt.show()
    fig.savefig(os.path.join(path_sim, '%s_pearson_corr_RMSE.png' % filename_output), format='png')


# SOBOL ANALYSIS
def run_sobol_analysis(df_params, skip_values, name_analysis: str, path_sim: str, y=None, n_comb=None):
    os.mknod(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))

    # Number of parameters to sample
    parameter_count = df_params.shape[0]

    names = df_params.iloc[:, 0].tolist()

    # Define the model inputs
    problem = {
        'num_vars': parameter_count,
        'names': names,
        'bounds': df_params.iloc[:, 1:3].values.tolist(),
        'dists': df_params.iloc[:, 3].values.tolist()
    }

    if y is not None:
        # Perform analysis
        s_i = sobol.analyze(problem, y)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(title='Sobol Analysis')
        ax.bar(names, s_i['S1'])
        fig.savefig(os.path.join(path_sim, 'Sobol_Analysis.png'), format='png')
        os.remove(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))
        os.mknod(os.path.join(path_sim, f'FINISHED_{name_analysis}.process'))
    else:
        # Number of samples to draw for each parameter
        sample_count = int(n_comb)
        # Generate samples
        param_values = saltelli.sample(problem, sample_count, skip_values=skip_values)
        os.remove(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))
        os.mknod(os.path.join(path_sim, f'FINISHED_{name_analysis}.process'))
        return param_values, names


# LHS--PRCC TOOLS ANALYSIS
def run_lhs_analysis(df_param: dict, n_samples: int, seed: int, iterations: int, path_sim: str, name_analysis: str):
    os.mknod(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))

    input_space = list(df_param.values())
    space = Space(input_space)
    lhs = Lhs(criterion="maximin", iterations=iterations)
    matrix = pd.DataFrame(lhs.generate(dimensions=space.dimensions, n_samples=n_samples, random_state=seed))
    matrix.columns = list(df_param.keys())

    os.remove(os.path.join(path_sim, f'STARTED_{name_analysis}.process'))
    os.mknod(os.path.join(path_sim, f'FINISHED_{name_analysis}.process'))

    return matrix


def run_prcc_analysis(lhs_matrix: pd.DataFrame, matrix_output: pd.DataFrame, path_sim: str, request):
    os.mknod(os.path.join(path_sim, f"STARTED_{request.POST['name_analysis']}.process"))
    # get column time
    x_time = matrix_output.pop('time')
    matrix_output = matrix_output.T

    if len(lhs_matrix) == matrix_output.shape[0]:
        # add Dummy value in LHS matrix
        lhs = Lhs(criterion="maximin")
        space = Space([(0., 1.)])
        dummy_values = lhs.generate(dimensions=space.dimensions, n_samples=len(lhs_matrix))
        lhs_matrix['Dummy_value'] = list(np.concatenate(dummy_values).flat)

        time_points = list(range(0, matrix_output.shape[1], int(request.POST['step_time_points'])))
        x_time = x_time.iloc[time_points,]

        matrix_output = matrix_output.iloc[:, time_points]
        matrix_output.columns = [f'time_{str(x)}' for x in range(matrix_output.shape[1])]
        # reset index to avoid problems with concat
        lhs_matrix.reset_index(drop=True, inplace=True)
        matrix_output.reset_index(drop=True, inplace=True)
        # define the columns for combinations
        col_time = [[], []]
        col_time[0] = list(lhs_matrix.columns)
        col_time[1] = list(matrix_output.columns)

        df_lhs_output = pd.concat([lhs_matrix, matrix_output], axis=1)

        output = pg.pairwise_corr(data=df_lhs_output, columns=col_time, method='spearman')
        output.to_csv(os.path.join(path_sim, 'prcc.csv'))
        name_pdf_file, name_time_corr_file = plot_prcc(output, x_time, path_sim,
                                                       float(request.POST['threshold_pvalue']))

        link_plot = get_media_link(name_pdf_file, request.scheme, request.get_host())
        link_time_corr = get_media_link(name_time_corr_file, request.scheme, request.get_host())

        response = JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                 'mess': '', 'link_plot': link_plot, 'link_time_corr': link_time_corr})

        os.remove(os.path.join(path_sim, f"STARTED_{request.POST['name_analysis']}.process"))
        os.mknod(os.path.join(path_sim, f"FINISHED_{request.POST['name_analysis']}.process"))

    else:
        shutil.rmtree(path_sim)
        mess = 'The number of rows of LHS matrix and the' \
               'number of columns of File to Analyze are different'
        response = JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!', 'mess': mess})

    return response


def run_prcc_specific_ts(lhs_matrix: pd.DataFrame, output_matrix: pd.DataFrame, path_sim: str, request):
    os.mknod(os.path.join(path_sim, f"STARTED_{request.POST['name_analysis']}.process"))

    # remove time column
    matrix_output = output_matrix[output_matrix['time'] == int(request.POST['timeStep'])].T.iloc[1:].squeeze()
    lhs_ranked = rankdata(lhs_matrix, method='ordinal', axis=0)
    output_ranked = rankdata(matrix_output, method='ordinal')
    name_pdf_file = os.path.join(path_sim, 'plot_prcc_specific_ts.pdf')
    flag = False

    # reset index to avoid problems with concat
    lhs_matrix.reset_index(drop=True, inplace=True)
    matrix_output.reset_index(drop=True, inplace=True)
    df_lhs_output = pd.concat([lhs_matrix, matrix_output], axis=1)
    col = list(df_lhs_output.columns)
    col[2] = 'time_0'
    df_lhs_output.columns = col
    output = pg.pairwise_corr(data=df_lhs_output, columns=list(col), method='spearman')

    with PdfPages(name_pdf_file) as pdf:
        for i in range(0, lhs_ranked.shape[1]):  # loop over parameter
            tmp = np.delete(lhs_ranked, i, axis=1)
            z_matrix = np.insert(tmp, 0, np.ones(len(tmp)), axis=1)

            reg = LinearRegression().fit(z_matrix, output_ranked)
            prediction = reg.predict(z_matrix)
            residual_output_ranked = (output_ranked - prediction)

            reg1 = LinearRegression().fit(z_matrix, lhs_ranked[:, i])
            prediction1 = reg1.predict(z_matrix)
            residual_lhs_ranked = (lhs_ranked[:, i] - prediction1)

            if stats.pearsonr(residual_lhs_ranked, residual_output_ranked)[1] < float(request.POST['pvalue']):
                flag = True
                fig, ax = plt.subplots()

                ax.scatter(residual_output_ranked, residual_lhs_ranked)
                ax.legend([lhs_matrix.columns[i]])
                prcc_val = output[(output['X'] == lhs_matrix.columns[i]) & (output['Y'] == 'time_0')]['r'].iloc[0]
                plt.title(f"Time Step: {request.POST['timeStep']}\n PRCC: {round(prcc_val, 4)}")
                plt.xlabel(lhs_matrix.columns[i])
                plt.ylabel(f"column: {str(int(request.POST['col']))}")
                pdf.savefig(fig)
                plt.close(fig)

    os.remove(os.path.join(path_sim, f"STARTED_{request.POST['name_analysis']}.process"))
    os.mknod(os.path.join(path_sim, f"FINISHED_{request.POST['name_analysis']}.process"))

    return name_pdf_file, flag


def plot_prcc(df: pd.DataFrame, x_time, path_sim: str, threshold: float = 0.01):
    params = df.iloc[:, 0].unique()
    dummy_value = df[df['X'] == params[-1]].loc[:, 'r']
    params = np.delete(params, -1)  # delete Dummy_value
    # this variable is a dictonary where the keys are parameters(param variable) and values are time and p-value
    dict_time_corr = dict()
    name_pdf_file = os.path.join(path_sim, 'plot_prcc_overtime.pdf')
    name_time_corr_file = os.path.join(path_sim, 'time_corr.json')
    with PdfPages(name_pdf_file) as pdf:
        for param in params:
            x_time_tmp = x_time.copy()
            df_tmp = df[df['X'] == param]
            x_time_tmp.reset_index(drop=True, inplace=True)
            df_tmp.reset_index(drop=True, inplace=True)
            time_value = [int(x.split('_')[1]) for x in df_tmp.loc[:, 'Y']]
            x_time_tmp = x_time_tmp[time_value]
            x = list(x_time_tmp)
            prcc_value = df_tmp.loc[:, 'r']
            p_value = df_tmp.loc[:, 'p-unc']
            x_time_tmp.reset_index(drop=True, inplace=True)
            df_time_corr = pd.concat([x_time_tmp, p_value], axis=1, sort=False, ignore_index=True)
            df_time_corr = df_time_corr.loc[df_time_corr[1] < threshold]
            if not len(df_time_corr.index) == 0:
                dict_time_corr[param] = dict()
                dict_time_corr[param]['time'] = list(df_time_corr.to_dict().values())[0]
                dict_time_corr[param]['p-val'] = list(df_time_corr.to_dict().values())[1]

            fig, ax = plt.subplots()
            ax.plot(x, prcc_value)
            ax.plot(x, dummy_value, color='red')
            ax.fill_between(x, 0, 1, where=p_value < threshold, color='gray', alpha=0.5,
                            transform=ax.get_xaxis_transform())
            plt.ylabel('PRCC')
            plt.xlabel('time(secs)')
            ax.legend([param, 'DUMMY', f'Significant(p<{threshold})'])
            pdf.savefig(fig)
            plt.close(fig)

    with open(name_time_corr_file, 'w') as f:
        json.dump(dict_time_corr, f, indent=2)

    return name_pdf_file, name_time_corr_file


def get_media_link(path_file: str, scheme: str, host: str):
    path_out = path_file.split('/')[-6:]
    out = '/'.join(path_out)

    return scheme + '://' + host + '/' + out


def get_row_col(ll: np.array):
    """
    this function is used in Uniqueness analysis and allow to get value,
     row and column of the first element different from zero, when input files are different.
    """

    index = []
    column = 0
    flag = True

    while flag:
        index = ll[column].to_numpy().nonzero()
        if len(index[0]) != 0:
            flag = False
        column += 1

    return ll[column-1][index[0]].index[0], column, ll[column-1][index[0]].values[0]


def get_correct_col_value(col: int):
    if col > 1:
        col = col - 1
    else:
        col = -1
    return col


def is_columns_object(list_df: [], sep: str, type_analysis: str = 'None', skip_rows: int = None, columns_to_drop: list = None):
    flag = False
    i = 0
    while not flag and i < len(list_df):
        df = pd.read_csv(list_df[i], sep=sep, skiprows=skip_rows, comment='#')
        if columns_to_drop is not None:
            df.drop(columns_to_drop, axis=1, inplace=True)
        i = i + 1
        if not df.select_dtypes(exclude=['int64', 'float64', 'int32', 'float32']).empty:
            if not 'sobol_generates_samples' == type_analysis:
                flag = True

    return flag
