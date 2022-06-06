import pandas as pd

category_to_funding = {'Formal Clinic':'Public',
                       'Informal Clinic':'Private'}

category_to_category2 = {'Formal Clinic':'Clinic',
                        'Informal Clinic':'Clinic'}


def get_full_results(param_dict,site,speed_walking, summary_stat = 'mean'):

    full_results = pd.read_csv(param_dict[site]['results_loc'] + 'With Costs/1/Facility Results.csv')
    facilities_classification = pd.read_csv(param_dict[site]['data_loc'] + 'hospital_public_private.csv')

    dwelling_facility_distances = pd.read_csv(param_dict[site]['data_loc'] + 'dwellings_facility_loc.csv')
    dwelling_facility_distances['Travel Time'] = (dwelling_facility_distances['Total Distance'] / 1000) / speed_walking

    funding = []
    category = []

    for i,r in full_results.iterrows():
        if r['Category'] == 'Hospital':
            if site in ['SA', 'ID']:
                funding.append(facilities_classification[facilities_classification['facility_id'] == r['facility_id']]['Funding'].values[0])
            else:
                funding.append(facilities_classification[facilities_classification['hfc_id'] == r['hfc_id']]['Funding'].values[0])
            category.append((r['Category']))
        else:
            funding.append(category_to_funding[r['Category']])
            category.append(category_to_category2[r['Category']])

    full_results['Funding'] = funding
    full_results['Facility Type'] = category

    if summary_stat == 'mean':

        if site in ['SA', 'ID']:
            tt_mean = dwelling_facility_distances[dwelling_facility_distances['Facility ID'].isin(list(full_results['facility_id']))].groupby('Facility ID')['Travel Time'].mean()
        else:
            tt_mean = dwelling_facility_distances[dwelling_facility_distances['Facility ID'].isin(list(full_results['hfc_id']))].groupby('Facility ID')['Travel Time'].mean()
    else:
        if site in ['SA', 'ID']:
            tt_mean = dwelling_facility_distances[dwelling_facility_distances['Facility ID'].isin(list(full_results['facility_id']))].groupby('Facility ID')['Travel Time'].median()
        else:
            tt_mean = dwelling_facility_distances[dwelling_facility_distances['Facility ID'].isin(list(full_results['hfc_id']))].groupby('Facility ID')['Travel Time'].median()

    if site in ['SA', 'ID']:
        full_results['Travel Time Mean'] = full_results['facility_id'].map(tt_mean.to_dict())
    else:
        full_results['Travel Time Mean'] = full_results['hfc_id'].map(tt_mean.to_dict())

    return full_results

def grouped_by_chart(group_by,ylabel, summary_stat, output_file, plotTitle = '',isStacked = False,pltZeroLine = False, side_by_side = True):
    iterables = [['Clinic', 'Hospital'], ['Private', 'Public']]
    catch_results = pd.DataFrame(index=pd.MultiIndex.from_product(iterables, names=["Type", "Funding"]))

    if side_by_side:
        fig, ax = plt.subplots(1,4, figsize=(30, 6))
        across = 0
        for site in ['KO', 'VI', 'SA', 'ID']:

            full_results = get_full_results(param_dict, site, summary_stat)
            if pltZeroLine:
                full_results.groupby(['Facility Type', 'Funding'])[group_by].mean().unstack().plot(ax=ax[across],
                                                                                                   kind='bar', rot=0,
                                                                                                   color=colour_to_plot,
                                                                                                   stacked = isStacked).axhline(y=1.5, c = 'black', linestyle = '--')
            else:
                full_results.groupby(['Facility Type', 'Funding'])[group_by].mean().unstack().plot(ax=ax[across],
                                                                                                   kind='bar', rot=0,
                                                                                                   color=colour_to_plot,
                                                                                                   stacked = isStacked)
            catch_results[site] = full_results.groupby(['Facility Type','Funding'])[group_by].mean().values
            ax[across].set_title(param_dict[site]['plt_label'])
            if across > 0:
                ax[across].set_ylabel('')
            else:
                ax[across].set_ylabel(ylabel)
            #ax[across].set_ylabel(ylabel)
            across += 1
        ax[0].get_legend().remove()
        ax[1].get_legend().remove()
        ax[2].get_legend().remove()
        if group_by == 'Attractiveness Score':
            ax[3].legend(bbox_to_anchor = (1, 1), fontsize = 20)
        else:
            ax[3].legend(bbox_to_anchor=(1, 0.15), fontsize=20)
        plt.suptitle(plotTitle, fontsize=24)
        plt.tight_layout()
        fig.savefig(figures + output_file +'.png')
        plt.show()

    else:
        fig, ax = plt.subplots(2, 2, figsize=(12, 9))
        across = 0
        down = 0

        for site in ['KO', 'VI', 'SA', 'ID']:

            full_results = get_full_results(param_dict, site, summary_stat)
            if pltZeroLine:
                full_results.groupby(['Facility Type', 'Funding'])[group_by].mean().unstack().plot(ax=ax[across, down],
                                                                                                   kind='bar', rot=0,
                                                                                                   color=colour_to_plot,
                                                                                                   stacked=isStacked).axhline(
                    y=1.5, c='black', linestyle='--')
            else:
                full_results.groupby(['Facility Type', 'Funding'])[group_by].mean().unstack().plot(ax=ax[across, down],
                                                                                                   kind='bar', rot=0,
                                                                                                   color=colour_to_plot,
                                                                                                   stacked=isStacked)
            catch_results[site] = full_results.groupby(['Facility Type', 'Funding'])[group_by].mean().values
            ax[across, down].set_title(param_dict[site]['plt_label'])
            if across == 0:
                ax[across, down].set_xlabel('')
            ax[across, down].set_ylabel(ylabel)
            down += 1
            if down > 1:
                down = 0
                across += 1
        ax[0, 0].get_legend().remove()
        ax[0, 1].get_legend().remove()
        ax[1, 0].get_legend().remove()
        ax[1, 1].legend(bbox_to_anchor=(1, 0.15))
        plt.suptitle(plotTitle)
        plt.tight_layout()
        fig.savefig(figures + output_file + '.png')
        plt.show()

    return catch_results


def scatter_plots(x_axis, y_axis, x_label, y_label, output_file, summary_stat):
    catch_persons = pd.DataFrame(index=['KO', 'VI', 'SA', 'ID'], columns=['Pearson Coefficent'])

    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    across = 0
    down = 0

    for site in ['KO', 'VI', 'SA', 'ID']:

        full_results = get_full_results(param_dict, site, summary_stat)

        for i, r in full_results.iterrows():
            x = r[x_axis]
            y = r[y_axis]
            # if r['Funding'] == 'Public':
            #     col_to_plot = 'green'
            # else:
            #     col_to_plot = 'red'
            col_to_plot = funding_colours[r['Funding']]

            if r['Facility Type'] == 'Hospital':
                marker_to_plot = "v"
            else:
                marker_to_plot = "*"
            ax[across, down].scatter(x, y, s=50, c=col_to_plot, marker=marker_to_plot, alpha=0.8)

        ax[across, down].set_title(param_dict[site]['plt_label'])
        if across > 0:
            ax[across, down].set_xlabel(x_label)
        ax[across, down].set_ylabel(y_label)
        down += 1
        if down > 1:
            down = 0
            across += 1

        catch_persons.loc[site] = full_results[[x_axis, y_axis]].corr('pearson').loc[x_axis][y_axis]
    plt.tight_layout()
    fig.savefig(figures + output_file + '.png')
    plt.show()

    return catch_persons

def plt_histograms(feature,output_file, numBins, bigRound = True):

    summary_stats = pd.DataFrame(columns = ['slum','type','funding','count','sum','mean','std dev'])
    df_i = 0
    for site in ['KO', 'VI', 'SA', 'ID']:
        full_results = get_full_results(param_dict, site)

        if bigRound:
            axis_range = abs(int(full_results[feature].min())) + abs(int(math.ceil(full_results[feature].max())))
            bin_width = axis_range / numBins
            buffer = bin_width * 1.25

            min_x_axis = int(full_results[feature].min()) - buffer
            max_x_axis = int(math.ceil(full_results[feature].max())) + buffer

        else:
            min_x_axis = int(full_results[feature].min())
            max_x_axis = int(math.ceil(full_results[feature].max()))

        fig, ax = plt.subplots(2, figsize=(12, 6))

        ax_ind = 0

        for type in ['Clinic', 'Hospital']:

            clinics = full_results[full_results['Facility Type'] == type]
            ax[ax_ind].set_xlim(min_x_axis, max_x_axis)
            for funding in ['Public', 'Private']:
                hist_to_plot = clinics[clinics['Funding'] == funding]
                row_to_add = [site, type, funding, hist_to_plot.shape[0],hist_to_plot[feature].sum(),hist_to_plot[feature].mean(), hist_to_plot[feature].std()]
                summary_stats.loc[df_i] = row_to_add
                df_i += 1
                hist_to_plot[feature].hist(ax=ax[ax_ind], color=funding_colours[funding], alpha=0.7, bins = numBins, range = (min_x_axis,max_x_axis))
            ax[ax_ind].set_title(type, fontsize = 14)
            ax_ind += 1
        plt.suptitle(param_dict[site]['plt_hist_label'], fontsize = 16)
        plt.tight_layout()
        fig.savefig(figures + output_file + '_' + site + '.png')
        plt.show()

    return summary_stats