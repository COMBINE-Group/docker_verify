import logging
import os
import shutil
from pathlib import Path
from time import localtime, strftime

from django.http import JsonResponse
from scipy import special
import numpy as np
import matplotlib.pyplot as plt

def copy_files(path, name_files):
    for name in name_files:
        shutil.copy2(os.path.join(path, name), name)


def create_simulation_folder(path, username, name_analysis):
    # [START] it check if simulation folder of user exists
    dir_simulation_user = os.path.join(path, username)

    if not os.path.isdir(dir_simulation_user):
        os.makedirs(dir_simulation_user)
    # [END]

    os.chdir(dir_simulation_user)

    simulation_id = name_analysis + strftime("%Y-%m-%d_%H:%M:%S", localtime())

    if not os.path.isdir(simulation_id):
        os.makedirs(simulation_id)
    else:
        # tornare errore perche' gia' esiste, allora bloccare tutto
        return JsonResponse(
            {'status': 0, 'type': 'error', 'title': 'Error!', 'mess': 'There was a problem during execution!'})

    os.chdir(simulation_id)


def check_status_simulation(base_dir, path, username, name_analysis=''):
    dir_simulation_user = os.path.join(path, username)

    if not os.path.isdir(dir_simulation_user):
        return JsonResponse({'status': 0, 'type': 'warning', 'title': 'Done!', 'mess': 'No simulation found!'})
    else:
        # html = ''
        html_s = ''
        html_f = ''
        started_string = 'STARTED'+name_analysis+'.process'
        finished_string = 'FINISHED'+name_analysis+'.process'

        for filename in Path(dir_simulation_user).rglob('*.process'):
            if filename.parts[-1] == started_string:
                html_s += '<option value="">' + filename.parts[-2] + '</option>'
            elif filename.parts[-1] == finished_string:
                html_f += '<option value="' + filename.parts[-2] + '">' + filename.parts[-2] + '</option>'

        html_s = '<optgroup label="Started">' + html_s + '</optgroup>'
        html_f = '<optgroup label="Finished">' + html_f + '</optgroup>'

        html = html_s + html_f

        # set BASE_DIR_UISSMS like a current position
        os.chdir(base_dir)

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


def parse_files(filename_output, files, col, start=0, end=0, starttime=0, endtime=float('inf')):
    time_step = 0
    alist = []
    mean_value = []

    for f in files:
        lista = read_data(f)
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

    # plot_trends(filename_output, files, start, end, col)
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

        myline = (np.argmax(tmp[:, col]))
        final_value = anarray[-1:, col][0]
        idx_timestep = np.where(anarray[:, col] == mymax)[0][-1]  # get last index of timestep relative to mymax

        # this step can be done istead  to artificially force to get the last max occurrence if a max holds
        return [ts, np.size(anarray, 0), anarray[idx_timestep, 0], mymax, final_value]
    else:
        raise Exception('I can\'t get the correct Peak Value, Have you set the correct value of START_TIME_AG?')


def run_plot_par(filename_output, files, column, starttime):
    with open('STARTED.process', 'w') as fp:
        pass
    res_list = parse_files(filename_output, files, column, starttime=starttime)

    # plots pv values and time-to peak values
    # depends from the results of parse_files
    plot_PV(res_list, filename_output, starttime=starttime)
    new_function(res_list, filename_output, starttime=starttime)

    # calculates correlations and RMSE. Indipendent from the previous functions
    calculate_corr(filename_output, files, column)

    os.remove('STARTED.process')
    with open('FINISHED.process', 'w') as fp:
        pass


def plot_trends(filename_output, files, start, end, col):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set(title=filename_output, xlabel="time (days)", ylabel="entities")

    for f in files:
        lista = read_data(f)
        time_step = (lista[2, 0] - lista[1, 0])
        if start != 0 or end != 0:
            listab = np.append(lista[:, 0:1], np.vstack(np.sum(lista[:, start:end + 1], axis=1)), axis=1)
            ax.plot(listab[:, 0] / (3600 * 24), listab[:, 1], label=str(time_step / 3600) + ' hrs')
        else:
            ax.plot(lista[:, 0] / (3600 * 24), lista[:, col], label=str(time_step / 3600) + ' hrs')

    ax.legend()
    fig.savefig(os.path.join(os.getcwd(), '%s_trends.png' % filename_output))

# LHS--PRCC TOOLS ANALYSIS
