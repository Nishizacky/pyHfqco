import matplotlib.pyplot as plt
import pandas as pd
import re
import math
# ----- Matplotlib の rc 設定 ----
config = {
    "font.size":20,
    "axes.xmargin" : 0,
    # "axes.grid":True,
    "axes.linewidth": 3,
    # "grid.linewidth": 3,
    "figure.figsize":[7.0, 7.0],
    "legend.fontsize": 18,
    "lines.linewidth": 3,
    "xtick.direction" : "in",
    "ytick.direction" : "in",
    "xtick.major.pad" : 10,
    "ytick.major.pad" : 10,
    "xtick.major.size" : 7,
    "ytick.major.size" : 7,
    "xtick.major.width" : 3,
    "ytick.major.width" : 3,
    "axes.unicode_minus": False
}
plt.rcParams.update(config)
# よくわからないがこれで Times New Roman が使える
plt.rcParams['font.family'] = 'DeJavu Serif'
plt.rcParams['font.serif'] = ['Times New Roman']

linestyle = ['-','--',  '-.', ':']


def time_graph(df : pd.DataFrame, ylabel : str, y_axis : str = "", x_axis : str = "", bs : bool = False, savefile : str= ""):
    x_multi = 1
    if x_axis[0] == "m":
        x_multi = 10**3
    elif x_axis[0] == "u":
        x_multi = 10**6
    elif x_axis[0] == "n":
        x_multi = 10**9
    elif x_axis[0] == "p":
        x_multi = 10**12
    
    y_multi = 1
    if len(y_axis) > 0:
        if y_axis[0] == "m":
            y_multi = 10**3
        elif y_axis[0] == "u":
            y_multi = 10**6
        elif y_axis[0] == "n":
            y_multi = 10**9
        elif y_axis[0] == "p":
            y_multi = 10**12

    df.index = df.index * x_multi
    df = df * y_multi
    if bs:
        df.plot(style=linestyle, color='black')
    else:
        df.plot()

    if y_axis == "rad":
        max_value = df.values.max()
        result = int(math.floor(max_value / (5 * math.pi)))
        result = max(result, 1)
        plt.yticks([result * i * math.pi for i in range(0, int(max_value / math.pi) + 1)], [f'{result * i}$\pi$' for i in range(0, int(max_value / math.pi) + 1)])

    plt.tick_params(labelsize=28)
    plt.xlabel("Time ["+x_axis+"]", size=24)  # x軸指定
    plt.ylabel(ylabel+" ["+y_axis+"]", size=24)    # y軸指定
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    if not savefile.startswith("-"):
        plt.savefig(savefile)
        plt.close('all')

def sim_plot(df : pd.DataFrame, timescale : str = "ps", blackstyle : bool = False, filename : str = ""):
    l = df.columns
    phase_list = list(filter(lambda s: re.search('P\(.+\)',s, flags=re.IGNORECASE), l))
    if not phase_list == []:
        time_graph(df.filter(items=phase_list),ylabel="Phase difference",y_axis="rad",x_axis=timescale, bs=blackstyle, savefile=filename+"-phase.png")

    voltage_list = list(filter(lambda s: re.search('V\(.+\)',s, flags=re.IGNORECASE), l))
    if not voltage_list == []:
        time_graph(df.filter(items=voltage_list),ylabel="Voltage",y_axis="mV",x_axis=timescale, bs=blackstyle, savefile=filename+"-voltage.png")
        
    current_list = list(filter(lambda s: re.search('I\(.+\)',s, flags=re.IGNORECASE), l))
    if not current_list == []:
        time_graph(df.filter(items=current_list),ylabel="Current",y_axis="uA",x_axis=timescale, bs=blackstyle, savefile=filename+"-current.png")


def subplot(df : pd.DataFrame, timescale : str = "ps", blackstyle : bool = False):
    fig, axes = plt.subplots(nrows=3, ncols=1, sharey=True)
    l = df.columns
    phase_list = list(filter(lambda s: re.search('P\(.+\)',s, flags=re.IGNORECASE), l))
    if not phase_list == []:
        time_graph(df.filter(items=phase_list),ylabel="Phase difference",y_axis="rad",x_axis=timescale, bs=blackstyle)
        df.filter(items=phase_list).plot(ax=axes[0])

    voltage_list = list(filter(lambda s: re.search('V\(.+\)',s, flags=re.IGNORECASE), l))
    if not voltage_list == []:
        time_graph(df.filter(items=voltage_list),ylabel="Voltage",y_axis="mV",x_axis=timescale, bs=blackstyle)
        df.filter(items=voltage_list).plot(ax=axes[1])
        
    current_list = list(filter(lambda s: re.search('I\(.+\)',s, flags=re.IGNORECASE), l))
    if not current_list == []:
        time_graph(df.filter(items=current_list),ylabel="Current",y_axis="uA",x_axis=timescale, bs=blackstyle)
        df.filter(items=current_list).plot(ax=axes[2])

def margin_plot(margins : pd.DataFrame, critical_ele : str, filename = None, blackstyle : bool = False):
    # バーのcolor
    plot_color = '#01b8aa'

    if blackstyle:
        plot_color = "gray"


    df = margins.sort_index()
    index = df.index
    column0 = df['low(%)']
    column1 = df['high(%)']

    # --- biasのカラーを変更したリスト ---
    hatch_list = []
    for i in index:
        if i == critical_ele:
            hatch_list.append("///")
        else:
            hatch_list.append("0")
    # ------

    # 図のサイズ　sharey:グラフの軸の共有(y軸)
    fig, axes = plt.subplots(figsize=(10, len(index)/2), ncols=2, sharey=True)
    plt.subplots_adjust(wspace=0)
    fig.suptitle("Margins[%]", x=0.5, y=-0.15)
    # axes[0].set_ylabel("Elements", fontsize=20)
    # axes[1].set_xlabel("Margin[%]", fontsize=20)

    # 分割した 0 グラフ
    axes[0].barh(index, column0, align='center', color=plot_color, hatch = hatch_list)
    axes[0].set_xlim(-100, 0)
    # axes[0].grid(axis='y')


    # 分割した 1 グラフ
    axes[1].barh(index, column1, align='center', color=plot_color, hatch = hatch_list)
    axes[1].set_xlim(0, 100)
    axes[1].tick_params(axis='y', colors=plot_color)  # 1 グラフのメモリ軸の色をプロットの色と合わせて見れなくする
    # axes[1].grid(axis='y')


    if filename != None:
        fig.savefig(filename)
        plt.close(fig)