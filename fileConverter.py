import sys
import re
import os
import glob

tmpTag = "__tmp__"

def netlist2csv(input="si.inp", ofname="simdata", option=0) -> bool:
    """
    Convert str data, .inp or .txt file into a csv file.
    """
    if input.endswith(".inp") or input.endswith(".txt"):
        print("n2c: " + input + " -> " + ofname + ".csv")
        f = open(str(input), "r")
        data = f.read()
        f.close()
    else:
        print("n2c: this str -> " + ofname + ".csv")
        data = input
    data = re.sub(".+@.+", "<e-mail>", data)
    data = re.sub("\*\*+ +", "*", data)
    data = re.sub(
        ",", ",/", data
    )  # this "/" is useful for changing the csv file to a netlist(txt) file
    data = re.sub("\*\*+", "*", data)
    data = re.sub(r"  +", ",", data)
    data = re.sub("(^\w.+)", ",\\1", data, flags=re.MULTILINE)
    data = re.sub("{{(.+)}}", "{\\1}", data, flags=re.MULTILINE)

    if option == 0:
        ofname += ".csv"
        out = open(ofname, "w")
        out.write(data)
        out.close()
    if not option == 0:
        subckt_loc = re.search("\*top cell", data, flags=re.MULTILINE)
        data_subckt = data[: subckt_loc.start() - 1]
        data_topcell = data[subckt_loc.start() :]
        out = open(ofname + "_sub.csv", "w")
        out.write(data_subckt)
        out.close()
        out = open(ofname + "_top.csv", "w")
        out.write(data_topcell)
        out.close()
    return True


config_data_script = ""


def csv2netlist_str(fname: str, ref_fname="cktconfig.py", auto_del=False) -> str:
    """Convert a csv file(fname) into str(return).

    If the csv file has some words coverd with '{}', this function replaces numerical data referenced from a file(ref_name).
    """
    if not fname.endswith(".csv"):
        sys.exit(fname + " is not '.csv' file")
    f = open(fname, "r")
    data = f.read()
    f.close()
    data = re.sub("^,", "", data, flags=re.MULTILINE)
    data = re.sub(",,+", "", data, flags=re.MULTILINE)
    data = re.sub(",/", "/", data)
    data = re.sub(",", "\t\t\t", data)
    data = re.sub("/", ",", data)
    variable_number = 0
    variable = ""
    for m in re.finditer("\{(.+)\}", data):
        variable += "str(" + m.group(1) + "), "
        variable_number += 1
    if variable_number == 0:
        return data
    if not ref_fname.endswith(".py"):
        sys.exit(ref_fname + "is not '.py' file")
    ff = open(ref_fname, "r")
    config_data = ff.read()
    ff.close()
    f = open(os.getcwd() + "/config_data_tmp.py", "w")
    f.write(config_data)
    f.write('data = f"""\n' + data + '\n"""\n')
    f.write(
        'import os\nf = open(os.getcwd()+"/netlist_tmp.txt", "w")\nf.write(data)\nf.close()\n'
    )
    f.close()
    os.system("python3 " + os.getcwd() + "/config_data_tmp.py")
    f = open(os.getcwd() + "/netlist_tmp.txt", "r")
    data = f.read()
    f.close()
    if auto_del is True:
        os.remove(os.getcwd() + "/config_data_tmp.py")
        os.remove(os.getcwd() + "/netlist_tmp.txt")
    return data


def py2netlist(fname="cktconfig.py", auto_del=True, coment_out_convert=True) -> str:
    """
    Cange a valiant named 'netlist' in the .py file -> str.

    -fnmae: this fanction requires '.py' file for output
    -auto_del: delete dvi files which is generate from this function
    -coment_out_convert: this converts # -> * in netlist so you can use "ctrl + /" on your editor
    """
    if fname.endswith(".py") is False:
        print("this is not .py file")
        return "netlist fname error"
    ff = open(fname, "r")
    config_data = ff.read()
    ff.close()
    f = open(os.getcwd() + "/config_data_tmp.py", "w")
    f.write(config_data)
    f.write(
        '\nimport os\nf = open(os.getcwd()+"/netlist_tmp.txt", "w")\nf.write(netlist)\nf.close()\n'
    )
    f.close()
    os.system("python3 " + os.getcwd() + "/config_data_tmp.py")
    f = open(os.getcwd() + "/netlist_tmp.txt", "r")
    data = f.read()
    if coment_out_convert is True:
        data.replace("#", "*")
    f.close()
    if auto_del is True:
        os.remove(os.getcwd() + "/config_data_tmp.py")
        os.remove(os.getcwd() + "/netlist_tmp.txt")
    return data


def jsm2netlist(fname="si.jsm", ref_fname="cktconfig.py",margine_mode = False, auto_del=True) -> str:
    """Convert a jsm file(fname) into str(return).

    If the jsm file has some words coverd with '{}', this function replaces numerical data referenced from a file(ref_name).
    """
    tmp_pythonFilename = "/"+tmpTag+"config_data.py"
    tmp_textFilename = "/"+tmpTag+"netlist.jsm"
    if not fname.endswith(".jsm"):
        sys.exit(fname + " is not '.jsm' file")
    f = open(fname, "r")
    data = f.read()
    f.close()
    variable_number = 0
    variable = ""
    for m in re.finditer("\{(.+)\}", data):
        variable += "str(" + m.group(1) + "), "
        variable_number += 1
    if variable_number == 0:
        return data
    # else: 
    #     print(variable)
    if not ref_fname.endswith(".py"):
        sys.exit(ref_fname + "is not '.py' file")
    ff = open(ref_fname, "r")
    config_data = ff.read()
    ff.close()
    f = open(os.getcwd() + tmp_pythonFilename, "w")
    f.write(config_data)
    f.write('\ndata = f"""\\\n' + data + '\n"""\n')
    writecontent = (
        'import os\nf = open(os.getcwd()+"'
        + tmp_textFilename
        + '", "w")\nf.write(data)\nf.close()\n'
    )
    f.write(writecontent)
    f.close()
    os.system("python3 " + os.getcwd() + tmp_pythonFilename)
    f = open(os.getcwd() + tmp_textFilename, "r")
    data = f.read()
    f.close()
    if auto_del is True:
        tmpfileDelete()
    return data

def tmpfileDelete():
    for filename in glob.glob(tmpTag+'*'):
        if os.path.exists(filename):
            os.remove(filename)
# if __name__ == "__main__":
