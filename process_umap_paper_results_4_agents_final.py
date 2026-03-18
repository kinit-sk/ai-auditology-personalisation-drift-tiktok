# -*- coding: utf-8 -*-

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import os
import math

path_results = r'path\to\data\dir'
results_file = 'UMAP_data_US_politics_4_agents_zenodo.csv'
path_figures = r'path\to\figures\dir'


# size of analysis time bin in minutes
minute_interval = 30

data_trim_minutes = 1000

        
all_data = pd.read_csv(os.path.join(path_results,results_file))

# overall statistics
stats = {}

len_run = len(all_data)
num_watch = (all_data.video_action_watch == True).sum()
num_like = (all_data.video_action_like == True).sum()
num_bookmark = (all_data.video_action_bookmark == True).sum()


stats['len_run'] = len_run
stats['num_watch'] = num_watch
stats['num_like'] = num_like
stats['num_bookmark'] = num_bookmark
stats['percentage_watch'] = (num_watch/len_run)*100
stats['percentage_like'] = (num_like/len_run)*100
stats['percentage_bookmark'] = (num_bookmark/len_run)*100

# convert to datetime
all_data['video_time_watch_loop_start'] = pd.to_datetime(all_data['video_time_watch_loop_start'],unit='s')

unique_topics = list(all_data['topic'].unique())
unique_agents = list(all_data['agent_id'].unique())
unique_stances = list(all_data['stance'].unique())

# BETWEEN TOPIC ANALYSIS

agents_analysis_data = {}

for topic in unique_topics:
    
    # get data for only one topic
    topic_data = all_data[all_data['topic']==topic]
    
    # select only one user and one run
    unique_topic_agents = list(topic_data['agent_id'].unique())
    
    for agent in unique_topic_agents:
        
        agent_data = topic_data[topic_data['agent_id']==agent]
        
        # NOTE: agent stance will allways == "indifferent"
        agent_stance = list(agent_data['stance'].unique())[0]
        
        # log agent settings
        agents_analysis_data[agent] = {'topic':topic,'stance':agent_stance}
        
        unique_topic_agent_runs = list(agent_data['run_id'].unique())
        
        agent_runs = []
        
        for r in range(len(unique_topic_agent_runs)):
            
            run = unique_topic_agent_runs[r]
            
            run_data = agent_data[agent_data['run_id']==run]           
            
            if r==0:
                
                # calculate elapsed time from the start of the run
                start = run_data['video_time_watch_loop_start'].min()
                run_data['elapsed'] = run_data['video_time_watch_loop_start'] - start

                # elapsed_total column, time from the very first video
                run_data['elapsed_total'] = run_data['elapsed']
                
                # max_elapsed_previous marks the time we should start counting total elapsed time at the next run
                max_elapsed_previous = run_data['elapsed_total'].max()
                
                run_data['day_id'] = r
                
                agent_runs.append(run_data)
                
            else:
                
                # calculate elapsed time from the start of the run
                start = run_data['video_time_watch_loop_start'].min()
                run_data['elapsed'] = run_data['video_time_watch_loop_start'] - start

                run_data['elapsed_total'] = run_data['elapsed'] + max_elapsed_previous
                
                # max_elapsed_previous marks the time we should start counting total elapsed time at the next run
                max_elapsed_previous = run_data['elapsed_total'].max()
                
                run_data['day_id'] = r
                
                agent_runs.append(run_data)
                
        # concatenate all runs for every agent for given topic
        agent_runs_concat = pd.concat(agent_runs)
        
        # DEFINE BINS for elapsed total
        total_time_elapsed = agent_runs_concat['elapsed_total'].max()
        total_time_elapsed_minutes = int(total_time_elapsed.total_seconds()/60)
        # number of 10 minute intervals (COULD BE SET UP AS VARIABLE!!!)
        total_intervals = math.ceil(total_time_elapsed_minutes/minute_interval) + 1

        # construct the bins

        total_bins = []

        for i in range(total_intervals):
            
            total_bins.append(pd.Timedelta(minutes = i*minute_interval))
            
        # calculate total bins for concatenated dataframe
        agent_runs_concat['elapsed_total_bin'] = pd.cut(agent_runs_concat['elapsed_total'], total_bins, right=False)
        
        # cut culumns that we dont need
        agent_runs_concat = agent_runs_concat[['video_action_watch','video_time_duration','elapsed_total_bin','elapsed_total','day_id','predicted_topic_match','predicted_stance_match','predicted_topic', 'predicted_stance']]
        
        agents_analysis_data[agent]['data'] = agent_runs_concat
        
        # aggregate data using created time bins
        
        # aggeragete video_action_watch
        
        # cast boolean values to float
        agent_runs_concat['video_action_watch'] = agent_runs_concat['video_action_watch'].astype(float)
        agent_runs_concat['predicted_topic_match'] = agent_runs_concat['predicted_topic_match'].astype(float)
        agent_runs_concat['predicted_stance_match'] = agent_runs_concat['predicted_stance_match'].astype(float)

        
        
        
        # sum across individual bins
        agent_runs_concat_agg_bins = agent_runs_concat[['video_action_watch','elapsed_total_bin']].groupby(['elapsed_total_bin']).sum()
        # WE ULTIMATELLY NEED PERCENTAGES AT THIS STAGE!!!
        # for every bin we need to sum the occurences of watch events and divide by number of interactions in this bin
        agent_runs_concat_agg_bins['bin_count'] = agent_runs_concat[['video_action_watch','elapsed_total_bin']].groupby(['elapsed_total_bin']).count()['video_action_watch']
        
        
        # RQ 1 analysis
        # count number of topic videos in time bin
        # count number of cooking videos in time bin
        # using 'bin_count' we can then calculate the percentages
        # NOTE: when no topic is present error arises that needs to be catched by inserting zeroes in the column
        try:
                        
            agent_runs_concat_agg_bins['predicted_topic_count'] = agent_runs_concat[['predicted_topic','elapsed_total_bin']].groupby(['elapsed_total_bin']).value_counts().unstack(fill_value=0).loc[:,topic].tolist()
            
        except:
            
            agent_runs_concat_agg_bins['predicted_topic_count'] = 0
            
        try:
            
            agent_runs_concat_agg_bins['predicted_topic_count_random'] = agent_runs_concat[['predicted_topic','elapsed_total_bin']].groupby(['elapsed_total_bin']).value_counts().unstack(fill_value=0).loc[:,'random'].tolist()
            
        except:
            
            agent_runs_concat_agg_bins['predicted_topic_count_random'] = 0
            
            
        # RQ 2 analysis
        # first calculate total number of videos where agent topic = predicted topic (column predicted_topic_match)
        # then calculate total number of videos where (agent topic = predicted topic) and (stance = support)
        # then calculate total number of videos where (agent topic = predicted topic) and (stance = oppose) 
        agent_runs_concat_agg_bins['predicted_topic_match_count'] = agent_runs_concat[['predicted_topic_match','elapsed_total_bin']].groupby(['elapsed_total_bin']).sum()
        
        agent_runs_concat['predicted_stance_support'] = 0
        agent_runs_concat.loc[(agent_runs_concat['predicted_topic_match'] == 1) & (all_data['predicted_stance'] == 'support'), 'predicted_stance_support'] = 1
        agent_runs_concat['predicted_stance_oppose'] = 0
        agent_runs_concat.loc[(agent_runs_concat['predicted_topic_match'] == 1) & (all_data['predicted_stance'] == 'oppose'), 'predicted_stance_oppose'] = 1
        
        agent_runs_concat_agg_bins['predicted_stance_support_count'] = agent_runs_concat[['predicted_stance_support','elapsed_total_bin']].groupby(['elapsed_total_bin']).sum()
        agent_runs_concat_agg_bins['predicted_stance_oppose_count'] = agent_runs_concat[['predicted_stance_oppose','elapsed_total_bin']].groupby(['elapsed_total_bin']).sum()
        
        
        # # save agg_bins
        agents_analysis_data[agent]['data_agg_bins'] = agent_runs_concat_agg_bins
        
# sum over columns 'video_action_watch', 'bin_count' and 'video_time_duration'

# 1. sum over topics
agg_data_topic = {x:'' for x in unique_topics}

for agent_name,agent_data in agents_analysis_data.items():
    
    topic = agent_data['topic']
        
    if type(agg_data_topic[topic]) == str:
    
        agg_data_topic[topic] = agent_data['data_agg_bins']
        
    else:
        
        # this works but column names are not unique!!!
        agg_data_topic[topic] = pd.concat([agg_data_topic[topic], agent_data['data_agg_bins']], axis = 1, ignore_index=False, sort=False)

        

# aggregate per agent columns per topic

agg_data_topic_sum = {}

for topic,data in agg_data_topic.items():
    
    agg_data_topic_sum[topic] = agg_data_topic[topic].groupby(axis=1, level=0).sum()
    agg_data_topic_sum[topic]['bin_watch_percentage'] = (agg_data_topic_sum[topic]['video_action_watch']/agg_data_topic_sum[topic]['bin_count'])*100
    agg_data_topic_sum[topic]['topic_watch_percentage'] = (agg_data_topic_sum[topic]['predicted_topic_count']/agg_data_topic_sum[topic]['bin_count'])*100
    agg_data_topic_sum[topic]['random_watch_percentage'] = (agg_data_topic_sum[topic]['predicted_topic_count_random']/agg_data_topic_sum[topic]['bin_count'])*100
    agg_data_topic_sum[topic]['predicted_stance_support_percentage'] = (agg_data_topic_sum[topic]['predicted_stance_support_count']/agg_data_topic_sum[topic]['predicted_topic_match_count'])*100
    agg_data_topic_sum[topic]['predicted_stance_oppose_percentage'] = (agg_data_topic_sum[topic]['predicted_stance_oppose_count']/agg_data_topic_sum[topic]['predicted_topic_match_count'])*100
    # agg_data_topic_sum[topic]['video_time_duration_watched_percentage'] = (agg_data_topic_sum[topic]['video_time_duration_watched']/agg_data_topic_sum[topic]['video_time_duration'])*100
    # add column with elapsed minutes
    agg_data_topic_sum[topic]['time_bin_id'] = agg_data_topic_sum[topic].index.values
    agg_data_topic_sum[topic]['time_bin_id'] = agg_data_topic_sum[topic]['time_bin_id'].apply(lambda x: int(x.left.total_seconds() / 60))
    
    # add column where we will track difference between predicted_topic_count and predicted_topic_count_recipes
    agg_data_topic_sum[topic]['topic_ratio'] = agg_data_topic_sum[topic]['predicted_topic_count'] - agg_data_topic_sum[topic]['predicted_topic_count_random']
    agg_data_topic_sum[topic]['topic_ratio'] = agg_data_topic_sum[topic]['topic_ratio']/(agg_data_topic_sum[topic]['predicted_topic_count'] + agg_data_topic_sum[topic]['predicted_topic_count_random'])
    
    # add column where we track difference between total amount of videos ('bin_count') and total amount of topic videos (predicted_topic_count + predicted_topic_count_recipes)
    agg_data_topic_sum[topic]['personalization_ratio'] = agg_data_topic_sum[topic]['predicted_topic_count'] + agg_data_topic_sum[topic]['predicted_topic_count_random']
    agg_data_topic_sum[topic]['personalization_ratio'] = agg_data_topic_sum[topic]['personalization_ratio']/agg_data_topic_sum[topic]['bin_count']
    
    agg_data_topic_sum[topic].replace(np.nan, 0, inplace=True)

  
# aggregate to one list for purposes of statistical analysis
# i.e. dont sum!!!
# we need these values from agents_analysis_data:
    # predicted_stance_support_count
    # predicted_stance_oppose_count
    # predicted_topic_count (use for RQ1 instead of topic_watch_percentage)
    # predicted_topic_count_recipes (use for RQ1 instead of cooking_watch_percentage)
# agg_data_topic_list = {}

# for topic,data in agg_data_topic.items():
    
#     agg_data_topic_list[topic] = agg_data_topic[topic].groupby(axis=1, level=0).agg(lambda x: list(x))
    
    
agg_data_topic_list = {x:'' for x in unique_topics}

for agent_name,agent_data in agents_analysis_data.items():
    
    topic = agent_data['topic']
        
    if type(agg_data_topic_list[topic]) == str:
            
        agg_data_topic_list[topic] = {}
        agg_data_topic_list[topic]['predicted_stance_support_count'] = agent_data['data_agg_bins']['predicted_stance_support_count'].tolist()
        agg_data_topic_list[topic]['predicted_stance_oppose_count'] = agent_data['data_agg_bins']['predicted_stance_oppose_count'].tolist()
        agg_data_topic_list[topic]['predicted_topic_count'] = agent_data['data_agg_bins']['predicted_topic_count'].tolist()
        agg_data_topic_list[topic]['predicted_topic_count_random'] = agent_data['data_agg_bins']['predicted_topic_count_random'].tolist()

        
    else:
               
        agg_data_topic_list[topic]['predicted_stance_support_count'].extend(agent_data['data_agg_bins']['predicted_stance_support_count'].tolist())
        agg_data_topic_list[topic]['predicted_stance_oppose_count'].extend(agent_data['data_agg_bins']['predicted_stance_oppose_count'].tolist())
        agg_data_topic_list[topic]['predicted_topic_count'].extend(agent_data['data_agg_bins']['predicted_topic_count'].tolist())
        agg_data_topic_list[topic]['predicted_topic_count_random'].extend(agent_data['data_agg_bins']['predicted_topic_count_random'].tolist())



# 3. sum over stance and topic
agg_data_topic_stance = {x:{y:'' for y in unique_stances} for x in unique_topics}

for agent_name,agent_data in agents_analysis_data.items():
    
    topic = agent_data['topic']
    stance = agent_data['stance']
    
    if type(agg_data_topic_stance[topic][stance]) == str:
    
        agg_data_topic_stance[topic][stance] = agent_data['data_agg_bins']
        
    else:
        
        # this works but column names are not unique!!!
        agg_data_topic_stance[topic][stance] = pd.concat([agg_data_topic_stance[topic][stance], agent_data['data_agg_bins']], axis = 1, ignore_index=False, sort=False)


agg_data_topic_stance_sum = {x:{y:'' for y in unique_stances} for x in unique_topics}

for topic,data_dict in agg_data_topic_stance.items():
    
    for stance,data in data_dict.items():
    
        agg_data_topic_stance_sum[topic][stance] = agg_data_topic_stance[topic][stance].groupby(axis=1, level=0).sum()
        agg_data_topic_stance_sum[topic][stance]['bin_watch_percentage'] = (agg_data_topic_stance_sum[topic][stance]['video_action_watch']/agg_data_topic_stance_sum[topic][stance]['bin_count'])*100
        
        agg_data_topic_stance_sum[topic][stance]['topic_watch_percentage'] = (agg_data_topic_stance_sum[topic][stance]['predicted_topic_count']/agg_data_topic_stance_sum[topic][stance]['bin_count'])*100
        agg_data_topic_stance_sum[topic][stance]['random_watch_percentage'] = (agg_data_topic_stance_sum[topic][stance]['predicted_topic_count_random']/agg_data_topic_stance_sum[topic][stance]['bin_count'])*100
        
        # agg_data_topic_stance_sum[topic][stance]['video_time_duration_watched_percentage'] = (agg_data_topic_stance_sum[topic][stance]['video_time_duration_watched']/agg_data_topic_stance_sum[topic][stance]['video_time_duration'])*100
        
        agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_percentage'] = (agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_count']/agg_data_topic_stance_sum[topic][stance]['predicted_topic_match_count'])*100
        agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_percentage'] = (agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_count']/agg_data_topic_stance_sum[topic][stance]['predicted_topic_match_count'])*100
        
        # calculate average per 1 agent, we have 4 agent per stance-topic
        agg_data_topic_stance_sum[topic][stance]['predicted_topic_count_per_agent_avg'] = agg_data_topic_stance_sum[topic][stance]['predicted_topic_count']/4
        # agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_per_agent_avg'] = agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_count']/4
        agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_per_agent_avg'] = agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_count']/4
        
        
        # add column with elapsed minutes
        agg_data_topic_stance_sum[topic][stance]['time_bin_id'] = agg_data_topic_stance_sum[topic][stance].index.values
        agg_data_topic_stance_sum[topic][stance]['time_bin_id'] = agg_data_topic_stance_sum[topic][stance]['time_bin_id'].apply(lambda x: (x.left.total_seconds() / 60))
        
        agg_data_topic_stance_sum[topic][stance].replace(np.nan, 0, inplace=True)
        
        # add column where we will track difference between predicted_topic_count and predicted_topic_count_recipes
        agg_data_topic_stance_sum[topic][stance]['stance_ratio'] = agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_count'] - agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_count']
        agg_data_topic_stance_sum[topic][stance]['stance_ratio'] = agg_data_topic_stance_sum[topic][stance]['stance_ratio']/(agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_count'] + agg_data_topic_stance_sum[topic][stance]['predicted_stance_oppose_count'])
        
        # fill nan with o (SMALL HACK)
        agg_data_topic_stance_sum[topic][stance]['stance_ratio'].fillna(0,inplace=True)
 
        
 
# aggregate to one list for purposes of statistical analysis
# i.e. dont sum!!!
# we need these values from agents_analysis_data:
    # predicted_stance_support_count
    # predicted_stance_oppose_count
    # predicted_topic_count (use for RQ1 instead of topic_watch_percentage)
    # predicted_topic_count_recipes (use for RQ1 instead of cooking_watch_percentage)

agg_data_topic_stance_list = {x:{y:'' for y in unique_stances} for x in unique_topics}

for agent_name,agent_data in agents_analysis_data.items():
    
    topic = agent_data['topic']
    stance = agent_data['stance']
    
    if type(agg_data_topic_stance_list[topic][stance]) == str:
    
        agg_data_topic_stance[topic][stance] = agent_data['data_agg_bins']
        
        agg_data_topic_stance_list[topic][stance] = {}
        agg_data_topic_stance_list[topic][stance]['predicted_stance_support_count'] = agent_data['data_agg_bins']['predicted_stance_support_count'].tolist()
        agg_data_topic_stance_list[topic][stance]['predicted_stance_oppose_count'] = agent_data['data_agg_bins']['predicted_stance_oppose_count'].tolist()
        agg_data_topic_stance_list[topic][stance]['predicted_topic_count'] = agent_data['data_agg_bins']['predicted_topic_count'].tolist()
        agg_data_topic_stance_list[topic][stance]['predicted_topic_count_random'] = agent_data['data_agg_bins']['predicted_topic_count_random'].tolist()

        
    else:
               
        agg_data_topic_stance_list[topic][stance]['predicted_stance_support_count'].extend(agent_data['data_agg_bins']['predicted_stance_support_count'].tolist())
        agg_data_topic_stance_list[topic][stance]['predicted_stance_oppose_count'].extend(agent_data['data_agg_bins']['predicted_stance_oppose_count'].tolist())
        agg_data_topic_stance_list[topic][stance]['predicted_topic_count'].extend(agent_data['data_agg_bins']['predicted_topic_count'].tolist())
        agg_data_topic_stance_list[topic][stance]['predicted_topic_count_random'].extend(agent_data['data_agg_bins']['predicted_topic_count_random'].tolist())



      
      
# RQ1 PLOTS

# we fist need to add topic_watch_percentage to cooking_watch_percentage
# this is needed so we get cumulative bar chart
# cooking will allways be at the bottom!!!

# RQ1.1 PLOTS
# we should plot the RATIO BETWEEN POLITICAL AND RANDOM
# scale +1, 0, -1
# this plot will give us visualization of TOPIC DRIFT
# if ratio -> +1 = more topic than cooking
# if ratio == 0 = 50:50 balance between topic and cooking
# if ratio -> -1 more cooking than topic

# ratio formula:
# (predicted_topic_count - predicted_topic_count_recipes)/(predicted_topic_count + predicted_topic_count_recipes)

# data will be in agg_data_topic_sum[topic]['topic_ratio']


# VERSION 1 : PERSONALIZATION DRIFT

for topic in unique_topics:
    
    agg_data_topic_sum[topic]['topic_watch_percentage_cumulative'] = agg_data_topic_sum[topic]['random_watch_percentage'] + agg_data_topic_sum[topic]['topic_watch_percentage']
    
    plot_name = topic
    file_name = plot_name + '_UMAP_PERSONALIZATION_DRIFT'
    
    # trim data to length 1000 minutes
    if type(data_trim_minutes) != str:
        
        agg_data_display = agg_data_topic_sum[topic].drop(agg_data_topic_sum[topic][agg_data_topic_sum[topic].time_bin_id > data_trim_minutes].index)
        
    else:
        
        agg_data_display = agg_data_topic_sum[topic]

    g1 = sns.barplot(agg_data_topic_sum[topic], x="time_bin_id", y="topic_watch_percentage_cumulative",color='royalblue',native_scale=True)
    g1.set_xticklabels(g1.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()
    g1.set_title(plot_name,fontsize=16)
    g1.set(xlabel='Elapsed time in minutes', ylabel='Ratio of recommended videos (in %)')
    g1.xaxis.label.set_size(13)
    g1.yaxis.label.set_size(13)
    
    g2 = sns.barplot(agg_data_topic_sum[topic], x="time_bin_id", y="topic_watch_percentage",color='orange',native_scale=True)
    g2.set_xticklabels(g2.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()
    g2.set_title(plot_name,fontsize=16)
    g2.set(xlabel='Elapsed time in minutes', ylabel='Ratio of recommended videos (in %)')
    g2.xaxis.label.set_size(13)
    g2.yaxis.label.set_size(13)
    
    g1.tick_params(axis='both', labelsize=13)
    g2.tick_params(axis='both', labelsize=13)
    
    g3 = sns.regplot(x="time_bin_id",y='topic_watch_percentage',data=agg_data_display, fit_reg=True, color = 'red', marker="x", ax=g2,order=2, robust = False)
    # g3.set(ylim=(-1.1, 1.1))
    g3.yaxis.label.set_size(13)
    g3.tick_params(axis='both', labelsize=13)
    
    g3.set(xlabel='Elapsed time in minutes', ylabel='Ratio of recommended videos (in %)')


    # add legend
    # top_bar = mpatches.Patch(color='orange', label='Topic + Cooking')
    # bottom_bar = mpatches.Patch(color='magenta', label='Personalization drift trend')
    # plt.legend(handles=[top_bar, bottom_bar],fontsize=13)
    
    top_bar = mpatches.Patch(color='orange', label=plot_name)
    middle_bar = mpatches.Patch(color='royalblue', label='Random')
    bottom_bar = mpatches.Patch(color='red', label='Preference-aligned drift')
    plt.legend(handles=[top_bar, middle_bar, bottom_bar],fontsize=11)
    # plt.legend(handles=[top_bar, middle_bar, bottom_bar],fontsize=11, loc='upper center',
    #        ncol=3, mode="expand", borderaxespad=0.)


    # g.set_title(plot_name)

    # g.set(xlabel='elapsed time in minutes', ylabel='Percent')

    # g.set_xticklabels(g.get_xticklabels(), rotation=40, ha="right")
    # plt.tight_layout()

    fig = g3.get_figure()
    fig.savefig(os.path.join(path_figures,file_name + '.png'),bbox_inches='tight')

    plt.show()
        
        
#RQ 2 plots in ABSOLUTE NUMBERS

# RQ2.1 PLOTS
# we should plot the RATIO BETWEEN SUPPORT AND OPPOSE
# scale +1, 0, -1
# this plot will give us visualization of POLARIZATION DRIFT
# if ratio -> +1 = more support than oppose
# if ratio == 0 = 50:50 balance between support and oppose
# if ratio -> -1 more oppose than support


# PROBLEM: how to tyreat missing data???

for topic in unique_topics:
    
    for stance in unique_stances: 
        
        plot_name = topic + ' seeded with both stances'
    
        # set promoting stance to 100% so we get cumulative plot
        # agg_data_topic_stance_sum[topic][stance]['predicted_stance_support_percentage_cumulative'] = 100
        
        # trim data to length 1000 minutes
        if type(data_trim_minutes) != str:
            
            agg_data_display = agg_data_topic_stance_sum[topic][stance].drop(agg_data_topic_stance_sum[topic][stance][agg_data_topic_stance_sum[topic][stance].time_bin_id > data_trim_minutes].index)
            
        else:
            
            agg_data_display = agg_data_topic_stance_sum[topic][stance]

    
        g1 = sns.barplot(agg_data_display, x="time_bin_id", y="predicted_topic_count",color='royalblue',native_scale=True)
        g1.set_xticklabels(g1.get_xticklabels(), rotation=40, ha="right")
        plt.tight_layout()
        g1.set_title(plot_name,fontsize=13)
        g1.set(xlabel='Elapsed time in minutes', ylabel='Number of recommended videos')
        g1.xaxis.label.set_size(13)
        g1.yaxis.label.set_size(13)
        
        g2 = sns.barplot(agg_data_display, x="time_bin_id", y="predicted_stance_oppose_count",color='orange',native_scale=True)
        g2.set_xticklabels(g2.get_xticklabels(), rotation=40, ha="right")
        plt.tight_layout()
        g2.set_title(plot_name,fontsize=13)
        g2.set(xlabel='Elapsed time in minutes', ylabel='Number of recommended videos')
        g2.xaxis.label.set_size(13)
        g2.yaxis.label.set_size(13)
        
        
        g1.tick_params(axis='both', labelsize=13)
        g2.tick_params(axis='both', labelsize=13)
        
        g3 = sns.regplot(x="time_bin_id",y='stance_ratio',data=agg_data_display, fit_reg=True, color = 'magenta', marker="x", ax=g2.axes.twinx(),order=1, robust = True)
        g3.set(ylabel='Stance ratio')
        g3.set(ylim=(-1.1, 1.1))
        g3.yaxis.label.set_size(13)
        g3.tick_params(axis='both', labelsize=13)
    
    
        # add legend
        top_bar = mpatches.Patch(color='royalblue', label='support')
        middle_bar = mpatches.Patch(color='orange', label='oppose')
        bottom_bar = mpatches.Patch(color='magenta', label='Polarisation-stance drift')
        plt.legend(handles=[top_bar, middle_bar, bottom_bar],fontsize=11)
    
    
        plt.tight_layout()
        fig = g3.get_figure()
        fig.savefig(os.path.join(path_figures,plot_name + '.png'))
    
        plt.show()
        
        

# STATISTICS FOR RQ 2.1:
    
from scipy import stats
    
data_oppose = agg_data_topic_stance_list['US Politics']['indifferent']['predicted_stance_oppose_count']
data_support = agg_data_topic_stance_list['US Politics']['indifferent']['predicted_stance_support_count']

# statistics of data
stats.describe(data_oppose)
stats.describe(data_support)

stats.ttest_ind(data_oppose, data_support)

# try mannwhitneyu test
stats.mannwhitneyu(data_oppose, data_support)

# we dont have the same variance so try equal_var=False
print('Difference between support stance and support recommended videos and oppose stance and oppose recommended videos for topic donald_trump: ')
print(stats.mannwhitneyu(data_oppose, data_support))
print('==============================================================')