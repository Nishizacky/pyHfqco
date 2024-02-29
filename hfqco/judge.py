import pandas as pd
import math
import re
from .config import Config
import matplotlib.pyplot as plt
from .graph import sim_plot
import copy

def get_switch_timing(config : Config, data : pd.DataFrame, plot = False, timescale = "ps", blackstyle = False) -> pd.DataFrame:

    p = math.pi
    p2 = math.pi * 2

    res_df = []

    if not config.phase_ele == []:
        new_df = pd.DataFrame()
        for squid in config.phase_ele:
            if len(squid) == 1:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')']
            elif len(squid) == 2:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')'] + data['P('+squid[1].upper()+')']
            elif len(squid) == 3:
                new_df['P('+'+'.join(squid)+')'] = data['P('+squid[0].upper()+')'] + data['P('+squid[1].upper()+')'] + data['P('+squid[2].upper()+')']
    
        if plot:
            sim_plot(new_df, timescale, blackstyle)

        for column_name, srs in new_df.items():
            # バイアスをかけた時の状態の位相(初期位相)
            init_phase = srs[( srs.index > config.start_time ) & ( srs.index < config.end_time )].mean()
            
            judge_phase = init_phase + p
            
            # クロックが入ってからのものを抽出
            srs = srs[srs.index > config.end_time]

            # 位相変数
            flag = 0
            for i in range(len(srs)-1):
                if (srs.iat[i] - (flag*p2 + judge_phase)) * (srs.iat[i+1] - (flag*p2 + judge_phase)) < 0:
                    flag = flag + 1
                    res_df.append({'time':srs.index[i], 'phase':flag, 'element':column_name})
                elif (srs.iat[i] - ((flag-1)*p2 + judge_phase)) * (srs.iat[i+1] - ((flag-1)*p2 + judge_phase)) < 0:
                    flag = flag - 1
                    res_df.append({'time':srs.index[i], 'phase':flag, 'element':column_name})

    if not config.voltage_ele == []:
        for vol in config.voltage_ele:
            srs_std = data['V('+vol+')'].rolling(window=10).std()
            srs_std_max = srs_std.rolling(window=10).max()
            srs_std.plot()
            basis = srs_std_max.mean()/2
            reap = False
            tmp = 0
            flag = 1
            for i in range(len(srs_std_max)-1):
                if not reap:
                    if srs_std_max.iat[i] < basis and basis < srs_std_max.iat[i+1]:
                        srs_std_max.iat[i] = basis *2
                        tmp = srs_std_max.index[i]
                        reap = True
                else:
                    if srs_std_max.iat[i] > basis and basis > srs_std_max.iat[i+1]:
                        srs_std_max.iat[i] = - basis * 2
                        if srs_std_max.index[i] - tmp > config.pulse_interval/2:
                            res_df = pd.concat([res_df, pd.DataFrame([{'time':tmp, 'phase':flag, 'element':'V('+vol+')'}])], ignore_index=True)
                            res_df = pd.concat([res_df, pd.DataFrame([{'time':srs_std_max.index[i], 'phase':-flag, 'element':'V('+vol+')'}])], ignore_index=True)
                            flag = flag + 1
                        reap = False

    return res_df


def compare_switch_timings(dl1 : list, dl2 : list, config : Config) -> bool:

    def get_dict(dict_list : list, phase : int, element : str) -> float:
        for l in dict_list:
            if l['phase'] == phase and l['element'] == element:
                return l['time']
        return 0

    # Number of switches is different
    if len(dl1) == len(dl2):
        for l1 in dl1:
            l2_time = get_dict(dl2, l1['phase'], l1['element'])
            l1_time = l1['time']
            if l2_time < l1_time - config.pulse_delay or l1_time + config.pulse_delay < l2_time:
                return False
        return True
    else:
        return False
    
def compare_switch_timings(dl1 : list, dl2 : list, config : Config) -> bool:

    def get_dict(dict_list : list, phase : int, element : str) -> float:
        for l in dict_list:
            if l['phase'] == phase and l['element'] == element:
                return l['time']
        return 0

    # Number of switches is different
    if len(dl1) == len(dl2):
        for l1 in dl1:
            l2_time = get_dict(dl2, l1['phase'], l1['element'])
            l1_time = l1['time']
            if l2_time < l1_time - config.pulse_delay or l1_time + config.pulse_delay < l2_time:
                return False
        return True
    else:
        return False
       
def compare_list(list1 : list, list2 : list, pulse_delay : float, log : bool = False) -> bool:
    list1inp  = copy.deepcopy(list1)
    if len(list1) != len(list2):
        if log:
            print("数が違います。len(list1)=",len(list1), ", len(list2)=",len(list2))
        return False
    
    list1inp = sorted(list1inp, key=lambda x: (x['element'], x['time']))
    list2 = sorted(list2, key=lambda x: (x['element'], x['time']))
    for dict1, dict2 in zip(list1inp, list2):
        if dict1['element'] == dict2['element'] and abs(dict1['time'] - dict2['time']) > pulse_delay:
            if log:
                print("遅延による誤動作。dff=",abs(dict1['time'] - dict2['time']))
            return False
    return True

def get_switch_timing_half_pi(elements : list, data : pd.DataFrame, start_time : float, end_time : float, interval : float = 0) -> list:

    result_df = []
        
    for ele in elements:
        if not ele in data.columns:
            raise ValueError("与えられたデータの中に素子の位相データが存在しませんでした。")
        
        # 素子の位相データ
        srs = data[ele]
        # バイアスをかけた時の状態の位相(初期位相)
        init_phase = srs[( srs.index > start_time ) & ( srs.index < end_time )].mean()
        # 基準の位相
        ref_phase = init_phase + math.pi/2
        # クロックが入ってからのものを抽出
        srs = srs[srs.index > end_time]

        # 位相変数
        flag = 0
        pre_leap_time = 0
        for i in range(len(srs)-1):
            if (srs.iat[i] - (flag*math.pi + ref_phase)) * (srs.iat[i+1] - (flag*math.pi + ref_phase)) <= 0 and pre_leap_time + interval < srs.index[i]:
                result_df.append({'time':srs.index[i], 'phase':flag, 'element':ele, 'ref':flag*math.pi + ref_phase})
                flag = flag + 1
                pre_leap_time = srs.index[i]
            elif (srs.iat[i] - ((flag-1)*math.pi + ref_phase)) * (srs.iat[i+1] - ((flag-1)*math.pi + ref_phase)) <= 0 and pre_leap_time + interval < srs.index[i]:
                result_df.append({'time':srs.index[i], 'phase':flag, 'element':ele, 'ref':flag*math.pi + ref_phase})
                flag = flag - 1
                pre_leap_time = srs.index[i]

    return result_df

def get_leap_timing(elements : list, data : pd.DataFrame, ref_value : float, interval : float = 100e-12, start_time : float = 0) -> list:

    result_df = []
        
    for ele in elements:
        if not ele in data.columns:
            raise ValueError("与えられたデータの中に素子の位相データが存在しませんでした。")
        
        # 素子の位相データ
        srs = data[ele]
        # クロックが入ってからのものを抽出
        srs = srs[srs.index > start_time]

        # 位相変数
        pre_leap_time = 0
        for i in range(len(srs)-1):
            if ((srs.iat[i] - ref_value) * (srs.iat[i+1] - ref_value)) < 0 and pre_leap_time + interval < srs.index[i]:
                pre_leap_time = srs.index[i]
                result_df.append({'time':srs.index[i], 'phase':0, 'element':ele})

    return result_df


def get_first_leap_time(element : str, data : pd.DataFrame, start_time : float, stop_time : float) -> int:

    hp = math.pi/2

    # columnsが存在しなければ失敗
    if not element in data.columns:
        print("columnsが存在していません。")
        return -1
    
    srs = data[element]

    # バイアスをかけた時の状態の位相(初期位相)
    init_phase = srs[( srs.index > start_time ) & ( srs.index < stop_time )].mean()
    
    for i in range(len(srs)-1):
        if ((srs.iat[i] - (init_phase + hp)) * (srs.iat[i+1] - (init_phase + hp)) < 0) or \
            ((srs.iat[i] - (init_phase - hp)) * (srs.iat[i+1] - (init_phase - hp)) < 0):
            return i

    return -1
 