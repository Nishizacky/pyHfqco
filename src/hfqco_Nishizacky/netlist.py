import re
import pandas as pd
from .util import stringToNum, isfloat, isint, vaild_number
from .pyjosim import simulation
from .judge import get_switch_timing_half_pi, compare_list
from .graph import margin_plot
import concurrent.futures
import copy
from tqdm import tqdm
from .graph import sim_plot
import math


class Netlist:
    def __init__(self, raw_data : str, config : dict,plot:bool=True):

        # get variable
        self.vdf, self.sim_data = self.__get_variable(raw=raw_data)

        # check config file
        self.start_time = None
        self.end_time = None
        self.pulse_delay = None
        self.pulse_interval = None
        self.phase_ele = []
        self.voltage_ele = []
        self.__get_config(config)

        # Base switch timing
        self.get_base_switch_timing(plot=plot)

    def __get_config(self, config_data : dict):
        # 全て確認
        for k in ["avgcalc.start.time", "avgcalc.end.time", "pulse.delay", "pulse.interval","phase.ele","voltage.ele"]:
            if not k in config_data:
                raise ValueError("\033[31m["+k+"]の値が読み取れません。"+"\033[0m")
        
        # start_time, end_time
        if not type(config_data["avgcalc.start.time"]) == float or not type(config_data["avgcalc.end.time"]) == float:
            raise ValueError("\033[31m[avgcalc.start.time], [avgcalc.end.time]の値が読み取れません。\033[0m")
        else:
            self.start_time = config_data["avgcalc.start.time"]
            self.end_time = config_data["avgcalc.end.time"]
            print("･ (Period to calculate initial phase)\t\t= ",self.start_time, " ~ ", self.end_time, "[s]")
            
        # pulse_delay
        if not type(config_data["pulse.delay"]) == float:
            raise ValueError("\033[31m[pulse.delay]の値が読み取れません。\033[0m")
        else:
            self.pulse_delay = config_data["pulse.delay"]
            print("･ (Acceptable switch timing delay)\t\t= ",config_data["pulse.delay"], "[s]")

        # pulse_interval
        if not type(config_data["pulse.interval"]) == float:
            raise ValueError("\033[31m[pulse.interval]の値が読み取れません。\033[0m")
        else:
            self.pulse_interval= config_data["pulse.interval"]
            print("･ (Interval between input SFQ or HFQ pulses)\t= ", config_data["pulse.interval"], "[s]")

        # phase_ele
        if not type(config_data["phase.ele"])==list:
            raise ValueError("\033[31m[phase.ele]の値が読み取れません。"+"\033[0m")
        else:
            self.phase_ele = config_data["phase.ele"]

        # voltage_ele
        if not type(config_data["voltage.ele"])==list:
            raise ValueError("\033[31m[voltage.ele]の値が読み取れません。"+"\033[0m")
        else:
            self.voltage_ele = config_data["voltage.ele"]

        

    def __get_variable(self, raw : str) -> tuple:
        df = pd.DataFrame()
        
        vlist = re.findall('#.+\(.+?\)',raw)

        for raw_line in vlist:
            li = re.sub('\s','',raw_line)
            char = re.search('#.+?\(',li, flags=re.IGNORECASE).group()
            char = re.sub('#|\(','',char)
            if not df.empty and char in df.index.tolist():
                continue
            dic = {'def': None, 'main': None, 'sub': None, 'element':None,'fix': False ,'upper': None, 'lower': None ,'shunt': None,'dp': True,'dpv': None}
            
            m = re.search('\(.+?\)',li).group()
            m = re.sub('\(|\)','',m)
            spl = re.split(',',m)
            if len(spl)==1:
                if isfloat(spl[0]) or isint(spl[0]):
                    num = stringToNum(spl[0])
                    dic['def'] = num
                    dic['main'] = num
                    dic['sub'] = num
            for sp in spl:
                val = re.split('=',sp)
                if len(val) == 1:
                    if isfloat(val[0]) or isint(val[0]):
                        num = stringToNum(spl[0])
                        dic['def'] = num
                        dic['main'] = num
                        dic['sub'] = num
                elif len(val) == 2:
                    if re.fullmatch('v|value',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['def'] = num
                        dic['main'] = num
                        dic['sub'] = num
                    elif re.fullmatch('fix|fixed',val[0],flags=re.IGNORECASE):
                        if re.fullmatch('true',val[1],flags=re.IGNORECASE):
                            dic['fix'] = True
                    elif re.fullmatch('shunt',val[0],flags=re.IGNORECASE):
                        dic['shunt'] = val[1]
                    elif re.fullmatch('dp',val[0],flags=re.IGNORECASE):
                        if re.fullmatch('false',val[1],flags=re.IGNORECASE):
                            dic['dp'] = False
                    elif re.fullmatch('dpv',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['dpv'] = num
                    elif re.fullmatch('upper',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['upper'] = num
                    elif re.fullmatch('lower',val[0],flags=re.IGNORECASE):
                        num = stringToNum(val[1])
                        dic['lower'] = num
                    else:
                        raise ValueError("[ "+sp+" ]の記述が読み取れません。")
                else:
                    raise ValueError("[ "+sp+" ]の記述が読み取れません。")

            for line in raw.splitlines():
                if raw_line in line:
                    if re.fullmatch('R',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'R'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('L',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'L'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('C',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'C'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('V',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'V'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    elif re.fullmatch('B',line[0:1],flags=re.IGNORECASE):
                        dic['element'] = 'B'
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    else:
                        dic['element'] = None
                        if dic['dpv'] == None:
                            dic['dpv'] = 7
                    break
            
            dic_df = pd.DataFrame.from_dict({ char : dic }, orient = "index")
            df = pd.concat([df, dic_df])

        for v in re.findall('#.+\(.+?\)',raw):
            ch = re.search('#.+?\(',v).group()
            ch = re.sub('#|\(','',ch)
            ch = "#("+ch+")"
            raw = raw.replace(v, ch)

        return df , raw
    
    def get_base_switch_timing(self, plot : bool = True):
        print("Simulate with default values.")
        df = self.simulation_with_paramters(self.vdf['def'])
        if plot:
            sim_plot(df)
        self.base_switch_timing = get_switch_timing_half_pi(self.phase_ele, df, self.start_time, self.end_time)
        print(self.base_switch_timing)

    
    def simulation_with_paramters(self, parameters : pd.Series) -> pd.DataFrame:
        copied_sim_data = self.sim_data
        for index in parameters.index:
            copied_sim_data = copied_sim_data.replace('#('+index+')', str(parameters[index]))
        return simulation(copied_sim_data)
    

    def custom_simulation(self, res_df : pd.DataFrame):
        param = copy.deepcopy(self.vdf['def'])
        
        # tqdmで経過が知りたい時
        with tqdm(total=len(res_df)) as progress:
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                for num, srs in res_df.iterrows():
                    # 値の書き換え
                    for colum, value in srs.items():
                        if not colum == 'param':
                            param[colum] = value

                    inp = copy.deepcopy(param)
                    future = executor.submit(self.get_critical_margin, num, inp)
                    future.add_done_callback(lambda p: progress.update()) # tqdmで経過が知りたい時
                    futures.append(future)

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            res : tuple = future.result()
            res_df.at[res[0],'min_ele'] = res[1]
            res_df.at[res[0],'min_margin'] = res[2]

        return res_df
    
    def get_critical_margin(self,num : int, param : pd.Series = pd.Series(dtype='float64')) -> tuple:
        margins = self.get_margins(param = param, plot=False)
        
        min_margin = 100
        min_ele = None
        for element in margins.index:
            if not self.vdf.at[element,'fix']:
                # 最小マージンの素子を探す。
                if abs(margins.at[element,'low(%)']) < min_margin or abs(margins.at[element,'high(%)']) < min_margin:
                    min_margin = vaild_number(min(abs(margins.at[element,'low(%)']), abs(margins.at[element,'high(%)'])), 4)
                    min_ele = element
        
        return (num, min_ele, min_margin)


    def get_margins(self, param : pd.Series = pd.Series(dtype='float64'), plot : bool = True, blackstyle : bool = False, accuracy : int = 8, thread : int = 128,multithread:bool=True) -> pd.DataFrame: 
        if param.empty:
            print("Using default parameters")
            param = self.vdf['def']

        # result を受け取る dataframe
        margin_result = pd.DataFrame(columns = ['low(value)', 'low(%)', 'high(value)', 'high(%)',"average(value)"])

        # 0%の値は動くか確認
        if not self.__operation_judge(param):
            for index in self.vdf.index:
                margin_result.loc[index] = 0

        else:
            result_dic = []
            if plot:
                with tqdm(total=len(self.vdf)) as progress:
                    futures = []
                    if multithread == True:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as executor:
                            for index in self.vdf.index:
                                future = executor.submit(self.__get_margin,param, index, accuracy)
                                future.add_done_callback(lambda p: progress.update()) # tqdmで経過が知りたい時
                                futures.append(future)
                            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                                # 結果を受け取り
                                result_dic= future.result()
                                # variables dataframeに追加
                                margin_result.loc[result_dic["index"]] = result_dic["result"]
                    else:
                        for index in self.vdf.index:
                                print("prosess "+str(index)+" ",end="")
                                result_dic = self.__get_margin(param, index, accuracy)
                                margin_result.loc[result_dic["index"]] = result_dic["result"]
                                print("finish")
            else:
                for index in self.vdf.index:
                    result_dic= self.__get_margin(param, index, accuracy)
                    margin_result.loc[result_dic["index"]] = result_dic["result"]
        margin_result = margin_result.reindex(self.vdf.index)
        # plot     
        if plot:
            min_margin = 100
            min_ele = None
            for element in margin_result.index:
                if not self.vdf.at[element,'fix']:
                    # 最小マージンの素子を探す。
                    if abs(margin_result.at[element,'low(%)']) < min_margin or abs(margin_result.at[element,'high(%)']) < min_margin:
                        min_margin = vaild_number(min(abs(margin_result.at[element,'low(%)']), abs(margin_result.at[element,'high(%)'])), 4)
                        min_ele = element
            margin_plot(margin_result, min_ele, blackstyle = blackstyle)
        return margin_result
    
    def __get_margin(self, srs : pd.Series, target_ele : str, accuracy : int = 7):

        # deepcopy　をする
        parameters : pd.Series = copy.deepcopy(srs)

        # デフォルト値の抽出
        default_v = parameters[target_ele]
        future = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as exector:
            promise_lMargine = exector.submit(self.get_margine_lower,parameters,target_ele,default_v,accuracy)
            promise_uMargine = exector.submit(self.get_margine_upper,parameters,target_ele,default_v,accuracy)
        lower_margin = promise_lMargine.result()
        lower_margin_rate = (lower_margin - default_v) * 100 / default_v
        upper_margin = promise_uMargine.result()
        upper_margin_rate = (upper_margin - default_v) * 100 / default_v
        # -----------------
        average = lower_margin+upper_margin
        average /= 2
        average = round(average,3-math.floor(math.log10(abs(average)))-1)
        # deepcopy　したものを削除
        del parameters

        return {"index" : target_ele, "result" : (lower_margin, lower_margin_rate, upper_margin, upper_margin_rate,average)}
    
    def __operation_judge(self, parameters : pd.Series):
        res = get_switch_timing_half_pi(self.phase_ele, self.simulation_with_paramters(parameters), self.start_time, self.end_time)
        return compare_list(res, self.base_switch_timing, self.pulse_delay)

    def get_margine_lower(self,parameters,target_ele,default_v,accuracy):
        high_v = default_v
        low_v = 0
        target_v = (high_v + low_v)/2

        for i in range(accuracy):
            parameters[target_ele] = target_v
            if self.__operation_judge(parameters):
                high_v = target_v
                target_v = (high_v + low_v)/2
            else:
                low_v = target_v
                target_v = (high_v + low_v)/2

        return high_v
        
    def get_margine_upper(self,parameters,target_ele,default_v,accuracy):
        high_v = 0
        low_v = default_v
        target_v = default_v * 2

        for i in range(accuracy):

            parameters[target_ele] = target_v
            if self.__operation_judge(parameters):
                if high_v == 0:
                    low_v = target_v
                    break
                low_v = target_v
                target_v = (high_v + low_v)/2
            else:
                high_v = target_v
                target_v = (high_v + low_v)/2

        return low_v
        